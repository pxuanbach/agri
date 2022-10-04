import uuid
from pydantic import BaseModel


class FarmTree(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    tree_id: uuid.UUID
    updated_by: uuid.UUID

    class Config:
        orm_mode = True