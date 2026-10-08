from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.storage.db import get_db

router = APIRouter(
    prefix="/health",
)


@router.get("")
async def health_check() -> dict[str, str]:
    settings = get_settings()

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))

        result = await session.execute(
            text(
                """
                SELECT extname
                FROM pg_extension
                WHERE extname = 'timescaledb'
                """
            )
        )

        timescale = result.scalar_one_or_none()

        if timescale is None:
            raise RuntimeError("TimescaleDB extension is not installed.")

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database is not ready: {exc}",
        ) from exc

    return {
        "status": "ready",
        "database": "postgresql",
        "timescaledb": "enabled",
    }
