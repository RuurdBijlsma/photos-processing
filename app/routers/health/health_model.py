from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str


async def check_health() -> HealthStatus:
    return HealthStatus(status="ok")
