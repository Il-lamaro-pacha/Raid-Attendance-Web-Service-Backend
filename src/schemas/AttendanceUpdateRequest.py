from pydantic import BaseModel
from src.schemas.AttendanceResponse import AttendanceResponse
from typing import List

class AttendanceUpdateRequest(BaseModel):
    updates: List[AttendanceResponse]