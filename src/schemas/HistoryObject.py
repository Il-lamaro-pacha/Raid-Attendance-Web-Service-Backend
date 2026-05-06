from pydantic import BaseModel
from datetime import datetime

class HistoryObject(BaseModel):
    date: datetime
    name: str