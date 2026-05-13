from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


@router.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok")
