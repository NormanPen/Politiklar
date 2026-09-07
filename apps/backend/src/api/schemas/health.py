"""Health check response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str = Field(..., description="Overall health status: 'healthy' or 'degraded'")
    database: str = Field(..., description="Database connection status: 'connected' or 'disconnected'")
    version: str = Field(..., description="API version string")
    timestamp: datetime = Field(..., description="Timestamp of the health check")
