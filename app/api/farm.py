from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.deps.db import get_async_session
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen
from app import crud
from app.utils import upload_multiple_file
from app.models.users import User
from app.models.farms import Farms
from app.schemas.farms import Farm as FarmSchema
from app.schemas.farms import FarmCreate, FarmUpdate
from app.core.constants import role_key, resource_type

# Awards
name="farm"
router = APIRouter(prefix=f"/{name}")

@router.get(
    "",
    name=f"{name}:get-farm",
)
async def get_farm(
    farm_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    get farm by id
    """
    farm = await crud.farm.get_farm_by_id(session, farm_id)
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )
    response = {**farm}
    response.update({"resources": await crud.farm.get_resources(session, farm_id, resource_type.FARM)})
    return response

@router.get(
    "/list",
    name=f"{name}:list-farm",
)
async def list_farm(
    get_all: bool,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    get farm by id
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if not get_all:
        if current_user_role.key != role_key.ADMIN and current_user_role.key != role_key.OWNER:
            raise HTTPException(
                status_code=404,
                detail="User do not have permission.",
            )
        farms = await crud.farm.get_farms_by_user_id(session, user.id)
    else:
        if current_user_role.key != role_key.ADMIN:
            raise HTTPException(
                status_code=404,
                detail="User do not have permission.",
            )
        farms = await crud.farm.get_all_farms(session)

    responses = []
    for farm in farms:
        response = {**farm}
        response.update({"resources": await crud.farm.get_resources(session, farm.Farms.id, resource_type.FARM)})
        responses.append(response)
    return responses

@router.post(
    "",
    name=f"{name}:create-farm",
)
async def create_farm(
    name: str ,
    area: Optional[Decimal] = None,
    description: Optional[str] = None,
    files: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
):
    """
    Create farm
    """
    farm_in = FarmCreate(
        name=name,
        area=area,
        description=description,
    )
    farm = await crud.farm.create(
        session, farm_in, user.id
    )
    response = FarmSchema.from_orm(farm)
    if files:
        resources = await upload_multiple_file(session, files, updated_by=user.id)
        await crud.farm.add_resources(session, resources, farm.id, resource_type.FARM)
        response.resources = resources
    return response

@router.patch(
    "",
    name=f"{name}:patch-farm",
)
async def create_farm(
    farm_id: uuid.UUID,
    obj_in: FarmUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
):
    """
    Update farm
    """
    farm = await session.get(Farms, farm_id)
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Sorry, the farm you looking for could not be found. Maybe the farm is deactivated or deleted.",
        )
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    await crud.farm.update_farm(session, farm, user.id)
    return farm

@router.patch(
    "/fertilizer",
    name=f"{name}:patch-farm-fertilizer",
)
async def patch_farm_fertilizer(
    farm_id: uuid.UUID,
    fertilizers: List[uuid.UUID],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
):
    """
    Update farm fertilizer
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN and current_user_role.key != role_key.OWNER:
        raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )
    farm_fertilizers = await crud.farm.update_farm_fertilizer(session, farm_id, fertilizers, user.id)

    return farm_fertilizers

@router.patch(
    "/tree",
    name=f"{name}:patch-farm-tree",
)
async def patch_tree(
    farm_id: uuid.UUID,
    trees: List[uuid.UUID],
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
):
    """
    Update farm tree
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN and current_user_role.key != role_key.OWNER:
        raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )
    farm_trees = await crud.farm.update_farm_tree(session, farm_id, trees, user.id)

    return farm_trees

@router.delete(
    "",
    name=f"{name}:delete-farm",
)
async def delete_farm(
    farm_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
):
    """
    Delete farm
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    farm = await crud.farm.get_only_farm_by_id(session, farm_id)
    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        if current_user_role.key != role_key.OWNER:
            raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )
        if farm.user_id != user.id:
            raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )    

    farm_trees = await crud.farm.delete_farm_relationship(session, farm_id, user.id)
    farm.deleted_at = datetime.utcnow()
    session.add(farm)
    await session.commit()

    return farm_trees