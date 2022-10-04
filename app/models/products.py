from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, DateTime, Text, DECIMAL
from sqlalchemy import func
from fastapi_users_db_sqlalchemy import GUID


from app.db import Base


class Products(Base):
    __tablename__ = "products"

    id = Column(GUID, primary_key=True)
    category_id = Column(GUID, ForeignKey("categories.id"))
    farm_id = Column(GUID, ForeignKey("farms.id"))
    name = Column(String(255))
    code = Column(String(255))
    price_in_retail = Column(DECIMAL(10,2))
    status = Column(String(255))
    description = Column(Text)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    updated_by = Column(GUID, ForeignKey("users.id"))
