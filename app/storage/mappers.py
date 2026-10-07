from app.models.measurement import Measurement
from app.models.spectrum import Spectrum
from app.storage.models import MeasurementRecord, SpectrumRecord


def measurement_to_record(
    measurement: Measurement,
) -> MeasurementRecord:
    return MeasurementRecord(
        timestamp=measurement.timestamp,
        device_id=measurement.device_id,
        channel=measurement.channel,
        value=measurement.value,
        unit=measurement.unit,
        quality=measurement.quality,
        metadata_=dict(measurement.metadata),
    )


def record_to_measurement(
    record: MeasurementRecord,
) -> Measurement:
    return Measurement(
        timestamp=record.timestamp,
        device_id=record.device_id,
        channel=record.channel,
        value=record.value,
        unit=record.unit,
        quality=record.quality,
        metadata=dict(record.metadata_),
    )


def spectrum_to_record(
    spectrum: Spectrum,
) -> SpectrumRecord:
    return SpectrumRecord(
        timestamp=spectrum.timestamp,
        device_id=spectrum.device_id,
        wavelength=spectrum.wavelength.tolist(),
        intensity=spectrum.intensity.tolist(),
        wavelength_unit=spectrum.wavelength_unit,
        intensity_unit=spectrum.intensity_unit,
        metadata_=dict(spectrum.metadata),
    )


def record_to_spectrum(
    record: SpectrumRecord,
) -> Spectrum:
    import numpy as np

    return Spectrum(
        timestamp=record.timestamp,
        device_id=record.device_id,
        wavelength=np.asarray(record.wavelength, dtype=float),
        intensity=np.asarray(record.intensity, dtype=float),
        wavelength_unit=record.wavelength_unit,
        intensity_unit=record.intensity_unit,
        metadata=dict(record.metadata_),
    )
