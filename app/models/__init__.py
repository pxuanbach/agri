# Import all models here so alembic can discover them
from fastapi_users.db import SQLAlchemyBaseUserTable

from app.db import Base
from app.models.role import Role
from app.models.resource import Resource
from app.models.users import User
from app.models.farms import Farms
from app.models.categories import Categories
from app.models.products import Products
from app.models.fertilizers import Fertilizers
from app.models.trees import Trees
from app.models.farm_fertilizers import FarmFertilizers
from app.models.farm_trees import FarmTrees
from app.models.item_resources import ItemResources
from app.models.rfids import Rfids
from app.models.transfer_status import TransferStatus
from app.models.transfer_request import TransferRequests
from app.models.product_history import ProductHistory