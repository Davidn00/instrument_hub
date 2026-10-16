import numpy as np
from fastapi import APIRouter

from app.api.v1.schemas.analysis import (
    FftAnalysisRequest,
    FftAnalysisResponse,
)
from app.processing.spectral import fft_spectrum

router = APIRouter(
    prefix="/analysis",
)


@router.post(
    "/fft",
    response_model=FftAnalysisResponse,
)
async def analyze_fft(
    request: FftAnalysisRequest,
) -> FftAnalysisResponse:
    samples = np.asarray(
        request.samples,
        dtype=float,
    )

    # Para el cálculo FFT, eliminar la media ayuda a evitar
    # que el componente DC domine la gráfica de frecuencias.
    processed_samples = samples - np.mean(samples) if request.remove_mean else samples

    result = fft_spectrum(
        processed_samples,
        request.sampling_rate_hz,
    )

    # Excluimos la componente DC (frecuencia cero) al buscar
    # la frecuencia dominante de la señal.
    if result.frequencies.size > 1 and np.any(result.amplitudes[1:] > 0):
        dominant_index = 1 + int(np.argmax(result.amplitudes[1:]))
        dominant_frequency = float(result.frequencies[dominant_index])
    else:
        dominant_frequency = 0.0

    return FftAnalysisResponse(
        sample_count=int(samples.size),
        sampling_rate_hz=request.sampling_rate_hz,
        time_seconds=(np.arange(samples.size) / request.sampling_rate_hz).tolist(),
        signal_values=samples.tolist(),
        frequencies_hz=result.frequencies.tolist(),
        amplitudes=result.amplitudes.tolist(),
        dominant_frequency_hz=dominant_frequency,
        remove_mean=request.remove_mean,
    )
