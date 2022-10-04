from decimal import Decimal
from typing import List, Literal, Optional, Any
import uuid
from pydantic import BaseModel


class RequestParams(BaseModel):
    skip: int
    limit: int
    order_by: Any

class RequestParamsUser(RequestParams):
    search: Optional[str]
    name: Optional[str]
    email: Optional[str]
    address: Optional[str]
    role_id: Optional[uuid.UUID]
    is_deleted: Optional[bool]


class RequestParamsCommon(BaseModel):
    search: Optional[str] = None
    updated_by: Optional[uuid.UUID] = None

class RequestParamsFertilizer(RequestParamsCommon):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    code: Optional[str] = None
    types: Optional[List[Literal["Hữu cơ", "Vô cơ", "Vi sinh", "Khác"]]] = None


class RequestParamsTree(RequestParamsCommon):
    name: Optional[str] = None
    code: Optional[str] = None

class RequestParamsProduct(RequestParams):
    search: Optional[str]
    name: Optional[str]
    code: Optional[str]
    range_price: Optional[Decimal]
    product_status: Optional[str]
    farm_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]
    is_deleted: Optional[bool]

class RequestParamsTransferRequest(RequestParams):
    product_id: Optional[uuid.UUID]
    transfer_to_user_id: Optional[uuid.UUID]
    transfer_from_user_id: Optional[uuid.UUID]
    transfer_status: Optional[str]
    is_deleted: Optional[bool]

class RequestParamsProductHistory(RequestParams):
    product_id: Optional[uuid.UUID]