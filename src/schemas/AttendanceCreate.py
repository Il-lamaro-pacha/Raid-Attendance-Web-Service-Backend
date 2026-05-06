from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from src.schemas.WowClass import WowClass

class AttendanceCreate(BaseModel):
    item_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=12)
    char_class: WowClass
    date: datetime

    model_config = {
        "str_strip_whitespace": True
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.isalpha():
            raise ValueError("Player name must contain only letters")
        return v