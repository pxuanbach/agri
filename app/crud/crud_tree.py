from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.core.constants import rfid_type
from app.models.rfids import Rfids

from app.utils import random_string_and_number
from app.crud.base import CRUDBase
from app.core.constants import resource_type
from app.models.trees import Trees
from app.models.resource import Resource
from app.models.item_resources import ItemResources
from app.schemas.trees import (
    TreeCreate,
    TreeUpdate
)


class CRUDTree(CRUDBase[Trees, TreeCreate, TreeUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Any:
        result = (
            (
                await db.execute(
                    select(self.model)
                    .filter(self.model.id == id)
                    .filter(Trees.deleted_at == None)
                )
            )
            .scalars()
            .first()
        )
        return result

    async def get_tree(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Any:
        return (
            (
                await db.execute(
                    select(
                        Trees,
                        Rfids
                    )
                    .filter(Trees.id == id)
                    .outerjoin(Rfids, and_(
                            Rfids.item_type == rfid_type.TREE,
                            Rfids.item_id == Trees.id,
                            Rfids.deleted_at == None
                        )
                    )
                    .filter(Trees.deleted_at == None)
                )
            )
            .first()
        )

    def add_filter(self, query, request_params) -> Any:
        if request_params.search:
            query = query.filter(
                or_(
                    func.lower(self.model.code).contains(request_params.search),
                    func.lower(self.model.name).contains(request_params.search),
                )
            )
        if request_params.name:
            query = query.filter(
                func.lower(self.model.name).contains(request_params.name),
            )
        if request_params.code:
            query = query.filter(
                func.lower(self.model.code).contains(request_params.code),
            )
        if request_params.updated_by:
            query = query.filter(
                self.model.updated_by == request_params.updated_by
            )
        return query

    async def get_multi(
        self, db: AsyncSession, request_params
    ) -> List[Trees]:
        query = select(self.model).filter(Trees.deleted_at == None)
        query = self.add_filter(query, request_params)
        datas = (
            (
                await db.execute(query)
            )
            .scalars()
            .all()
        )
        return datas

    async def  list_tree(
        self, db: AsyncSession, request_params
    ) -> Any:
        query = select(
            Trees,
            Rfids
            ).outerjoin(Rfids, and_(
            Rfids.item_type == rfid_type.TREE,
            Rfids.item_id == Trees.id,
            Rfids.deleted_at == None
            )
        ).filter(Trees.deleted_at == None)
        
        query = self.add_filter(query, request_params)
        datas = (
            (
                await db.execute(query)
            )
            .all()
        )
        return datas

    async def unique_code(self, db: AsyncSession) -> str:
        while True:
            code = random_string_and_number(6)
            # print(f"{code}\n")
            db_obj = (
                (
                    await db.execute(
                        select(self.model)
                        .filter(self.model.code == code)
                    )
                )
                .scalars()
                .first()
            )
            if not db_obj:
                return code

    async def create(
        self, db: AsyncSession, obj_in: TreeCreate, **kwargs
    ) -> Trees:
        db_obj = self.model(**obj_in.dict(exclude={"resources"}), id=uuid.uuid4()) 
        db_obj.updated_by = kwargs.get("updated_by")
        db_obj.code = await self.unique_code(db)
        db.add(db_obj)
        await db.commit()

        rfid = Rfids(
            id=uuid.uuid4(),
            code = db_obj.code,
            item_id = db_obj.id,
            item_type = rfid_type.TREE,
            updated_by = kwargs.get("updated_by")
        )
        db.add(rfid)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: Trees,
        obj_in: Union[TreeUpdate, Dict[str, Any]],
        **kwargs
    ) -> Trees:
        """updated_by"""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data.update({"updated_by": kwargs.get("updated_by")})
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def delete(
        self, db: AsyncSession, db_obj: Trees, **kwargs
    ) -> Trees:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)

        rfid = (
            await db.execute(
                select(Rfids)
                .filter(Rfids.item_id == db_obj.id)
                .filter(Rfids.item_type == rfid_type.TREE)
                .filter(Rfids.deleted_at == None)
            )
        ).scalars().first()
        if rfid:
            rfid.deleted_at = datetime.utcnow()
            rfid.updated_by = kwargs.get("updated_by")
            db.add(rfid)
        await db.commit()
        return 


tree = CRUDTree(Trees)