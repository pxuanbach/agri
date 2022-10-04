import uuid
from pydantic import BaseModel


class FarmFertilizer(BaseModel):
    id: uuid.UUID
    farm_id: uuid.UUID
    fertilizer_id: uuid.UUID
    updated_by: uuid.UUID

    class Config:
        orm_mode = True