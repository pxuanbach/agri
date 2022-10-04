from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import String, Text
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class Categories(Base):
    __tablename__ = "categories"

    id = Column(GUID, primary_key=True)
    name = Column(String(255), unique=True)
    description = Column(Text)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))