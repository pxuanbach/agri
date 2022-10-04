from datetime import datetime
import uuid
from typing import Optional
from fastapi_users import models
from pydantic import BaseModel, EmailStr


class BaseUserField(models.BaseUser):
    role_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    dob: Optional[datetime] = None
    address: Optional[str] = None


class User(BaseUserField):
    class Config:
        orm_mode = True


class UserGetMe(BaseUserField):
    membership_plan: Optional[dict] = {}

    class Config:
        orm_mode = True


class UserCreate(User, models.BaseUserCreate):
    # role_id: uuid.UUID = None
    role_key: str


class UserUpdate(User, models.BaseUserUpdate):
    email: EmailStr = None


class UserDB(User, models.BaseUserDB):
    role_id: Optional[uuid.UUID]


class UserChagePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str
