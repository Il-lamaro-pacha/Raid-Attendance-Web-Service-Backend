from pydantic import BaseModel
from typing import List

from src.schemas.RollbackItem import RollbackItem

class ListRollbackItem(BaseModel):
    rollback : List[RollbackItem]