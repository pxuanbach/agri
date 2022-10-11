from decimal import Decimal
import math
from typing import Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product_history import ProductHistory
from app.schemas.request_params import RequestParamsProduct, RequestParamsProductHistory
from app.deps.request_params import parse_filter_search_params_product, parse_filter_search_params_product_history
from app import crud
from app.utils import upload_multiple_file
from app.deps.db import get_async_session
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen, resource_type
from app.models.users import User
from app.models.products import Products
from app.schemas.products import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate
)
from app.schemas.responses import ResponsePagination

name = "product"
router = APIRouter(prefix=f"/{name}s")


@router.get(
    "",
    name=f"{name}:list",
)
async def get_list_products(
    request_params: RequestParamsProduct = Depends(
        parse_filter_search_params_product(Products)
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all))
) -> Any:
    """
    Get list products
    """
    total = await crud.product.total_products(session, user.id, request_params)
    products = await crud.product.list_products(session, user.id, request_params)
    responses = []
    for product in products:
        response = {**product}
        response.update({"resources": await crud.product.get_resources(session, product.Products.id, resource_type.PRODUCT)})
        responses.append(response)

    if not responses:
        page_total = 1
    else:
        page_total = math.ceil(total/ request_params.limit)

    return ResponsePagination(
        page_total=page_total,
        page_size=request_params.limit,
        page=request_params.skip / request_params.limit + 1,
        data=responses,
    )

@router.get(
    "/history",
    name=f"{name}:history-list",
)
async def get_list_products_history(
    request_params: RequestParamsProductHistory = Depends(
        parse_filter_search_params_product_history(ProductHistory)
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all))
) -> Any:
    """
    Get list products
    """
    total = await crud.product_history.total_product_histories_by_product(session, request_params)
    histories = await crud.product_history.list_product_histories_by_product(session, request_params)

    responses = []
    for history in histories:
        response = {**history}
        if history.buyer_created_by is not None:
            response.update({"buyer_parent": await crud.user.get_user_basic_info_by_id(session, history.buyer_created_by)})
        else: 
            response.update({"buyer_parent": None})
        if history.seller_created_by is not None:
            response.update({"seller_parent": await crud.user.get_user_basic_info_by_id(session, history.seller_created_by)})
        else: 
            response.update({"seller_parent": None})

        responses.append(response)
        
    if not responses:
        page_total = 1
    else:
        page_total = math.ceil(total/ request_params.limit)

    return ResponsePagination(
        page_total=page_total,
        page_size=request_params.limit,
        page=request_params.skip / request_params.limit + 1,
        data=responses,
    )

@router.post(
    "",
    name=f"{name}:create",
    status_code=201
)
async def create_product(
    name: str,
    farm_id: Optional[uuid.UUID] = None,
    description:  Optional[str] = None,
    price_in_retail: Optional[Decimal] = None,
    files: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner))
) -> Any:
    """
    Create a product
    """
    product_in = ProductCreate(
        name=name,
        farm_id=farm_id,
        description=description,
        price_in_retail=price_in_retail
    )
    product = await crud.product.create(
        session, product_in, updated_by=user.id
    )
    response = ProductSchema.from_orm(product)
    if files:
        resources = await upload_multiple_file(session, files, updated_by=user.id)
        await crud.product.add_resources(session, resources, product.id, resource_type.PRODUCT)
        response.resources = resources
    return response


@router.get(
    "/{product_id}",
    name=f"{name}:one",
)
async def get_product_by_id(
    product_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get product by id
    """
    product = await crud.product.get_product_by_id(session, user.id, product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="The product not found."
        )
    response = {**product}
    response.update({"resources": await crud.product.get_resources(session, product_id, resource_type.PRODUCT)})
    return response


@router.patch(
    "/{product_id}",
    name=f"{name}:update",
)
async def update_product_by_id(
    product_id: uuid.UUID,
    product_in: ProductUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Update product by id
    - updated_by
    """
    product = await crud.product.get(session, product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="The product not found."
        )
    product = await crud.product.update(
        session, product, product_in, updated_by=user.id
    )
    response = ProductSchema.from_orm(product)
    return response


@router.delete(
    "/{product_id}",
    name=f"{name}:delete",
)
async def delete_product_by_id(
    product_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Delete product by id
    - updated_by
    - deleted_at
    """
    product = await crud.product.get(session, product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="The product not found."
        )
    await crud.product.delete(session, product, updated_by=user.id)
    return "The product deleted successfully!"