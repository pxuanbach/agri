from datetime import datetime
import math
from pathlib import Path
from typing import Any, Optional
import uuid
import aiofiles
import filetype
from fastapi import BackgroundTasks, Depends, Form, HTTPException, Request, UploadFile, status
from fastapi.routing import APIRouter
from fastapi_users import models
from fastapi_users.manager import (
    BaseUserManager,
    InvalidPasswordException,
    UserAlreadyExists,
)
from fastapi_users.router.common import ErrorCode, ErrorModel
from PIL import Image
from app.schemas.responses import ResponsePagination
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.deps.db import get_async_session
from app.deps.request_params import parse_filter_search_params_users
from app.deps.users import AuthorizeCurrentUser, get_topics_by_role, get_user_manager
from app import crud
from app.models.users import User
from app.core.firebase import _firebase
from app.schemas.request_params import RequestParamsUser
from app.schemas.users import User as UserSchema
from app.schemas.users import UserChagePassword, UserUpdate
from app.core.config import settings
from app.models.resource import Resource
from app.core.constants import role_authen, role_key

name="user"
router = APIRouter(prefix=f"/{name}")

@router.get(
    "/list-sub-user",
    name=f"{name}:list-sub-user",
)
async def list_sub_users(
    request_params: RequestParamsUser = Depends(
        parse_filter_search_params_users(User)
    ),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    List your sub users
    """
    total = await crud.user.total_sub_user(session, user.id, request_params)
    users = await crud.user.get_sub_customers(session, user.id, request_params)
    if not users:
        return ResponsePagination(
            page_total=1,
            page_size=request_params.limit,
            page=request_params.skip / request_params.limit + 1,
            data=users,
        )
    return ResponsePagination(
        page_total=math.ceil(total/ request_params.limit),
        page_size=request_params.limit,
        page=request_params.skip / request_params.limit + 1,
        data=users,
    )

@router.get(
    "",
    name=f"{name}:list-user-by-search",
)
async def search_users(
    request_params: RequestParamsUser = Depends(
        parse_filter_search_params_users(User)
    ),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List your search users
    """
    total = await crud.user.total_user(session, request_params)
    users = await crud.user.search_user(session, request_params)
    if not users:
        return ResponsePagination(
            page_total=1,
            page_size=request_params.limit,
            page=request_params.skip / request_params.limit + 1,
            data=users,
        )
    return ResponsePagination(
        page_total=math.ceil(total/ request_params.limit),
        page_size=request_params.limit,
        page=request_params.skip / request_params.limit + 1,
        data=users,
    )

@router.get(
    "/user",
    name=f"{name}:get-user",
)
async def get_user_by_id(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_async_session)
):
    """
    get user detail by id
    """
    user_detail = await crud.user.get_user_detail_by_id(session, user_id)
    return user_detail

@router.get(
    "/me",
    name=f"{name}:get-me",
)
async def get_me_user(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    get your user detail
    """
    user_detail = await crud.user.get_user_detail_by_id(session, user.id)
    return user_detail

@router.post(
    "",
    name=f"{name}:create-user",
)
async def create_sub_user(
    email: str,
    name: str,
    password: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    Create sub user for business
    """
    current_user_role = await crud.user.get_role_by_id(
        session, user.role_id
    )
    if not current_user_role:
        raise HTTPException(
            status_code=404,
            detail="User role of current user not found.",
        )
    if current_user_role.key != role_key.ADMIN and current_user_role.key != role_key.CUSTOMER:
        raise HTTPException(
            status_code=401,
            detail="User do not have permission.",
        )
    new_user = await crud.user.create_sub_customers(session, user.id, user.role_id, name, email, password)
    return new_user

@router.post(
    "/update-avatar", status_code=200, response_model=UserSchema, include_in_schema=True
)
async def update_avatar(
    file: UploadFile,
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
    session: AsyncSession = Depends(get_async_session),
):
    ts = int(float(datetime.now().strftime('%s.%f')) * 1e3)
    filename = f"""{ts}_{file.filename}"""
    Path(f"""{settings.STATIC_PATH}/media""").mkdir(parents=True, exist_ok=True)
    destination_file_path = f"""{settings.STATIC_PATH}/media/{filename}"""
    _size: int = 0
    async with aiofiles.open(destination_file_path, 'wb') as out_file:
        while content := await file.read(1024):  # async read file chunk
            _size += len(content)
            await out_file.write(content)  # async write file chunk
    media = Resource(
            id = uuid.uuid4(),
            name = filename,
            file_path = f"/static/media/{filename}",
            file_size = str(_size),
            file_type = file.content_type,
            updated_by = user.id
    )
    session.add(media)
    await session.commit()

    if filetype.is_image(destination_file_path):
        pass
    else:
        raise HTTPException(
            status_code=400,
            detail="Only image type allowed",
        )

    _user: Optional[User] = await session.get(User, user.id)
    _user.avatar_id = media.id
    session.add(_user)
    await session.commit()
    return _user


@router.post(
    "/change-password",
    status_code=200,
    response_model=UserSchema,
    include_in_schema=True,
)
async def change_password(
    obj_in: UserChagePassword,
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
    session: AsyncSession = Depends(get_async_session),
):
    # Check current password
    user_manager = next(get_user_manager())
    verified, updated_password_hash = user_manager.password_helper.verify_and_update(
        obj_in.current_password, user.hashed_password
    )
    if not verified:
        raise HTTPException(
            status_code=400,
            detail="Current password incorrect",
        )
    if obj_in.new_password != obj_in.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="New password not match",
        )
    await user_manager.validate_password(obj_in.new_password, user)
    hashed_password = user_manager.password_helper.hash(obj_in.new_password)

    _user: Optional[User] = await session.get(User, user.id)
    _user.hashed_password = hashed_password
    session.add(_user)
    await session.commit()
    return _user

@router.patch(
    "/me",
    response_model=UserSchema,
    dependencies=[Depends(AuthorizeCurrentUser(role_authen.roles_all))],
    name="users:patch_current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_me(
    background_tasks: BackgroundTasks,
    request: Request,
    user_update: UserUpdate,  # type: ignore
    user: User = Depends(AuthorizeCurrentUser((role_authen.roles_all))),  # type: ignore
    user_manager: BaseUserManager[models.UC, models.UD] = Depends(get_user_manager),
):
    # user_manager = next(get_user_manager())
    try:
        user_mana = await user_manager.update(user_update, user, safe=True, request=request)
        # Subscribe topic
        try:
            topics = get_topics_by_role(user)
            if user_mana.firebase_register_token:
                background_tasks.add_task(
                    _firebase.subscribe,
                    tokens=[user_mana.firebase_register_token], 
                    topics=topics,
                )
        except Exception as e:
            print("ERROR", str(e))

        return user_mana
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )