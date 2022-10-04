from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel

from app.schemas.resource import Resource


class TreeCreate(BaseModel):
    name: str
    description: Optional[str]


class TreeUpdate(TreeCreate):
    name: Optional[str]


class Tree(TreeCreate):
    id: uuid.UUID
    code: str
    deleted_at: Optional[datetime]
    updated_by: uuid.UUID
    resources: Optional[List[Resource]] = []

    class Config:
        orm_mode = True