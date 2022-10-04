from typing import Any, Generic, List, Optional, TypeVar

from pydantic.generics import GenericModel
from pydantic.main import BaseModel

from app.schemas.users import User

T = TypeVar("T")

class ResponsePaginationReviewDashboard(BaseModel):
    page_total: int
    page_size: int
    page: int
    data: dict

class ResponsePaginationUsers(BaseModel):
    page_total: int
    page_size: int
    page: int
    data: List[User]


class ResponsePagination(BaseModel):
    page_total: int
    page_size: int
    page: int
    data: List[Any]


class ResponseGeneric(GenericModel):
    page_total: Optional[int]
    page_size: Optional[int]
    page: Optional[int]


class ResponseGenericPagination(ResponseGeneric, Generic[T]):
    data: Optional[List[T]] = None
