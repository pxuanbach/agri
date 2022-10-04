from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.sql.functions import func
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class FarmTrees(Base):
    __tablename__ = "farm_trees"

    id = Column(GUID, primary_key=True)
    farm_id = Column(GUID, ForeignKey("farms.id"))
    tree_id = Column(GUID, ForeignKey("trees.id"))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))