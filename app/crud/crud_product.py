from datetime import datetime
from typing import Any, List, Optional, Union, Dict
import uuid
from fastapi import HTTPException
from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.core.constants import rfid_type
from app.models.rfids import Rfids
from app.models.product_transfer_status import ProductTransferStatus
from app.utils import random_string_and_number
from app.crud.base import CRUDBase
from app.models.products import Products
from app.schemas.products import (
    ProductCreate,
    ProductUpdate
)
from app.models.users import User
from app.models.transfer_request import TransferRequests
from app.models.transfer_status import TransferStatus
from app.core.constants import product_transfer_status


class CRUDProduct(CRUDBase[Products, ProductCreate, ProductUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[Products]:
        return (
            (
                await db.execute(
                    select(self.model)
                    .filter(self.model.id == id)
                    .filter(self.model.deleted_at == None)
                )
            )
            .scalars()
            .first()
        )

    async def get_multi(
        self, db: AsyncSession
    ) -> List[Products]:
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

    async def get_product_by_id(self, db: AsyncSession, user_id: uuid.UUID, product_id: uuid.UUID
    )->Any:
        product = (
            await db.execute(
            select(
                Products,
                Rfids,
                ProductTransferStatus.transfer_status.label("product_status"),
                User.id.label("user_id"),
                User.name.label("user_name"),
                User.address.label("user_address"),
                User.email.label("user_email"),
                User.dob.label("user_dob"),
                User.avatar_id.label("user_avatar")
                )
            .filter(Products.deleted_at == None)
            .filter(Products.id == product_id)
            .filter(User.id == Products.updated_by)
            .outerjoin(Rfids, and_(
                    Rfids.item_type == rfid_type.PRODUCT,
                    Rfids.item_id == Products.id,
                    Rfids.deleted_at == None
                    )
                )
            .outerjoin(ProductTransferStatus, and_(
                Products.id == ProductTransferStatus.product_id,
                ProductTransferStatus.updated_by == user_id
                )
            )
            .group_by(Products.id)
            .group_by(User.id)
            .group_by(Rfids.id)
            .group_by(ProductTransferStatus.id)
            )
        ).first()
        return product

    async def total_products(self, db: AsyncSession, user_id:uuid.UUID, request_params
    )->Any:
        query = (
            select(func.count(Products.id))
            .filter(User.id == Products.updated_by)
            .outerjoin(ProductTransferStatus, and_(
                    Products.id == ProductTransferStatus.product_id,
                    ProductTransferStatus.updated_by == user_id
                    )
                )
            )
        query = await self.add_filter_to_product_query(db, request_params, query)
        total = await db.scalar(query)
        return total

    async def list_products(self, db: AsyncSession, user_id:uuid.UUID, request_params
    )->Any:
        query = (
            select(
                Products,
                ProductTransferStatus.transfer_status.label("product_status"),
                User.id.label("user_id"),
                User.name.label("user_name"),
                User.avatar_id.label("user_avatar")
                )
            .offset(request_params.skip)
            .limit(request_params.limit)
            .order_by(request_params.order_by)
            .outerjoin(ProductTransferStatus, and_(
                Products.id == ProductTransferStatus.product_id,
                ProductTransferStatus.updated_by == user_id
                )
            )
            .group_by(Products.id)
            .group_by(ProductTransferStatus.id)
            .group_by(User.id)
            )
        query = await self.add_filter_to_product_query(db, request_params, query)
        products = (await db.execute(query)).all()
        return products

    async def add_filter_to_product_query(self, db: AsyncSession, request_params, query
    )-> Any:
        if request_params.search:
            query = query.filter(
                or_(
                    func.lower(Products.name).contains(request_params.search),
                    func.lower(Products.code).contains(request_params.search),
                )
            )
        if request_params.user_id:
            user = (
                await db.execute(
                    select(
                        User.id,
                        User.created_by,
                        )
                    .filter(User.id == request_params.user_id)
                )
            ).first()
            if user.created_by is None:
                query = query.filter(User.id == Products.updated_by)
                query = query.filter(
                    User.id == request_params.user_id
                )
            else:
                query = query.filter(user.created_by == Products.updated_by)
                query = query.filter(
                    User.id == user.created_by
                )
        else:
            query = query.filter(User.id == Products.updated_by)
        if request_params.farm_id:
            query = query.filter(
                Products.farm_id == request_params.farm_id
            )
        if request_params.name:
            query = query.filter(
                Products.name == request_params.name
            )
        if request_params.product_status:
            if request_params.product_status == product_transfer_status.NORMAL:
                query = query.filter(
                    or_(
                        ProductTransferStatus.transfer_status == request_params.product_status,
                        ProductTransferStatus.transfer_status == None,
                    )
                )
            else:
                query = query.filter(
                        ProductTransferStatus.transfer_status == request_params.product_status
                )
        if request_params.code:
            query = query.filter(
                Products.code == request_params.code
            )
        if request_params.range_price:
            query = query.filter(
                or_(
                Products.price_in_retail <= request_params.range_price,
                Products.price_in_retail == None,
                )
            )
        if request_params.is_deleted == False:
            query = query.filter(
                Products.deleted_at == None
            )
        return query

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
        self, db: AsyncSession, obj_in: ProductCreate, **kwargs
    ) -> Products:
        db_obj = self.model(**obj_in.dict(), id=uuid.uuid4()) 
        db_obj.updated_by = kwargs.get("updated_by")
        db_obj.code = await self.unique_code(db)
        db.add(db_obj)
        await db.commit()

        product_status = ProductTransferStatus(
            id=uuid.uuid4(),
            product_id = db_obj.id,
            transfer_status = product_transfer_status.NORMAL,
            updated_by = kwargs.get("updated_by")
        )
        db.add(product_status)

        rfid = Rfids(
            id=uuid.uuid4(),
            code = db_obj.code,
            item_id = db_obj.id,
            item_type = rfid_type.PRODUCT,
            updated_by = kwargs.get("updated_by")
        )
        db.add(rfid)

        await db.commit()
        return db_obj

    async def get_product_transfer_status(
        self, db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID
    )->Any:
        status = (
            await db.execute(
                select(
                    ProductTransferStatus
                )
                .filter(ProductTransferStatus.product_id == Products.id)
                .filter(ProductTransferStatus.product_id == product_id)
                .filter(ProductTransferStatus.updated_by == user_id)
            )
        ).scalars().first()
        return status
    
    async def check_pending_product_status_of_requester(
        self, db: AsyncSession, product_id: uuid.UUID, user_id: uuid.UUID
    )->Any:
        status = (
            await db.execute(
                select(
                    TransferRequests
                )
                .filter(TransferRequests.transfer_to_user_id == user_id)
                .filter(TransferRequests.product_id == Products.id)
                .filter(Products.id == product_id)
                .filter(Products.deleted_at == None)
                .filter(TransferRequests.transfer_status_id == TransferStatus.id)
                .filter(TransferStatus.name == product_transfer_status.PENDING)
            )
        ).scalars().first()
        return status

    async def check_pending_product_status(
        self, db: AsyncSession, product_id: uuid.UUID
    )->Any:
        status = (
            await db.execute(
                select(
                    TransferRequests
                )
                .filter(TransferRequests.product_id == Products.id)
                .filter(Products.id == product_id)
                .filter(Products.deleted_at == None)
                .filter(TransferRequests.transfer_status_id == TransferStatus.id)
                .filter(TransferStatus.name == product_transfer_status.PENDING)
            )
        ).scalars().first()
        return status

    async def update_product_status(
        self, db: AsyncSession, product_id: uuid.UUID, **kwargs
    )->Any:
        updated_by = kwargs.get("updated_by")
        user = (await db.execute(
                select(User)
                .filter(User.id == updated_by)
            )
        ).scalars().first()
        if user.created_by != None:
            status = await self.get_product_transfer_status(db, product_id, user.created_by)
            if not status:
                product_transfer_status = ProductTransferStatus(
                    id = uuid.uuid4(),
                    product_id = product_id,
                    transfer_status = kwargs.get("product_status"),
                    updated_by = user.created_by
                )
                db.add(product_transfer_status)
            else:
                status.transfer_status = kwargs.get("product_status")
                db.add(status)

        status = await self.get_product_transfer_status(db, product_id, updated_by)
        if not status:
            product_transfer_status = ProductTransferStatus(
                id = uuid.uuid4(),
                product_id = product_id,
                transfer_status = kwargs.get("product_status"),
                updated_by = updated_by
            )
            db.add(product_transfer_status)
        else:
            status.transfer_status = kwargs.get("product_status")
            db.add(status)
        await db.commit()  


    async def update_products_status(
        self, db: AsyncSession, product_id: uuid.UUID, **kwargs
    )->Any:
        statuses = (
            await db.execute(
                select(
                    ProductTransferStatus
                )
                .filter(ProductTransferStatus.product_id == Products.id)
                .filter(ProductTransferStatus.product_id == product_id)
                .filter(ProductTransferStatus.transfer_status == kwargs.get("from_status"))
            )
        ).scalars().all()

        status_list = []
        for status in statuses:
            status.transfer_status = kwargs.get("to_status")
            status_list.append(status)
        db.add_all(status_list)
        await db.commit()
        return status_list

    async def update_product_owner(
        self, db: AsyncSession, db_obj: Products, **kwargs
    )->Any:
        updated_by = kwargs.get("updated_by")
        user = (await db.execute(
                select(User)
                .filter(User.id == updated_by)
            )
        ).scalars().first()
        if user.created_by:
            updated_by = user.created_by

        db_obj.updated_at = datetime.utcnow()
        db_obj.updated_by = updated_by
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: Products,
        obj_in: Union[ProductUpdate, Dict[str, Any]],
        **kwargs
    ) -> Products:
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
        self, db: AsyncSession, db_obj: Products, **kwargs
    ) -> Products:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)

        rfid = (
            await db.execute(
                select(Rfids)
                .filter(Rfids.item_id == db_obj.id)
                .filter(Rfids.item_type == rfid_type.PRODUCT)
                .filter(Rfids.deleted_at == None)
            )
        ).scalars().first()
        if rfid:
            rfid.deleted_at = datetime.utcnow()
            rfid.updated_by = kwargs.get("updated_by")
            db.add(rfid)
        await db.commit()
        return 


product = CRUDProduct(Products)