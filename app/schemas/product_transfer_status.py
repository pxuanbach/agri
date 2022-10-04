from typing import Optional
import uuid
from pydantic import BaseModel


class ProductTransferStatusCreate(BaseModel):
    product_id: Optional[uuid.UUID]
    transfer_status: Optional[str]


class ProductTransferStatusUpdate(ProductTransferStatusCreate):
    pass


class ProductTransferStatus(ProductTransferStatusCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True