from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import String
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class Rfids(Base):
    __tablename__ = "rfids"

    id = Column(GUID, primary_key=True)
    code = Column(String(255), unique=True)
    item_id = Column(GUID)
    item_type = Column(String(255))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))