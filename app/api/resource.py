from datetime import datetime
from typing import Any, List, Literal, Optional
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.core.constants import resource_type
from app.utils import upload_multiple_file
from app.deps.db import get_async_session
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen
from app.models.users import User
from app.models.farms import Farms
from app.models.trees import Trees
from app.models.fertilizers import Fertilizers
from app.models.products import Products
from app.models.resource import Resource
from app.schemas.resource import Resource as ResourceSchema

name = "resource"
router = APIRouter(prefix=f"/{name}s")


@router.post(
    "",
    name=f"{name}:create",
)
async def upload_file(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Create multiple resources
    """
    resources = await upload_multiple_file(session, files, user.id)
    return resources


@router.get(
    "/{resource_id}",
    name=f"{name}:one",
)
async def get_resource_by_id(
    resource_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get resource by id
    """
    resource: Optional[Resource] = await session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=404,
            detail="The resource not found."
        )
    return resource


@router.patch(
    "/items",
    name=f"{name}:update_of_item",
)
async def update_resource_of_item(
    deleted_resource_ids: List[uuid.UUID] = Query(None),
    files: Optional[List[UploadFile]] = File(None),
    item_id: uuid.UUID = Form(...),
    item_type: Literal[
        f"{resource_type.FARM}", f"{resource_type.FERTILIZER}",
        f"{resource_type.PRODUCT}", f"{resource_type.TREE}"
    ] = Form(...),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Update resource of item
    """
    resources = None
    if files:
        resources = await upload_multiple_file(session, files, user.id)
    if item_type == resource_type.FARM:
        item: Optional[Farms] = await session.get(Farms, item_id)
        if not item:
            raise HTTPException(400, "The farm not found.")
        await crud.farm.delete_resources(session, deleted_resource_ids, item.id, item_type)
        await crud.farm.add_resources(session, resources, item.id, item_type)
        resources = await crud.farm.get_resources(session, item.id, item_type)
        response = {**item.__dict__}
        response.update({"resources": resources})
    elif item_type == resource_type.TREE:
        item: Optional[Trees] = await session.get(Trees, item_id)
        if not item:
            raise HTTPException(400, "The tree not found.")
        await crud.tree.delete_resources(session, deleted_resource_ids, item.id, item_type)
        await crud.tree.add_resources(session, resources, item.id, item_type)
        resources = await crud.tree.get_resources(session, item.id, item_type)
        response = {**item.__dict__}
        response.update({"resources": resources})
    elif item_type == resource_type.FERTILIZER:
        item: Optional[Fertilizers] = await session.get(Fertilizers, item_id)
        if not item:
            raise HTTPException(400, "The fertilizer not found.")
        await crud.fertilizer.delete_resources(session, deleted_resource_ids, item.id, item_type)
        await crud.fertilizer.add_resources(session, resources, item.id, item_type)
        resources = await crud.fertilizer.get_resources(session, item.id, item_type)
        response = {**item.__dict__}
        response.update({"resources": resources})
    elif item_type == resource_type.PRODUCT:
        item: Optional[Fertilizers] = await session.get(Products, item_id)
        if not item:
            raise HTTPException(400, "The product not found.")
        await crud.product.delete_resources(session, deleted_resource_ids, item.id, item_type)
        await crud.product.add_resources(session, resources, item.id, item_type)
        resources = await crud.product.get_resources(session, item.id, item_type)
        response = {**item.__dict__}
        response.update({"resources": resources})
    return response


@router.delete(
    "/{resource_id}",
    name=f"{name}:delete",
)
async def delete_resource_by_id(
    resource_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Delete resource\n
    - deleted_at
    - updated_by
    """
    resource: Optional[Resource] = await session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=404,
            detail="The resource not found."
        )
    resource.deleted_at = datetime.utcnow()
    resource.updated_by = user.id
    session.add(resource)
    await session.commit()
    return "The resource deleted successfully!"