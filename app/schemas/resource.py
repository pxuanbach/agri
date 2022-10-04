from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel


class Resource(BaseModel):
    id: uuid.UUID
    name: str
    file_path: str
    file_type: str
    file_size:  Optional[Decimal]
    updated_by: uuid.UUID

    class Config:
        orm_mode = True
