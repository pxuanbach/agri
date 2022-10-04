from typing import Optional
import uuid
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description:  Optional[str]


class CategoryUpdate(CategoryCreate):
    pass


class Category(CategoryCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True
