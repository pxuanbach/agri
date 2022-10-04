from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import uuid

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import Base
from app.models.item_resources import ItemResources
from app.models.resource import Resource

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    # async def get(self, db: Session, id: Any) -> Optional[ModelType]:
    #     result = await db.execute(select(self.model).where(self.model.id == id))
    #     obj = result.scalars().first()
    #     await db.commit()
    #     return obj
    # def get_multi(
    #     self, db: Session, *, skip: int = 0, limit: int = 100
    # ) -> List[ModelType]:
    #     return db.query(self.model).offset(skip).limit(limit).all()

    # def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
    #     obj_in_data = jsonable_encoder(obj_in)
    #     db_obj = self.model(**obj_in_data)  # type: ignore
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    # def update(
    #     self,
    #     db: Session,
    #     *,
    #     db_obj: ModelType,
    #     obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    # ) -> ModelType:
    #     obj_data = jsonable_encoder(db_obj)
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     for field in obj_data:
    #         if field in update_data:
    #             setattr(db_obj, field, update_data[field])
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    # def remove(self, db: Session, *, id: int) -> ModelType:
    #     obj = db.query(self.model).get(id)
    #     db.delete(obj)
    #     db.commit()
    #     return obj

    async def add_resources(
        self, db: AsyncSession, resources: List[Resource], item_id: uuid.UUID, item_type: str
    ) -> List[Resource]:
        if not resources:
            return None
        items = []
        for obj in resources:
            item = ItemResources(
                id=uuid.uuid4(),
                item_type=item_type,
                item_id=item_id,
                resource_id=obj.id,
                updated_by=obj.updated_by,
            )
            items.append(item)
        db.add_all(items)
        await db.commit()
        return resources
    
    async def get_resources(
        self, db: AsyncSession, item_id: uuid.UUID, item_type: str
    ) -> List[Resource]:
        resources = (
            (
                await db.execute(
                    select(Resource)
                    .filter(
                        ItemResources.item_id == item_id,
                        ItemResources.item_type == item_type,
                        Resource.id == ItemResources.resource_id,
                        ItemResources.deleted_at == None,
                    )
                )
            )
            .scalars()
            .all()
        )
        return resources

    async def delete_resources(
        self, db: AsyncSession, resource_ids: List[uuid.UUID], item_id: uuid.UUID, item_type: str
    ) -> None:
        if not resource_ids:
            return None
        item_resources: List[ItemResources] = (
            (
                await db.execute(
                    select(ItemResources)
                    .filter(
                        ItemResources.item_id == item_id,
                        ItemResources.item_type == item_type,
                        Resource.id == ItemResources.resource_id,
                        Resource.id.in_(resource_ids)
                    )
                )
            )
            .scalars()
            .all()
        )
        for obj in item_resources:
            obj.deleted_at = datetime.utcnow()
        db.add_all(item_resources)
        await db.commit() 
        return
