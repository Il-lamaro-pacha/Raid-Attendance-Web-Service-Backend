
from src.schemas.AttendancePreview import AttendancePreview
from pydantic import BaseModel
from typing import List

class AttendancePreviewRequest(BaseModel):
    newAttendances: List[AttendancePreview]