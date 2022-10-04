import uuid
from app.core.config import settings
from sqlalchemy.future import select
from app.deps.users import get_user_manager
from app.models.users import User
from app.models.role import Role
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from app.core.config import settings
from app.deps.users import get_user_manager
from app.models.users import User 
from app.schemas.users import UserCreate

engine = create_engine(
    settings.DATABASE_URL,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
session = SessionLocal()
session.rollback()
session.commit()

user_manager = next(get_user_manager())

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin"
OWNER_EMAIL = "owner@gmail.com"
OWNER_PASSWORD = "owner"
CUSTOMER_EMAIL = "customer@gmail.com"
CUSTOMER_PASSWORD = "customer"
SUB_CUSTOMER_EMAIL = "sub_customer@gmail.com"
SUB_CUSTOMER_PASSWORD = "customer"

ADMIN = "admin"
OWNER = "owner"
CUSTOMER = "customer"
SUB_CUSTOMER = "sub_customer"

# admin 
result = session.execute(select(User).where(User.email == ADMIN_EMAIL))
user = result.scalars().first()
if not user:
    role = (session.execute(select(Role).where(Role.key == ADMIN))).scalars().first()
    user_in = User(
        id=uuid.uuid4(),
        email = ADMIN_EMAIL,
        hashed_password = user_manager.password_helper.hash(ADMIN_PASSWORD),
        role_id=role.id,
    )
    session.add(user_in)
    session.commit()
    admin_director = user_in.id
    print("Create admin success")
else:
    admin_director = user.id
    print("admin existed")

# owner
result = session.execute(select(User).where(User.email == OWNER_EMAIL))
user = result.scalars().first()
if not user:
    role = (session.execute(select(Role).where(Role.key == OWNER))).scalars().first()
    user_in = User(
        id=uuid.uuid4(),
        email = OWNER_EMAIL,
        hashed_password = user_manager.password_helper.hash(OWNER_PASSWORD),
        role_id=role.id,
    )
    session.add(user_in)
    session.commit()
    print("Create owner success")
else:
    print("owner existed")
    
# CUSTOMER
result = session.execute(select(User).where(User.email == CUSTOMER_EMAIL))
user = result.scalars().first()
if not user:
    role = (session.execute(select(Role).where(Role.key == CUSTOMER))).scalars().first()
    user_in = User(
        id=uuid.uuid4(),
        email = CUSTOMER_EMAIL,
        hashed_password = user_manager.password_helper.hash(CUSTOMER_PASSWORD),
        role_id=role.id,
    )
    print(user)
    session.add(user_in)
    session.commit()
    print("Create customer success")
else:
    print("customer existed")

# SUB CUSTOMER
result = session.execute(select(User).where(User.email == CUSTOMER_EMAIL))
parent = result.scalars().first()
result = session.execute(select(User).where(User.email == SUB_CUSTOMER_EMAIL))
user = result.scalars().first()
if not user:
    role = (session.execute(select(Role).where(Role.key == CUSTOMER))).scalars().first()
    user_in = User(
        id=uuid.uuid4(),
        email = SUB_CUSTOMER_EMAIL,
        hashed_password = user_manager.password_helper.hash(SUB_CUSTOMER_PASSWORD),
        role_id=role.id,
        created_by=parent.id,
    )
    print(user)
    session.add(user_in)
    session.commit()
    print("Create customer success")
else:
    print("customer existed")