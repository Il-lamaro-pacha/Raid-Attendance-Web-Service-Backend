from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from src.schemas.WowClass import WowClass

class AttendancePreviewResponse(BaseModel):
    current_item: str | None = Field(..., min_length=1, max_length=100) 
    current_item_id: int | None = Field(..., gt=0)
    current_score: int | None = Field(default=1, ge=0)
    next_item: str | None = Field(..., min_length=1, max_length=100)
    next_item_id: int | None = Field(..., gt=0)
    next_score: int | None = Field(default=1, ge=0)
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