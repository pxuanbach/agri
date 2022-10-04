from datetime import datetime
from typing import Any, List
import uuid
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.crud.base import CRUDBase
from app.models.farm_fertilizers import FarmFertilizers
from app.models.farm_trees import FarmTrees
from app.models.farms import Farms
from app.models.fertilizers import Fertilizers
from app.models.rfids import Rfids
from app.models.trees import Trees
from app.models.resource import Resource
from app.schemas.farms import FarmCreate, FarmUpdate
from app.models.users import User
from app.schemas.item_resources import ItemResource as ItemResourceSchema
from app.models.item_resources import ItemResources
from app.schemas.farm_fertilizers import FarmFertilizer as FarmFertilizerSchema
from app.schemas.farm_trees import FarmTree as FarmTreeSchema
from app.core.constants import resource_type, rfid_type
from app.utils.random import random_string_and_number

class CRUDFarm(CRUDBase[Farms, FarmCreate, FarmUpdate]):

    async def get_only_farm_by_id(self, db: AsyncSession, farm_id: uuid.UUID
    ) -> Any:
        farm = (
            await db.execute(
                select(Farms)
                .filter(Farms.id == farm_id)
                .filter(Farms.deleted_at == None)
            )
        ).scalars().first()
        return farm

    async def get_farm_by_id(self, db: AsyncSession, farm_id: uuid.UUID
    ) -> Any:
        fertilizers = func.array_agg(
            func.distinct(Fertilizers.id.label("id"), Fertilizers.name.label("name"))
        ).label("fertilizers")
        trees = func.array_agg(
            func.distinct(Trees.id.label("id"), Trees.name.label("name"))
        ).label("trees")
        farm = (
            await db.execute(
                select(
                    Farms,
                    fertilizers,
                    trees,
                    Rfids
                )
                .filter(Farms.id == farm_id)
                .filter(Farms.deleted_at == None)
                .outerjoin(FarmFertilizers, and_(
                    FarmFertilizers.farm_id == Farms.id,
                    FarmFertilizers.deleted_at == None
                    )
                )
                .outerjoin(Fertilizers, and_(
                    FarmFertilizers.fertilizer_id == Fertilizers.id,
                    Fertilizers.deleted_at == None
                    )
                )
                .outerjoin(FarmTrees, and_(
                    FarmTrees.farm_id == Farms.id,
                    FarmTrees.deleted_at == None
                )
                )
                .outerjoin(Trees, and_(
                    FarmTrees.tree_id == Trees.id,
                    Trees.deleted_at == None
                    )
                )
                .outerjoin(Rfids, and_(
                    Rfids.item_type == rfid_type.FARM,
                    Rfids.item_id == Farms.id,
                    Rfids.deleted_at == None
                    )
                )
                .group_by(Farms.id)
                .group_by(Rfids.id)
            )
        ).first()

        return farm

    async def get_all_farms(self, db: AsyncSession
    ) -> Any:
        fertilizers = func.array_agg(
            func.distinct(Fertilizers.id.label("id"), Fertilizers.name.label("name"))
        ).label("fertilizers")
        trees = func.array_agg(
            func.distinct(Trees.id.label("id"), Trees.name.label("name"))
        ).label("trees")
        farms = (
            await db.execute(
                select(
                    Farms,
                    fertilizers,
                    trees,
                    Rfids
                )
                .filter(Farms.deleted_at == None)
                .outerjoin(FarmFertilizers, and_(
                    FarmFertilizers.farm_id == Farms.id,
                    FarmFertilizers.deleted_at == None
                    )
                )
                .outerjoin(Fertilizers, and_(
                    FarmFertilizers.fertilizer_id == Fertilizers.id,
                    Fertilizers.deleted_at == None
                    )
                )
                .outerjoin(FarmTrees, and_(
                    FarmTrees.farm_id == Farms.id,
                    FarmTrees.deleted_at == None
                )
                )
                .outerjoin(Trees, and_(
                    FarmTrees.tree_id == Trees.id,
                    Trees.deleted_at == None
                    )
                )
                .outerjoin(Rfids, and_(
                    Rfids.item_type == rfid_type.FARM,
                    Rfids.item_id == Farms.id,
                    Rfids.deleted_at == None
                    )
                )
                .group_by(Farms.id)
                .group_by(Rfids.id)
            )
        ).all()

        return farms

    async def get_farms_by_user_id(self, db: AsyncSession, user_id: uuid.UUID
    ) -> Any:
        fertilizers = func.array_agg(
            func.distinct(Fertilizers.id.label("id"), Fertilizers.name.label("name"))
        ).label("fertilizers")
        trees = func.array_agg(
            func.distinct(Trees.id.label("id"), Trees.name.label("name"))
        ).label("trees")
        farms = (
            await db.execute(
                select(
                    Farms,
                    fertilizers,
                    trees,
                    Rfids
                )
                .filter(Farms.user_id == user_id)
                .filter(Farms.deleted_at == None)
                .outerjoin(FarmFertilizers, and_(
                    FarmFertilizers.farm_id == Farms.id,
                    FarmFertilizers.deleted_at == None
                    )
                )
                .outerjoin(Fertilizers, and_(
                    FarmFertilizers.fertilizer_id == Fertilizers.id,
                    Fertilizers.deleted_at == None
                    )
                )
                .outerjoin(FarmTrees, and_(
                    FarmTrees.farm_id == Farms.id,
                    FarmTrees.deleted_at == None
                )
                )
                .outerjoin(Trees, and_(
                    FarmTrees.tree_id == Trees.id,
                    Trees.deleted_at == None
                    )
                )
                .outerjoin(Rfids, and_(
                    Rfids.item_type == rfid_type.FARM,
                    Rfids.item_id == Farms.id,
                    Rfids.deleted_at == None
                    )
                )
                .group_by(Farms.id)
                .group_by(Rfids.id)
            )
        ).all()

        return farms

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

    async def create(self, db: AsyncSession, farm_in: FarmCreate, user_id: uuid.UUID
    ) -> Farms:
        #create farm
        new_farm = Farms(
            id = uuid.uuid4(),
            name = farm_in.name,
            user_id = user_id,
            area = farm_in.area,
            description = farm_in.description,
            updated_by = user_id
        )
        db.add(new_farm)
        await db.commit()

        rfid = Rfids(
            id = uuid.uuid4(),
            item_id = new_farm.id,
            item_type = rfid_type.FARM,
            code = await self.unique_code(db),
            updated_by = user_id
        )
        db.add(rfid)

        await db.commit()
        return new_farm

    async def update_farm_fertilizer(
        self, db: AsyncSession, farm_id: uuid.UUID, fertilizers: List[uuid.UUID], user_id: uuid.UUID
    )->Any:
        farm_fertilizers = (
            await db.execute(
                select(FarmFertilizers)
                .filter(FarmFertilizers.farm_id == Farms.id)
                .filter(Farms.id == farm_id)
                .filter(FarmFertilizers.deleted_at == None)
            )
        ).scalars().all()
        for farm_fertilizer in farm_fertilizers:
            farm_fertilizer.deleted_at = datetime.utcnow()
            db.add(farm_fertilizer)
        await db.commit()

        farm_fertilizers: List[FarmFertilizerSchema] = list()
        for fertilizer in fertilizers:
            farm_fertilizers.append(
                FarmFertilizers(
                    id = uuid.uuid4(),
                    farm_id = farm_id,
                    fertilizer_id = fertilizer,
                    updated_by = user_id,
                )
            )
        db.add_all(farm_fertilizers)
        await db.commit()

        return farm_fertilizers

    async def update_farm_tree(
        self, db: AsyncSession, farm_id: uuid.UUID, trees: List[uuid.UUID], user_id: uuid.UUID
    )->Any:
        farm_trees = (
            await db.execute(
                select(FarmTrees)
                .filter(FarmTrees.farm_id == Farms.id)
                .filter(Farms.id == farm_id)
                .filter(FarmTrees.deleted_at == None)
            )
        ).scalars().all()
        for farm_tree in farm_trees:
            farm_tree.deleted_at = datetime.utcnow()
            db.add(farm_tree)
        await db.commit()

        farm_trees: List[FarmTreeSchema] = list()
        for tree in trees:
            farm_trees.append(
                FarmTrees(
                    id = uuid.uuid4(),
                    farm_id = farm_id,
                    tree_id = tree,
                    updated_by = user_id,
                )
            )
        db.add_all(farm_trees)
        await db.commit()

        return farm_trees

    async def update_farm(
        self, db: AsyncSession, farm_in: Farms, user_id: uuid.UUID
    )->Any:
        farm_in.updated_by = user_id
        db.add(farm_in)
        await db.commit()
        return farm_in

    async def delete_farm_relationship(
        self, db: AsyncSession, farm_id: uuid.UUID, user_id: uuid.UUID
    )->Any:
        rfid = (
            await db.execute(
                select(Rfids)
                .filter(Rfids.item_id == Farms.id)
                .filter(Rfids.item_type == rfid_type.FARM)
                .filter(FarmTrees.deleted_at == None)
            )
        ).scalars().first()
        if rfid:
            rfid.deleted_at = datetime.utcnow()
            rfid.updated_by = user_id
            db.add(rfid)

        farm_fertilizers = (
            await db.execute(
                select(FarmFertilizers)
                .filter(FarmFertilizers.farm_id == Farms.id)
                .filter(Farms.id == farm_id)
                .filter(FarmFertilizers.deleted_at == None)
            )
        ).scalars().all()
        for farm_fertilizer in farm_fertilizers:
            farm_fertilizer.updated_by = user_id
            farm_fertilizer.deleted_at = datetime.utcnow()
            db.add(farm_fertilizer)

        farm_trees = (
            await db.execute(
                select(FarmTrees)
                .filter(FarmTrees.farm_id == Farms.id)
                .filter(Farms.id == farm_id)
                .filter(FarmTrees.deleted_at == None)
            )
        ).scalars().all()
        for farm_tree in farm_trees:
            farm_tree.updated_by = user_id
            farm_tree.deleted_at = datetime.utcnow()
            db.add(farm_tree)

        await db.commit()
        return {"success": True}


farm = CRUDFarm(Farms)