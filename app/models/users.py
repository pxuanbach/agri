from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import String, Text
from fastapi_users_db_sqlalchemy import GUID
from app.db import Base


class User(Base, SQLAlchemyBaseUserTable):
    __tablename__ = "users"

    role_id = Column(GUID, ForeignKey("role.id"))
    name = Column(String(255))
    dob = Column(DateTime(timezone=True))
    address = Column(String(255))
    firebase_register_token = Column(Text)
    created_by = Column(GUID, ForeignKey("users.id"))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    avatar_id = Column(GUID, ForeignKey("resource.id"))
    updated_by = Column(GUID, ForeignKey("users.id"))