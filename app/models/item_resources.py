from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.sql.functions import func
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class ItemResources(Base):
    __tablename__ = "item_resources"

    id = Column(GUID, primary_key=True)
    item_type = Column(String(255))
    item_id = Column(GUID)
    resource_id = Column(GUID, ForeignKey("resource.id"))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))