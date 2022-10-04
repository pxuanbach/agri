from decimal import Decimal
import uuid
from datetime import datetime
from typing import List, Optional
from app.schemas.resource import Resource
from pydantic import BaseModel


class FarmCreate(BaseModel):
    name: str
    area: Optional[Decimal]
    description: Optional[str]

class FarmUpdate(FarmCreate):
    pass


class Farm(FarmCreate):
    id: uuid.UUID
    deleted_at: Optional[datetime]
    updated_by: uuid.UUID
    resources: Optional[List[Resource]] = []
    
    class Config:
        orm_mode = True
