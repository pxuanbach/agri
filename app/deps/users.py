from typing import Any, List, Optional, Union

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, Request, Response, BackgroundTasks
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.constants import (
    role_key, 
    # member_status_constants, 
)
from app.core.exceptions import UserNotExists
from app.db import SessionLocal
from app.deps.db import get_async_session, get_db
from app.models.users import User as UserModel
from app.models.role import Role
from app.schemas.users import User, UserCreate, UserDB, UserGetMe, UserUpdate
from app.core.firebase import _firebase


bearer_transport = BearerTransport(tokenUrl=f"{settings.API_PATH}/auth/jwt/login")


ALLOW_REGISTER_roleS = [
    role_key.OWNER,
    role_key.CUSTOMER,
]

ALLOW_APP_LOGIN_keyS = [
    role_key.ADMIN,
    role_key.OWNER,
    role_key.CUSTOMER,
]


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

class NormalAuthentication(AuthenticationBackend):
    async def logout(
        self,
        strategy: Strategy[models.UC, models.UD],
        user: models.UD,
        token: str,
        response: Response,
    ) -> Any:
        # # Remove firebase token
        # db = SessionLocal()
        # user_info = db.get(UserModel, user.id)
        # user_info.firebase_register_token = ""
        # db.add(user_info)
        # db.commit()
        # unsubscribe from firebase
        try:
            topics = get_topics_by_role(user)
            if user.firebase_register_token:
                _firebase.unsubscribe(
                    tokens=[user.firebase_register_token], 
                    topics=topics
                )
        except:
            pass
        # Remove firebase token
        db = SessionLocal()
        user_info = db.get(UserModel, user.id)
        user_info.firebase_register_token = ""
        db.add(user_info)
        db.commit()

        return {"success": True}


jwt_authentication = NormalAuthentication(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class MemberLoginAuthentication(AuthenticationBackend):
    async def login(
        self,
        strategy: Strategy[models.UC, models.UD],
        user: models.UD,
        response: Response
    ) -> Any:
        role = get_role_by_user(user)
        if role is None or role.key not in ALLOW_APP_LOGIN_keyS:
            raise HTTPException(
                status_code=403,
            )
        token = await strategy.write_token(user)
        return await self.transport.get_login_response(token, response)

def get_role_by_user(user: User) -> Role:
    db = SessionLocal()
    result = db.execute(select(Role).where(Role.id == user.role_id))
    role = result.scalars().first()

    return role

member_authentication = MemberLoginAuthentication(
    name="member_app_jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def validate_password(
        self, password: str, user: Union[UserCreate, User]
    ) -> None:
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password should be at least 8 characters",
            )
        if user.email in password:
            raise HTTPException(
                status_code=400,
                detail="Password should not contain e-mail",
            )
        # add validate user type here
        if not user.role_id:
            db = SessionLocal()
            result = db.execute(
                select(Role).where(Role.key == user.role_key)
            )
            role = result.scalars().first()

            if not role:
                raise HTTPException(
                    status_code=400,
                    detail="User role not exist",
                )
            else:
                if role.key not in ALLOW_REGISTER_roleS:
                    raise HTTPException(
                        status_code=403,
                        detail="Not allowed",
                    )
                user.role_id = role.id

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # print(f"User {user.email} has forgot their password. Reset token: {token}")
        # if settings.EMAILS_ENABLED and user:
        #     send_reset_password_email(
        #         email_to=user.email, email=user.email, token=token
        #     )
        return

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[models.UD]:
        """
        Authenticate and return a user following an email and a password.
        Will automatically upgrade password hash if necessary.
        :param credentials: The user credentials.
        """
        try:
            user = await self.get_by_email(credentials.username)
        except UserNotExists:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            self.password_helper.hash(credentials.password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        # Update password hash to a more robust one if needed
        if updated_password_hash is not None:
            user.hashed_password = updated_password_hash
            await self.user_db.update(user)
        db = SessionLocal()
        db.commit()
        return user

def get_topics_by_role(user: User) -> List[str]:
    db = SessionLocal()
    result = db.execute(
        select(
            Role.key
        )
        .filter(User.role_id == Role.id)
        .filter(User.id == user.id)
    )
    role = result.scalars().first()

    result_topics = []
    result_topics.append(f"user_{user.id}")
    result_topics.append(f"role_{role}")
            
    return result_topics


def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(UserDB, session, UserModel)


def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication, member_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


class AuthorizeCurrentUser:
    def __init__(self, roles) -> None:
        self.roles = roles

    async def __call__(
        self, 
        user: UserModel = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
    ):
        role: Role = await session.get(Role, user.role_id)
        if role.key not in self.roles:
            raise HTTPException(403, "The user doesn't have enough privileges.")
        return user


# async def authorize_current_user(
#     user: UserModel = Depends(current_user),
#     session: AsyncSession = Depends(get_async_session)
# ) -> UserModel:
#     if role.key in [role_key.ADMIN, role_key.OWNER]:
#         raise HTTPException(403, "The user doesn't have enough privileges.")
#     return user
