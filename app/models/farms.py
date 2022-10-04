from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime, DECIMAL, Text
from sqlalchemy import func
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class Farms(Base):
    __tablename__ = "farms"

    id = Column(GUID, primary_key=True)
    name = Column(String(255))
    user_id = Column(GUID, ForeignKey("users.id"))
    description = Column(Text)
    area = Column(DECIMAL(10, 2))
    code = Column(String(255))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))
