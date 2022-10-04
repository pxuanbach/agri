from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime, Text
from sqlalchemy import func
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class TransferStatus(Base):
    __tablename__ = "transfer_status"

    id = Column(GUID, primary_key=True)
    name = Column(String(255))
    description = Column(Text)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))
