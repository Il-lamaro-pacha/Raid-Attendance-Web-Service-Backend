
from src.schemas.AttendanceCreate import AttendanceCreate
from pydantic import BaseModel
from typing import List

class AttendanceCreateRequest(BaseModel):
    attendance_list: List[AttendanceCreate]