from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.transfer_status import TransferStatus
from app.models.transfer_request import TransferRequests
from app.core.constants import transfer_status
from app.schemas.transfer import (
    TransferRequestCreate,
    TransferRequestUpdate
)
from app.models.users import User
from app.models.products import Products


class CRUDTransferRequest(CRUDBase[TransferRequests, TransferRequestCreate, TransferRequestUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[TransferRequests]:
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
    ) -> List[TransferRequests]:
        datas = (
            (
                await db.execute(
                    select(self.model).filter(self.model.deleted_at == None)
                )
            )
            .scalars()
            .all()
        )
        return datas

    async def get_transfer_request( self, db: AsyncSession, id: uuid.UUID
    )-> Any:
        transfer_request = (
            await db.execute(
                select(
                    TransferRequests,
                    Products
                )
                .filter(TransferRequests.id == id)
                .filter(Products.id == TransferRequests.product_id)
                .filter(TransferRequests.deleted_at == None)
            )
        ).first()
        return transfer_request

    async def total_transfer_requests_by_product(
        self, db: AsyncSession, request_params
    )->Any:
        query = (
                select(
                    func.count(TransferRequests.id)
                )
                .filter(Products.id == TransferRequests.product_id)
                .group_by(TransferRequests.id)
                .group_by(Products.id)
            )
        query = await self.add_filter_to_transfer_request_query(db, request_params, query)
        total = await db.scalar(query)
        return total

    async def list_transfer_requests_by_product( self, db: AsyncSession, request_params
    )-> Any:
        query = (
                select(
                    TransferRequests,
                    TransferStatus
                )
                .offset(request_params.skip)
                .limit(request_params.limit)
                .order_by(request_params.order_by)
                .filter(Products.id == TransferRequests.product_id)
                .outerjoin(TransferStatus, 
                TransferStatus.id == TransferRequests.transfer_status_id)
                .group_by(TransferRequests.id)
                .group_by(Products.id)
                .group_by(TransferStatus.id)
            )
        query = await self.add_filter_to_transfer_request_query(db, request_params, query)
        transfer_request = (await db.execute(query)).all()
        return transfer_request

    async def add_filter_to_transfer_request_query(self, db: AsyncSession, request_params, query
    )-> Any:
        if request_params.product_id:
            query = query.filter(
                TransferRequests.product_id == request_params.product_id
            )
        if request_params.transfer_from_user_id:
            query = query.filter(
                TransferRequests.transfer_from_user_id == request_params.transfer_from_user_id
            )
        if request_params.transfer_to_user_id:
            query = query.filter(
                TransferRequests.transfer_to_user_id == request_params.transfer_to_user_id
            )
        if request_params.transfer_status:
            status = (
                await db.execute(
                    select(TransferStatus.id)
                    .filter(func.lower(TransferStatus.name) == request_params.transfer_status)
                )
            ).scalars().first()
            if not status:
                raise HTTPException(
                    status_code=404,
                    detail="status not found."
                )
            else:
                query = query.filter(
                    TransferRequests.transfer_status_id == status
                )
        if request_params.is_deleted == False:
            query = query.filter(
                Products.deleted_at == None
            )
        return query

    async def get_status(self, db: AsyncSession, status: str
    )-> Any:
        status_id = (
            await db.execute(
                select(TransferStatus.id)
                .filter(TransferStatus.name == status)
            )
        ).scalars().first()
        return status_id

    async def create(
        self, db: AsyncSession, obj_in: TransferRequestCreate, **kwargs
    ) -> TransferRequests:
        db_obj = self.model(**obj_in.dict(), id=uuid.uuid4(), transfer_status_id=kwargs.get("status_id")) 
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def check_existed_transfer_request(
        self, db: AsyncSession, product_id: uuid.UUID, requested_by: uuid.UUID
    )-> Any:
        transfer_request = (
            await db.execute(
                select(TransferRequests)
                .filter(TransferRequests.product_id == Products.id)
                .filter(TransferRequests.product_id == product_id)
            )
        ).scalars().first()
        return transfer_request

    async def update_transfer_requests_status_by_product(
        self, db: AsyncSession, product_id: uuid.UUID, status: uuid.UUID, **kwargs
    )-> Any:
        pending_id = await self.get_status(db, transfer_status.PENDING)
        transfer_requests = (
            await db.execute(
                select(TransferRequests)
                .filter(TransferRequests.product_id == Products.id)
                .filter(Products.id == product_id)
                .filter(TransferRequests.transfer_status_id == pending_id)
            )
        ).scalars().all()
        updated_request = []
        for transfer_request in transfer_requests:
            transfer_request.transfer_status_id = status
            transfer_request.updated_by = kwargs.get("updated_by")
            updated_request.append(transfer_request)
        db.add_all( updated_request)
        await db.commit()
        return updated_request

    async def update_transfer_request_status(
        self, db: AsyncSession, db_obj: TransferRequests, status: uuid.UUID, **kwargs
    )-> Any:
        db_obj.transfer_status_id = status
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: TransferRequests,
        obj_in: Union[TransferRequestUpdate, Dict[str, Any]],
        **kwargs
    ) -> TransferRequests:
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
        self, db: AsyncSession, db_obj: TransferRequests, **kwargs
    ) -> TransferRequests:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return 


transfer_request = CRUDTransferRequest(TransferRequests)