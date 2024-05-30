from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

class AirValue(BaseModel):
    pm25: int
    pm10: int
    esp_name: str

class AirValueWithTimestamp(BaseModel):
    pm25: int
    pm10: int
    esp_name: str
    timestamp: datetime

router = APIRouter()