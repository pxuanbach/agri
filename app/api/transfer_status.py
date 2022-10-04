from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.constants import role_key
from app import crud
from app.deps.db import get_async_session
from app.models.users import User
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen
from app.schemas.transfer import (
    TransferStatus as TransferStatusSchema,
    TransferStatusCreate,
    TransferStatusUpdate
)

name = "transfer-status"
router = APIRouter(prefix=f"/{name}")


@router.get(
    "",
    name=f"{name}:list",
)
async def get_list_transfer_status(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin)),
) -> Any:
    """
    Get list transfer status
    """
    transfer_status = await crud.transfer_status.get_multi(session)
    return transfer_status


@router.post(
    "",
    name=f"{name}:create",
    status_code=201,
    include_in_schema=False,
)
async def create_transfer_status(
    transfer_status_in: TransferStatusCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin)),
) -> Any:
    """
    Create a transfer status
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )

    transfer_status = await crud.transfer_status.create(
        session, transfer_status_in, updated_by=user.id
    )
    return transfer_status


@router.get(
    "/{transfer_status_id}",
    name=f"{name}:one",

    include_in_schema=False,
)
async def get_transfer_status_by_id(
    transfer_status_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin)),
) -> Any:
    """
    Get transfer status by id
    """
    transfer_status = await crud.transfer_status.get(session, transfer_status_id)
    if not transfer_status:
        raise HTTPException(
            status_code=404,
            detail="The transfer status not found."
        )
    return transfer_status


@router.patch(
    "/{transfer_status_id}",
    name=f"{name}:update",
    include_in_schema=False,
)
async def update_transfer_status_by_id(
    transfer_status_id: uuid.UUID,
    transfer_status_in: TransferStatusUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin))
) -> Any:
    """
    Update transfer status by id
    - updated_by
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )

    transfer_status = await crud.transfer_status.get(session, transfer_status_id)
    if not transfer_status:
        raise HTTPException(
            status_code=404,
            detail="The transfer status not found."
        )
    transfer_status = await crud.transfer_status.update(
        session, transfer_status, transfer_status_in, updated_by=user.id
    )
    return transfer_status


@router.delete(
    "/{transfer_status_id}",
    name=f"{name}:delete",
    include_in_schema=False,
)
async def delete_transfer_status_by_id(
    transfer_status_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin))
) -> Any:
    """
    Delete transfer status by id
    - updated_by
    - deleted_at
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN:
        raise HTTPException(
            status_code=404,
            detail="User do not have permission.",
        )

    transfer_status = await crud.transfer_status.get(session, transfer_status_id)
    if not transfer_status:
        raise HTTPException(
            status_code=404,
            detail="The transfer_status not found."
        )
    await crud.transfer_status.delete(session, transfer_status, updated_by=user.id)
    return "The transfer_status deleted successfully!"