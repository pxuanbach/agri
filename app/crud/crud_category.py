from typing import Any
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.crud.base import CRUDBase
from app.models.categories import Categories
from app.schemas.categories import CategoryCreate, CategoryUpdate

from app.db import Base


class CRUDCategory(CRUDBase[Categories, CategoryCreate, CategoryUpdate]):

    async def list_category(self, db: AsyncSession
    ) -> Any:
        categories = (
            await db.execute(
                select(Categories)
            )
        ).all()

        return categories

    async def get_category_by_id(self, db: AsyncSession, category_id: uuid.UUID
    ) -> Any:
        category = (
            await db.execute(
                select(Categories)
                .filter(Categories.id == category_id)
            )
        ).first()

        return category

    async def create_category(self, db: AsyncSession, category_in: CategoryCreate
    ) -> Any:
        new_category = Categories(
            id = uuid.uuid4(),
            name = category_in.name,
            description = category_in.description,
        )
        db.add(new_category)
        await db.commit()
        return new_category

category = CRUDCategory(Categories)