from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DECIMAL, String, Text
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class Resource(Base):
    __tablename__ = "resource"

    id = Column(GUID, primary_key=True)
    name = Column(Text, unique=True)
    file_size = Column(DECIMAL(10,2))
    file_path = Column(Text)
    file_type = Column(String(255))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))