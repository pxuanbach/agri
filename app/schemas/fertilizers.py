from datetime import datetime
from typing import Literal, Optional, List
from app.schemas.resource import Resource
import uuid
from pydantic import BaseModel


class FertilizerCreate(BaseModel):
    name: str
    description: Optional[str]
    manufacturer: str
    manufacture_date: Optional[datetime]
    compositions: Optional[str]
    type: Literal["Hữu cơ", "Vô cơ", "Vi sinh", "Khác"]


class FertilizerUpdate(FertilizerCreate):
    name: Optional[str]
    manufacturer: Optional[str]
    manufacture_date: Optional[datetime]
    type: Optional[Literal["Hữu cơ", "Vô cơ", "Vi sinh", "Khác"]]


class Fertilizer(FertilizerCreate):
    id: uuid.UUID
    code: str
    updated_by: uuid.UUID
    deleted_at: Optional[datetime]
    resources: Optional[List[Resource]] = []

    class Config:
        orm_mode = True