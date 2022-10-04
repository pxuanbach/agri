from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.transfer_status import TransferStatus
from app.schemas.transfer import (
    TransferStatusCreate,
    TransferStatusUpdate
)


class CRUDTransferStatus(CRUDBase[TransferStatus, TransferStatusCreate, TransferStatusUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[TransferStatus]:
        return (
            (
                await db.execute(
                    select(self.model)
                    .filter(self.model.id == id)
                )
            )
            .scalars()
            .first()
        )

    async def get_multi(
        self, db: AsyncSession
    ) -> List[TransferStatus]:
        datas = (
            (
                await db.execute(
                    select(self.model)
                )
            )
            .scalars()
            .all()
        )
        return datas

    async def create(
        self, db: AsyncSession, obj_in: TransferStatusCreate, **kwargs
    ) -> TransferStatus:
        db_obj = self.model(**obj_in.dict(), id=uuid.uuid4()) 
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: TransferStatus,
        obj_in: Union[TransferStatusUpdate, Dict[str, Any]],
        **kwargs
    ) -> TransferStatus:
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
        self, db: AsyncSession, db_obj: TransferStatus, **kwargs
    ) -> TransferStatus:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return 


transfer_status = CRUDTransferStatus(TransferStatus)