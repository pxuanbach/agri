from typing import Any
import uuid
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func
from app.crud.base import CRUDBase
from app.deps.users import get_user_manager
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate
from app.models.role import Role


class CRUDUser(CRUDBase[User,UserCreate,UserUpdate]
):

    async def create_sub_customers(
        self, db: AsyncSession, my_user_id: uuid.UUID, role_id: uuid.UUID, name: str, email: str, password: str
    ) -> User:
        user_manager = next(get_user_manager())
        new_user = User(
            id=uuid.uuid4(),
            created_by = my_user_id,
            role_id = role_id,
            name = name,
            email = email,
            hashed_password = user_manager.password_helper.hash(password),
        )
        db.add(new_user)
        await db.commit()
        return new_user

    async def total_user(
        self, db: AsyncSession, request_params
    ) -> Any:
        query = (
            select(func.count(User.id))
            .outerjoin(Role, Role.id == User.role_id)
            .group_by(User.id)
            .group_by(Role.id)
        )
        query = await self.add_filter_to_search_user_query(request_params, query)
        total = await db.scalar(query)
        return total

    async def total_sub_user(
        self, db: AsyncSession, my_user_id: uuid.UUID, request_params
    ) -> Any:
        query = (
            select(func.count(User.id))
            .outerjoin(Role, Role.id == User.role_id)
            .filter(User.created_by == my_user_id)
            .filter(User.is_active == True)
            .group_by(User.id)
            .group_by(Role.id)
        )
        query = await self.add_filter_to_search_user_query(request_params, query)
        total = await db.scalar(query)
        return total

    async def search_user(
        self, db: AsyncSession, request_params
    ) -> User:
        query = (
                select(
                    User.id,
                    User.name,
                    User.address,
                    User.email,
                    User.dob,
                    User.avatar_id,
                    User.created_by,
                    User.deleted_at, 
                    User.created_at, 
                    User.updated_at,
                    User.updated_by,
                    Role
                )
                .offset(request_params.skip)
                .limit(request_params.limit)
                .order_by(request_params.order_by)
                .outerjoin(Role, Role.id == User.role_id)
                .group_by(User.id)
                .group_by(Role.id)
            )
        query = await self.add_filter_to_search_user_query(request_params, query)
        users = (await db.execute(query)).all()
        return users

    async def add_filter_to_search_user_query(
        self, request_params, query
    )-> User:
        if request_params.search:
            query = query.filter(
                or_(
                    func.lower(User.name).contains(request_params.search),
                    func.lower(User.address).contains(request_params.search),
                    func.lower(User.email).contains(request_params.search),
                )
            )
        if request_params.role_id:
            query = query.filter(
                User.role_id == request_params.role_id
            )
        if request_params.name:
            query = query.filter(
                User.name == request_params.name
            )
        if request_params.address:
            query = query.filter(
                User.address == request_params.address
            )
        if request_params.email:
            query = query.filter(
                User.email == request_params.email
            )
        if request_params.is_deleted == False:
            query = query.filter(
                User.deleted_at == None
            )
        return query

    async def get_sub_customers(
        self, db: AsyncSession, my_user_id: uuid.UUID, request_params
    ) -> User:
        query=(
                    select(
                        User.id,
                        User.name,
                        User.address,
                        User.email,
                        User.dob,
                        User.avatar_id,
                        User.created_by,
                        User.deleted_at, 
                        User.created_at, 
                        User.updated_at,
                        User.updated_by,
                        Role
                    )
                    .offset(request_params.skip)
                    .limit(request_params.limit)
                    .order_by(request_params.order_by)
                    .outerjoin(Role, Role.id == User.role_id)
                    .filter(User.created_by == my_user_id)
                    .filter(User.is_active == True)
                    .group_by(User.id)
                    .group_by(Role.id)
            )
        query = await self.add_filter_to_search_user_query(request_params, query)
        users = (await db.execute(query)).all()
        return users

    async def get_role_by_id(
        self, db: AsyncSession, role_id: uuid.UUID
    ) -> Role:
        result = await db.execute(select(Role).where(Role.id == role_id))
        role = result.scalars().first()
        return role

    async def get_user_detail_by_id(
        self, db: AsyncSession, user_id: uuid.UUID
    )->User:
        result = await db.execute(
            select(
                User.id,
                User.name,
                User.address,
                User.email,
                User.dob,
                User.firebase_register_token,
                User.avatar_id,
                User.created_by,
                User.deleted_at, 
                User.created_at, 
                User.updated_at,
                User.updated_by,
                Role
            )
            .outerjoin(Role, Role.id == User.role_id)
            .filter(User.id == user_id)
            .filter(User.is_active == True)
            .group_by(User.id)
            .group_by(Role.id)
            )
        user = result.first()
        return user

    async def get_user_by_id(
        self, db: AsyncSession, user_id: uuid
    )->User:
        result = await db.execute(
            select(User)
            .filter(User.id == user_id)
            .filter(User.is_active == True)
            )
        user = result.scalars().first()
        return user

user = CRUDUser(User)
