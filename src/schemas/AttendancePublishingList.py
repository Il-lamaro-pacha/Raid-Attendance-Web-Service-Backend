from pydantic import BaseModel
from typing import List
from src.schemas.AttendanceResponse import AttendanceResponse

class AttendancePublishingList(BaseModel):
    attendance_list: List[AttendanceResponse]