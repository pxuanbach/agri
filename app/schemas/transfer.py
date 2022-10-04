from typing import Optional
import uuid
from pydantic import BaseModel


class TransferStatusCreate(BaseModel):
    name: str
    description:  Optional[str]


class TransferStatusUpdate(TransferStatusCreate):
    pass


class TransferStatus(TransferStatusCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True


class TransferRequestCreate(BaseModel):
    product_id: uuid.UUID
    transfer_to_user_id: uuid.UUID
    transfer_from_user_id: uuid.UUID
    description: Optional[str]


class TransferRequestUpdate(TransferRequestCreate):
    pass

class TransferRequest(TransferRequestCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True


class ProductHistoryCreate(BaseModel):
    product_id: uuid.UUID
    transfer_from_user_id: uuid.UUID
    transfer_to_user_id: uuid.UUID


class ProductHistoryUpdate(ProductHistoryCreate):
    pass


class ProductHistory(ProductHistoryCreate):
    id: uuid.UUID

    class Config:
        orm_mode = True