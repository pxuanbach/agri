from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid
from sqlalchemy import select, or_, func, tuple_
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.crud.base import CRUDBase
from app.models.product_history import ProductHistory
from app.schemas.transfer import (
    ProductHistoryCreate,
    ProductHistoryUpdate
)
from app.models.users import User
from app.models.products import Products


class CRUDProductHistory(CRUDBase[ProductHistory, ProductHistoryCreate, ProductHistoryUpdate]):
    async def get(
        self, db: AsyncSession, id: uuid.UUID
    ) -> Optional[ProductHistory]:
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
    ) -> List[ProductHistory]:
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

    async def total_product_histories_by_product(self, db: AsyncSession, request_params
    ) -> Any:
        buyer = aliased(User, name='buyer')
        seller = aliased(User, name='seller')
        query = (
                select(func.count(ProductHistory.id))
                .filter(buyer.id == ProductHistory.transfer_to_user_id)
                .filter(seller.id == ProductHistory.transfer_from_user_id)
                .filter(Products.id == ProductHistory.product_id)
                .filter(ProductHistory.deleted_at == None)
            )
        query = await self.add_filter_to_list_product_histories(query, request_params)
        total = await db.scalar(query)
        return total

    async def list_product_histories_by_product(self, db: AsyncSession, request_params
    ) -> Any:
        buyer = aliased(User, name='buyer')
        seller = aliased(User, name='seller')
        query = (
                select(
                    ProductHistory,
                    buyer.name.label('buyer_name'),
                    buyer.address.label('buyer_address'),
                    buyer.email.label('buyer_email'),
                    buyer.dob.label('buyer_dob'),
                    buyer.avatar_id.label('buyer_avatar_id'),
                    buyer.created_by.label('buyer_created_by'),
                    seller.name.label('seller_name'),
                    seller.address.label('seller_address'),
                    seller.email.label('seller_email'),
                    seller.dob.label('seller_dob'),
                    seller.avatar_id.label('seller_avatar_id'),
                    seller.created_by.label('seller_created_by'),
                )
                .offset(request_params.skip)
                .limit(request_params.limit)
                .order_by(request_params.order_by)
                .filter(buyer.id == ProductHistory.transfer_to_user_id)
                .filter(seller.id == ProductHistory.transfer_from_user_id)
                .filter(Products.id == ProductHistory.product_id)
                .filter(ProductHistory.deleted_at == None)
            )
        query = await self.add_filter_to_list_product_histories(query, request_params)
        product_history = (await db.execute(query)).all()
        return product_history

    async def add_filter_to_list_product_histories(
        self, query, request_params
    )->Any:
        if request_params.product_id:
            query = query.filter(
                ProductHistory.product_id == request_params.product_id
            )
        return query

    async def create(
        self, db: AsyncSession, obj_in: ProductHistoryCreate, user_id: uuid.UUID
    ) -> ProductHistory:
        db_obj = self.model(**obj_in.dict(), id=uuid.uuid4(), updated_by = user_id) 
        db.add(db_obj)
        await db.commit()
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ProductHistory,
        obj_in: Union[ProductHistoryUpdate, Dict[str, Any]],
        **kwargs
    ) -> ProductHistory:
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
        self, db: AsyncSession, db_obj: ProductHistory, **kwargs
    ) -> ProductHistory:
        db_obj.deleted_at = datetime.utcnow()
        db_obj.updated_by = kwargs.get("updated_by")
        db.add(db_obj)
        await db.commit()
        return 


product_history = CRUDProductHistory(ProductHistory)