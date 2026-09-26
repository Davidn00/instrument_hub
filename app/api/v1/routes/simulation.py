from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.simulation import (
    DeviceAcquisitionRequest,
    DeviceAcquisitionResponse,
    DeviceMeasurementRequest,
    DeviceMeasurementResponse,
    GenerateSignalRequest,
    GenerateSignalResponse,
    SimulatedDeviceInfo,
)
from app.services.simulation import (
    SimulationService,
    UnknownSimulationDeviceError,
    UnsupportedAcquisitionError,
)

router = APIRouter(
    prefix="/simulation",
)


simulation_service = SimulationService()


@router.get(
    "/devices",
    response_model=list[SimulatedDeviceInfo],
)
async def list_simulated_devices() -> list[dict[str, str]]:
    return simulation_service.list_devices()


@router.post(
    "/signals",
    response_model=GenerateSignalResponse,
)
async def generate_signal(
    request: GenerateSignalRequest,
) -> GenerateSignalResponse:
    parameters = request.model_dump(exclude={"signal_type"})

    try:
        generated = simulation_service.generate_signal(
            signal_type=request.signal_type,
            parameters=parameters,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return GenerateSignalResponse(
        signal_type=generated.signal_type,
        samples=generated.samples.tolist(),
        sampling_rate=generated.sampling_rate,
        unit=generated.unit,
        metadata=generated.metadata,
    )


@router.post(
    "/devices/{device_type}/measurement",
    response_model=DeviceMeasurementResponse,
)
async def read_device_measurement(
    device_type: str,
    request: DeviceMeasurementRequest,
) -> DeviceMeasurementResponse:
    try:
        measurement = await simulation_service.read_measurement(
            device_type=device_type,
            device_id=request.device_id,
        )
    except UnknownSimulationDeviceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return DeviceMeasurementResponse(
        timestamp=measurement.timestamp.isoformat(),
        value=measurement.value,
        unit=measurement.unit,
        sensor_id=measurement.sensor_id,
        device_id=measurement.device_id,
        measurement_type=(measurement.measurement_type),
        metadata=measurement.metadata,
    )


@router.post(
    "/devices/{device_type}/acquire",
    response_model=DeviceAcquisitionResponse,
)
async def acquire_device_signal(
    device_type: str,
    request: DeviceAcquisitionRequest,
) -> DeviceAcquisitionResponse:
    try:
        signal = simulation_service.acquire_signal(
            device_type=device_type,
            device_id=request.device_id,
            duration=request.duration,
        )
    except UnknownSimulationDeviceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except UnsupportedAcquisitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DeviceAcquisitionResponse(
        device_id=request.device_id,
        channel=signal.channel,
        sampling_rate=signal.sampling_rate,
        unit=signal.unit,
        number_of_samples=signal.number_of_samples,
        duration=signal.duration,
        samples=signal.samples.tolist(),
        metadata=signal.metadata,
    )
