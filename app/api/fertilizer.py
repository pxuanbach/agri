import uuid
from datetime import datetime
from typing import List, Optional, Any, Literal
import uuid
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.utils import upload_multiple_file
from app.deps.db import get_async_session
from app.deps.request_params import parse_filter_search_params_fertilizers
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen, resource_type
from app.models.users import User
from app.models.fertilizers import Fertilizers
from app.schemas.request_params import RequestParamsFertilizer
from app.schemas.fertilizers import (
    Fertilizer as FertilizerSchema,
    FertilizerCreate,
    FertilizerUpdate
)

name = "fertilizer"
router = APIRouter(prefix=f"/{name}s")


@router.get(
    "",
    name=f"{name}:list",
)
async def get_list_fertilizers(
    request_params: RequestParamsFertilizer = Depends(parse_filter_search_params_fertilizers()),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get list fertilizers
    """
    fertilizers = await crud.fertilizer.list_fertilizer(session, request_params)
    responses = []
    for fertilizer in fertilizers:
        response = {**fertilizer}
        response.update({"resources": await crud.fertilizer.get_resources(session, fertilizer.Fertilizers.id, resource_type.TREE)})
        responses.append(response)
    return responses


@router.post(
    "",
    name=f"{name}:create",
    status_code=201
)
async def create_fertilizer(
    name: str,
    description: Optional[str] = None,
    manufacturer: str  = None,
    manufacture_date: datetime  = None,
    compositions: Optional[str]  = None,
    type: Literal["Hữu cơ", "Vô cơ", "Vi sinh", "Khác"]  = None,
    files: Optional[List[UploadFile]] = File(None),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Create a fertilizer
    """
    fertilizer_in = FertilizerCreate(
        name=name,
        description=description,
        manufacturer=manufacturer,
        manufacture_date=manufacture_date,
        compositions=compositions,
        type=type
    )
    fertilizer = await crud.fertilizer.create(
        session, fertilizer_in, updated_by=user.id
    )
    response = FertilizerSchema.from_orm(fertilizer)
    if files:
        resources = await upload_multiple_file(session, files, updated_by=user.id)
        await crud.fertilizer.add_resources(session, resources, fertilizer.id, resource_type.FERTILIZER)
        response.resources = resources
    return response


@router.get(
    "/{fertilizer_id}",
    name=f"{name}:one",
)
async def get_fertilizer_by_id(
    fertilizer_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
) -> Any:
    """
    Get fertilizer by id
    """
    fertilizer = await crud.fertilizer.get_fertilizer(session, fertilizer_id)
    if not fertilizer:
        raise HTTPException(
            status_code=404,
            detail="The fertilizer not found."
        )
    response = {**fertilizer}
    response.update({"resources": await crud.tree.get_resources(session, fertilizer_id, resource_type.FERTILIZER)})
    return response


@router.patch(
    "/{fertilizer_id}",
    name=f"{name}:update",
)
async def update_fertilizer_by_id(
    fertilizer_id: uuid.UUID,
    fertilizer_in: FertilizerUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Update fertilizer by id
    - updated_by
    """
    fertilizer = await crud.fertilizer.get(session, fertilizer_id)
    if not fertilizer:
        raise HTTPException(
            status_code=404,
            detail="The fertilizer not found."
        )
    fertilizer = await crud.fertilizer.update(
        session, fertilizer, fertilizer_in, updated_by=user.id
    )
    return fertilizer


@router.delete(
    "/{fertilizer_id}",
    name=f"{name}:delete",
)
async def delete_fertilizer_by_id(
    fertilizer_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_owner)),
) -> Any:
    """
    Delete fertilizer by id
    - updated_by
    - deleted_at
    """
    fertilizer = await crud.fertilizer.get(session, fertilizer_id)
    if not fertilizer:
        raise HTTPException(
            status_code=404,
            detail="The fertilizer not found."
        )
    await crud.fertilizer.delete(session, fertilizer, updated_by=user.id)
    return "The fertilizer deleted successfully!"