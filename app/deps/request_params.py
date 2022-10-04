from decimal import Decimal
import json
from typing import List, Literal, Optional
from urllib.parse import unquote
import uuid

from dateutil import parser
from fastapi import HTTPException, Query, Depends
from sqlalchemy import asc, desc
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.core.config import settings
from app.schemas.request_params import (
    RequestParams,
    RequestParamsProductHistory,
    RequestParamsUser,
    RequestParamsCommon,
    RequestParamsFertilizer,
    RequestParamsTree,
    RequestParamsProduct,
    RequestParamsTransferRequest
)


def parse_react_admin_params(model: DeclarativeMeta) -> RequestParams:
    """Parses sort and range parameters coming from a react-admin request"""

    def inner(
        sort_: Optional[str] = Query(
            None,
            alias="sort",
            description='Format: `["field_name", "direction"]`',
            example='["id", "ASC"]',
        ),
        range_: Optional[str] = Query(
            None,
            alias="range",
            description="Format: `[start, end]`",
            example="[0, 10]",
        ),
    ):
        skip, limit = 0, 10
        if range_:
            start, end = json.loads(range_)
            skip, limit = start, (end - start + 1)

        order_by = desc(model.id)
        if sort_:
            sort_column, sort_order = json.loads(sort_)
            if sort_order.lower() == "asc":
                direction = asc
            elif sort_order.lower() == "desc":
                direction = desc
            else:
                raise HTTPException(400, f"Invalid sort direction {sort_order}")
            try:
                order_by = direction(model.__table__.c[sort_column])
            except:
                raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParams(skip=skip, limit=limit, order_by=order_by)

    return inner


def parse_common_params(model: DeclarativeMeta) -> RequestParams:
    def inner(
        skip: Optional[int] = settings.PAGING_DEFAULT_SKIP,
        limit: Optional[int] = settings.PAGING_DEFAULT_LIMIT,
        order_by: Optional[str] = "id DESC",
    ):
        # _order_by = desc(model.id)
        sort_column, sort_order = order_by.split(" ")[0], order_by.split(" ")[1]
        if sort_order.lower() == "asc":
            direction = asc
        elif sort_order.lower() == "desc":
            direction = desc
        else:
            raise HTTPException(400, f"Invalid sort direction {sort_order}")
        try:
            order_by = direction(model.__table__.c[sort_column])
        except:
            raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParams(skip=skip, limit=limit, order_by=order_by)

    return inner


def parse_filter_search_params_users(model: DeclarativeMeta) -> RequestParamsUser:
    def inner(
        search: Optional[str] = Query(
            None, description="Search in email, name, address", example="string"
        ),
        skip: Optional[int] = settings.PAGING_DEFAULT_SKIP,
        limit: Optional[int] = settings.PAGING_DEFAULT_LIMIT,
        order_by: Optional[str] = "id DESC",
        email: Optional[str] = Query(
            None,
            description="Find user have email equal query value",
            example="",
        ),
        address: Optional[str] = Query(
            None,
            description="Find user have address equal query value",
            example="",
        ),
        name: Optional[str] = Query(
            None,
            description="Find user have full_name equal query value",
            example="",
        ),
        role_id: Optional[str] = Query(
            None,
            description="Find user have role_id equal query value",
            example="",
        ),
        is_deleted: Optional[bool] = Query(
            None, description="Find user have is_deleted equal query value", example=""
        ),
    ):
        if search:
            search = unquote(search)
            search = search.lower()
        if email:
            email = email.lower()
        if address:
            address = address.lower()
        if name:
            name = name.lower()
        sort_column, sort_order = order_by.split(" ")[0], order_by.split(" ")[1]
        if sort_order.lower() == "asc":
            direction = asc
        elif sort_order.lower() == "desc":
            direction = desc
        else:
            raise HTTPException(400, f"Invalid sort direction {sort_order}")
        try:
            order_by = direction(model.__table__.c[sort_column])
        except:
            raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParamsUser(
            search=search,
            skip=skip,
            limit=limit,
            order_by=order_by,
            email=email,
            name=name,
            role_id=role_id,
            address=address,
            is_deleted=is_deleted,
        )

    return inner


def parse_filter_search_params() -> RequestParamsCommon:
    def inner(
        search: Optional[str] = Query(
            None, description="unquote, lower case"
        ),
        updated_by: Optional[uuid.UUID] = Query(None, description="equal"),
    ):
        if search:
            search = unquote(search)
            search = search.lower()
        return RequestParamsCommon(
            search=search,
            updated_by=updated_by
        )

    return inner


def parse_filter_search_params_fertilizers() -> RequestParamsFertilizer:
    def inner(
        name: Optional[str] = Query(None, description="contains"),
        manufacturer: Optional[str] = Query(None, description="contains"),
        code: Optional[str] = Query(None, description="contains"),
        types: Optional[List[Literal["Hữu cơ", "Vô cơ", "Vi sinh", "Khác"]]] = Query(None, description="in"),
        request_params: RequestParamsCommon = Depends(parse_filter_search_params()),
    ):
        if name:
            name = name.lower()
        if manufacturer:
            manufacturer = manufacturer.lower()
        if code:
            code = code.lower()
        return RequestParamsFertilizer(
            search=request_params.search,
            name=name,
            manufacturer=manufacturer,
            code=code,
            updated_by=request_params.updated_by,
            types=types
        )
    
    return inner


def parse_filter_search_params_trees() -> RequestParamsTree:
    def inner(
        name: Optional[str] = Query(None, description="contains"),
        code: Optional[str] = Query(None, description="contains"),
        request_params: RequestParamsCommon = Depends(parse_filter_search_params()),
    ):
        if name:
            name = name.lower()
        if code:
            code = code.lower()
        return RequestParamsTree(
            search=request_params.search,
            name=name,
            code=code,
            updated_by=request_params.updated_by,
        )
    
    return inner

def parse_filter_search_params_product(model: DeclarativeMeta) -> RequestParamsProduct:
    def inner(
        search: Optional[str] = Query(
            None, description="Search in name, code", example="string"
        ),
        skip: Optional[int] = settings.PAGING_DEFAULT_SKIP,
        limit: Optional[int] = settings.PAGING_DEFAULT_LIMIT,
        order_by: Optional[str] = "id DESC",
        name: Optional[str] = Query(
            None,
            description="Find product have name equal query value",
            example="",
        ),
        code: Optional[str] = Query(
            None,
            description="Find product have code equal query value",
            example="",
        ),
        range_price: Optional[Decimal] = Query(
            None,
            description="Find product have price value in range",
            example="",
        ),    
        product_status: Optional[str] = Query(
            None,
            description="Find product have status equal query value (pending/failed/accepted)",
            example="",
        ),
        farm_id: Optional[uuid.UUID] = Query(
            None,
            description="Find product have farm_id equal query value",
            example="",
        ),
        user_id: Optional[uuid.UUID] = Query(
            None,
            description="Find product have user_id equal query value",
            example="",
        ),
        is_deleted: Optional[bool] = Query(
            None, description="Find product have is_deleted equal query value", example=""
        ),
    ):
        if search:
            search = unquote(search)
            search = search.lower()
        if product_status:
            product_status = product_status.lower()
        if name:
            name = name.lower()
        sort_column, sort_order = order_by.split(" ")[0], order_by.split(" ")[1]
        if sort_order.lower() == "asc":
            direction = asc
        elif sort_order.lower() == "desc":
            direction = desc
        else:
            raise HTTPException(400, f"Invalid sort direction {sort_order}")
        try:
            order_by = direction(model.__table__.c[sort_column])
        except:
            raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParamsProduct(
            search=search,
            skip=skip,
            limit=limit,
            order_by=order_by,
            name=name,
            farm_id=farm_id,
            user_id=user_id,
            product_status=product_status,
            code=code,
            range_price=range_price,
            is_deleted=is_deleted,
        )

    return inner

def parse_filter_search_params_transfer_request(model: DeclarativeMeta) -> RequestParamsTransferRequest:
    def inner(
        skip: Optional[int] = settings.PAGING_DEFAULT_SKIP,
        limit: Optional[int] = settings.PAGING_DEFAULT_LIMIT,
        order_by: Optional[str] = "id DESC",
        product_id: Optional[uuid.UUID] = Query(
            None,
            description="Find user have product_id equal query value",
            example="",
        ),
        transfer_to_user_id: Optional[uuid.UUID] = Query(
            None,
            description="Find user have transfer_to_user_id equal query value",
            example="",
        ),
        transfer_from_user_id: Optional[uuid.UUID] = Query(
            None,
            description="Find user have transfer_from_user_id equal query value",
            example="",
        ),
        transfer_status: Optional[str] = Query(
            None,
            description="Find user have transfer status equal query value (pending/failed/accepted)",
            example="",
        ),
        is_deleted: Optional[bool] = Query(
            None, description="Find user have is_deleted equal query value", example=""
        ),
    ):
        if transfer_status:
            transfer_status = transfer_status.lower()
        sort_column, sort_order = order_by.split(" ")[0], order_by.split(" ")[1]
        if sort_order.lower() == "asc":
            direction = asc
        elif sort_order.lower() == "desc":
            direction = desc
        else:
            raise HTTPException(400, f"Invalid sort direction {sort_order}")
        try:
            order_by = direction(model.__table__.c[sort_column])
        except:
            raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParamsTransferRequest(
            skip=skip,
            limit=limit,
            order_by=order_by,
            product_id=product_id,
            transfer_to_user_id=transfer_to_user_id,
            transfer_from_user_id=transfer_from_user_id,
            transfer_status=transfer_status,
            is_deleted=is_deleted,
        )

    return inner


def parse_filter_search_params_product_history(model: DeclarativeMeta) -> RequestParamsProductHistory:
    def inner(
        skip: Optional[int] = settings.PAGING_DEFAULT_SKIP,
        limit: Optional[int] = settings.PAGING_DEFAULT_LIMIT,
        order_by: Optional[str] = "id DESC",
        product_id: Optional[uuid.UUID] = Query(
            None,
            description="Find product history have product_id equal query value",
            example="",
        ),
    ):
        sort_column, sort_order = order_by.split(" ")[0], order_by.split(" ")[1]
        if sort_order.lower() == "asc":
            direction = asc
        elif sort_order.lower() == "desc":
            direction = desc
        else:
            raise HTTPException(400, f"Invalid sort direction {sort_order}")
        try:
            order_by = direction(model.__table__.c[sort_column])
        except:
            raise HTTPException(400, f"Invalid sort field {sort_column}")

        return RequestParamsProductHistory(
            skip=skip,
            limit=limit,
            order_by=order_by,
            product_id=product_id
        )

    return inner