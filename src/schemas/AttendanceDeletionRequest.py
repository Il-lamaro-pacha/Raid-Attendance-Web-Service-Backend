from pydantic import BaseModel
from typing import List

class AttendanceDeletionRequest(BaseModel):
    player_names: List[str]