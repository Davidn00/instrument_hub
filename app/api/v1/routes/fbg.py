from datetime import UTC, datetime
from typing import Any

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.fbg import (
    FBGAnalysisRequest,
    FBGAnalysisResponse,
    FBGPeakResponse,
    FBGTrackingPointResponse,
)
from app.api.v1.schemas.storage import SpectrumResponse
from app.models.spectrum import Spectrum
from app.processing.fbg import (
    detect_bragg_peak,
    detect_bragg_peaks,
    track_bragg_wavelength,
)
from app.storage.db import get_db
from app.storage.repositories import SpectrumRepository

router = APIRouter(prefix="/fbg", tags=["FBG Analysis"])


def _utc(value: datetime) -> datetime:
    """Normalize a datetime for timestamp comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _spectrum_response(spectrum: Spectrum) -> SpectrumResponse:
    return SpectrumResponse(
        timestamp=spectrum.timestamp,
        device_id=spectrum.device_id,
        wavelength=spectrum.wavelength.tolist(),
        intensity=spectrum.intensity.tolist(),
        wavelength_unit=spectrum.wavelength_unit,
        intensity_unit=spectrum.intensity_unit,
        metadata=spectrum.metadata,
    )


@router.post(
    "/analyze",
    response_model=FBGAnalysisResponse,
)
async def analyze_fbg(
    request: FBGAnalysisRequest,
    session: AsyncSession = Depends(get_db),
) -> FBGAnalysisResponse:
    repository = SpectrumRepository(session)

    stored_spectra = await repository.list(
        device_id=request.device_id,
        limit=request.history_limit,
        offset=0,
    )

    if not stored_spectra:
        raise HTTPException(
            status_code=404,
            detail=(f"No stored spectra were found for device '{request.device_id}'."),
        )

    # The repository returns newest-first. Tracking needs chronological order.
    spectra = sorted(
        stored_spectra,
        key=lambda item: _utc(item.timestamp),
    )

    selected_spectrum = spectra[-1]

    if request.spectrum_timestamp is not None:
        requested_timestamp = _utc(request.spectrum_timestamp)

        matching_spectrum = next(
            (item for item in spectra if _utc(item.timestamp) == requested_timestamp),
            None,
        )

        if matching_spectrum is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "The selected spectrum was not found in the "
                    "requested device history. Increase history_limit "
                    "or select a spectrum returned by GET /spectra."
                ),
            )

        selected_spectrum = matching_spectrum

    if request.noise_reduction:
        if (
            request.noise_window_length % 2 == 0
            or request.noise_window_length <= request.noise_polyorder
        ):
            raise HTTPException(
                status_code=422,
                detail=(
                    "noise_window_length must be odd and greater than noise_polyorder."
                ),
            )

        if request.noise_window_length > selected_spectrum.number_of_pixels:
            raise HTTPException(
                status_code=422,
                detail=(
                    "The selected spectrum contains fewer samples "
                    "than noise_window_length."
                ),
            )

    detection_options: dict[str, Any] = {
        "prominence": request.prominence,
        "height": request.height,
        "distance": request.distance,
        "width": request.width,
        "noise_reduction": request.noise_reduction,
        "noise_window_length": request.noise_window_length,
        "noise_polyorder": request.noise_polyorder,
        "refinement": request.refinement,
    }

    try:
        detection = detect_bragg_peaks(
            selected_spectrum,
            **detection_options,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    # Select the strongest detected peak, if any.
    strongest_peak = (
        max(
            detection.peaks,
            key=lambda peak: (
                peak.prominence if peak.prominence is not None else peak.intensity
            ),
        )
        if detection.peaks
        else None
    )

    filtered = np.asarray(
        detection.filtered_intensity,
        dtype=float,
    )
    rms_value = float(np.sqrt(np.mean(np.square(filtered))))

    # Build tracking from the spectra that contain a valid Bragg peak.
    # A spectrum without a detected peak must not invalidate the whole history.
    trackable_spectra: list[Spectrum] = []

    for candidate in spectra:
        if request.noise_reduction and (
            request.noise_window_length > candidate.number_of_pixels
        ):
            continue

        try:
            detect_bragg_peak(
                candidate,
                **detection_options,
            )
        except ValueError:
            continue

        trackable_spectra.append(candidate)

    tracking_points: list[FBGTrackingPointResponse] = []
    reference_wavelength: float | None = request.reference_wavelength_nm

    if trackable_spectra:
        try:
            tracking = track_bragg_wavelength(
                trackable_spectra,
                reference_wavelength_nm=reference_wavelength,
                **detection_options,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Unable to track Bragg wavelength: {exc}",
            ) from exc

        reference_wavelength = tracking.reference_wavelength_nm
        tracking_points = [
            FBGTrackingPointResponse(
                timestamp=point.timestamp,
                wavelength_nm=point.wavelength_nm,
                delta_wavelength_nm=point.delta_wavelength_nm,
                peak_intensity=point.peak_intensity,
            )
            for point in tracking.points
        ]
    elif reference_wavelength is None and strongest_peak is not None:
        reference_wavelength = strongest_peak.wavelength_nm

    return FBGAnalysisResponse(
        device_id=request.device_id,
        spectrum=_spectrum_response(selected_spectrum),
        filtered_intensity=filtered.tolist(),
        peaks=[
            FBGPeakResponse(
                index=peak.index,
                wavelength_nm=peak.wavelength_nm,
                intensity=peak.intensity,
                prominence=peak.prominence,
                width_nm=peak.width_nm,
            )
            for peak in detection.peaks
        ],
        peak_wavelength_nm=(
            strongest_peak.wavelength_nm if strongest_peak is not None else None
        ),
        peak_intensity=(
            strongest_peak.intensity if strongest_peak is not None else None
        ),
        rms=rms_value,
        reference_wavelength_nm=reference_wavelength,
        tracking_points=tracking_points,
        analyzed_spectra_count=len(trackable_spectra),
        noise_reduction=request.noise_reduction,
        noise_window_length=request.noise_window_length,
        noise_polyorder=request.noise_polyorder,
        prominence=request.prominence,
        refinement=request.refinement,
    )
