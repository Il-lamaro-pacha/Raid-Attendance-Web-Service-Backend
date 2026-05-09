from pydantic import BaseModel

class RegistrationUserCreate(BaseModel):
    email: str
    guild_id: str
    server: str
    username: str