from pydantic import BaseModel


class PlayerAttendanceResponse(BaseModel):
    player: str
    item: str
    item_id: int
    score: int

