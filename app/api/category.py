from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.deps.db import get_async_session
from app.deps.users import AuthorizeCurrentUser
from app.core.constants import role_authen
from app import crud
from app.models.users import User
from app.schemas.categories import CategoryCreate

# Awards
name="category"
router = APIRouter(prefix=f"/{name}")

@router.get(
    "",
    name=f"{name}:get-category",
)
async def list_categories(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_all)),
):
    """
    List categories
    """
    categories = await crud.category.list_category(session)
    return categories

@router.post(
    "",
    name=f"{name}:create-category",
)
async def create_category(
    category_in: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(AuthorizeCurrentUser(role_authen.roles_admin)),
):
    """
    Create category
    """

    new_category = await crud.category.create_category(session,category_in)
    return new_category