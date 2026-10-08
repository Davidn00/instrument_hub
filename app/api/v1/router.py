from fastapi import APIRouter

from app.api.v1.routes.acquisition import (
    router as acquisition_router,
)
from app.api.v1.routes.devices import (
    router as devices_router,
)
from app.api.v1.routes.experiments import (
    router as experiments_router,
)
from app.api.v1.routes.health import (
    router as health_router,
)
from app.api.v1.routes.measurements import (
    router as measurements_router,
)
from app.api.v1.routes.simulation import (
    router as simulation_router,
)
from app.api.v1.routes.spectra import (
    router as spectra_router,
)
from app.api.v1.routes.websocket import (
    router as websocket_router,
)

api_router = APIRouter()


api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    simulation_router,
    tags=["Simulation"],
)

api_router.include_router(
    devices_router,
    tags=["Devices"],
)

api_router.include_router(
    acquisition_router,
    tags=["Acquisition"],
)

api_router.include_router(
    measurements_router,
    tags=["Measurements"],
)

api_router.include_router(
    spectra_router,
    tags=["Spectra"],
)

api_router.include_router(
    experiments_router,
    tags=["Experiments"],
)

api_router.include_router(
    websocket_router,
    tags=["WebSocket"],
)
