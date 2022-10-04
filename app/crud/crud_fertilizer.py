from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.models.rfids import Rfids
from app.core.constants import rfid_type

from app.utils import random_string_and_number
from app.crud.base import CRUDBase
from app.models.fertilizers import Fertilizers
from app.schemas.fertilizers import (
    FertilizerCreate,
    FertilizerUpdate
)


class CRUDFertilizer(CRUDBase[Fertilizers, FertilizerCreate, FertilizerUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[Fertilizers]:
        return (
            (
                await db.execute(
                    select(
                        self.model,
                        Rfids
                    ).filter(self.model.id == id)
                    .filter(self.model.deleted_at == None)
                )
            )
            .scalars()
            .first()
        )

    async def get_fertilizer(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Any:
        return (
            (
                await db.execute(
                    select(
                        Fertilizers,
                        Rfids
                    ).filter(Fertilizers.id == id)
                    .outerjoin(Rfids, and_(
                        Rfids.item_type == rfid_type.FERTILIZER,
                        Rfids.item_id == Fertilizers.id,
                        Rfids.deleted_at == None
                        )
                    )
                    .filter(Fertilizers.deleted_at == None)
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
                    func.lower(self.model.manufacturer).contains(request_params.search),
                )
            )
        if request_params.name:
            query = query.filter(
                func.lower(self.model.name).contains(request_params.name),
            )
        if request_params.manufacturer:
            query = query.filter(
                func.lower(self.model.manufacturer).contains(request_params.manufacturer),
            )
        if request_params.code:
            query = query.filter(
                func.lower(self.model.code).contains(request_params.code),
            )
        if request_params.updated_by:
            query = query.filter(
                self.model.updated_by == request_params.updated_by
            )
        if request_params.types:
            query = query.filter(
                self.model.type.in_(request_params.types)
            )
        return query
        

    async def get_multi(
        self, db: AsyncSession, request_params
    ) -> List[Fertilizers]:
        query = select(
            self.model,
            Rfids
        ).outerjoin(Rfids, and_(
            Rfids.item_type == rfid_type.FERTILIZER,
            Rfids.item_id == self.model.id,
            Rfids.deleted_at == None
            )
        ).filter(self.model.deleted_at == None)
        
        
        query = self.add_filter(query, request_params)
        datas = (
            (
                await db.execute(query)
            )
            .scalars()
            .all()
        )
        return datas

    async def list_fertilizer(
        self, db: AsyncSession, request_params
    ) -> Any:
        query = select(
            Fertilizers,
            Rfids
        ).outerjoin(Rfids, and_(
            Rfids.item_type == rfid_type.FERTILIZER,
            Rfids.item_id == Fertilizers.id,
            Rfids.deleted_at == None
            )
        ).filter(Fertilizers.deleted_at == None)
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
        self, db: AsyncSession, obj_in: FertilizerCreate, **kwargs
    ) -> Fertilizers:
        db_obj = self.model(**obj_in.dict(), id=uuid.uuid4()) 
        db_obj.updated_by = kwargs.get("updated_by")
        db_obj.code = await self.unique_code(db)
        db.add(db_obj)
        await db.commit()

        rfid = Rfids(
            id=uuid.uuid4(),
            code = db_obj.code,
            item_id = db_obj.id,
            item_type = rfid_type.FERTILIZER,
            updated_by = kwargs.get("updated_by")
        )
        db.add(rfid)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: Fertilizers,
        obj_in: Union[FertilizerUpdate, Dict[str, Any]],
        **kwargs
    ) -> Fertilizers:
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
        self, db: AsyncSession, db_obj: Fertilizers, **kwargs
    ) -> Fertilizers:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)

        rfid = (
            await db.execute(
                select(Rfids)
                .filter(Rfids.item_id == db_obj.id)
                .filter(Rfids.item_type == rfid_type.FERTILIZER)
                .filter(Rfids.deleted_at == None)
            )
        ).scalars().first()
        if rfid:
            rfid.deleted_at = datetime.utcnow()
            rfid.updated_by = kwargs.get("updated_by")
            db.add(rfid)
        await db.commit()
        return 


fertilizer = CRUDFertilizer(Fertilizers)