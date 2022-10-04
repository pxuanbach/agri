from typing import Optional
import uuid
from pydantic import BaseModel


class RoleCreate(BaseModel):
    key: str
    description:  Optional[str]


class RoleUpdate(RoleCreate):
    pass


class Role(RoleCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True
