from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel


class ItemResource(BaseModel):
    id: uuid.UUID
    item_type: str
    item_id: uuid.UUID
    resource_id: uuid.UUID

    class Config:
        orm_mode = True