from pydantic import BaseModel


class UserContext(BaseModel):
    username: str
    server: str
    guild_id: str
    email: str
