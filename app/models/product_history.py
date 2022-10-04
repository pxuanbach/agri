from sqlalchemy.sql.sqltypes import String, DECIMAL
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.sql.functions import func
from app.db import Base


class ProductHistory(Base):
    __tablename__ = "product_history"

    id = Column(GUID, primary_key=True)
    product_id = Column(GUID, ForeignKey("products.id"))
    transfer_from_user_id = Column(GUID, ForeignKey("users.id"))
    transfer_to_user_id = Column(GUID, ForeignKey("users.id"))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))