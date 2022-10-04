from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from app.schemas.resource import Resource
import uuid
from pydantic import BaseModel



class ProductCreate(BaseModel):
    name: str
    farm_id: Optional[uuid.UUID]
    description:  Optional[str]
    price_in_retail: Optional[Decimal]

class ProductUpdate(ProductCreate):
    pass


class Product(ProductCreate):
    id: uuid.UUID
    code: str
    deleted_at: Optional[datetime]
    updated_by: uuid.UUID
    resources: Optional[List[Resource]] = []

    class Config:
        orm_mode = True
