from datetime import datetime
import decimal
from pathlib import Path
from typing import List, Optional
import uuid
import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.resource import Resource


def remove_dot_in_path(value: str) -> str:
    if value.startswith("."):
        value = value.replace(".", "", 1)
    return value


async def upload_single_file(
    db: AsyncSession, file: UploadFile, updated_by: uuid.UUID
) -> Resource:
    """
    Upload Single File
    """
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    file_name = f"{ts}_{file.filename}"
    Path(f"{settings.STATIC_PATH}").mkdir(parents=True, exist_ok=True)
    destination_file_path = f"{settings.STATIC_PATH}/{file_name}"
    _size: decimal.Decimal = 0
    async with aiofiles.open(destination_file_path, 'wb') as out_file:
        while content := await file.read(1024):  # async read file chunk
            _size += (len(content)/1024)
            await out_file.write(content)  # async write file chunk

    resource = Resource(
        id=uuid.uuid4(),
        name=file_name,
        file_path=remove_dot_in_path(destination_file_path),
        file_type=file.content_type,
        file_size=_size,      # size of original file
        updated_by=updated_by,
    )
    db.add(resource)
    await db.commit()
    return resource


async def upload_multiple_file(
    db: AsyncSession, files: List[UploadFile], updated_by: uuid.UUID
) -> List[Resource]:
    """
    Upload Multiple File
    """
    resources = []
    for file in files:
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        file_name = f"{ts}_{file.filename}"
        Path(f"{settings.STATIC_PATH}").mkdir(parents=True, exist_ok=True)
        destination_file_path = f"{settings.STATIC_PATH}/{file_name}"
        _size: decimal.Decimal = 0
        async with aiofiles.open(destination_file_path, 'wb') as out_file:
            while content := await file.read(1024):  # async read file chunk
                _size += (len(content)/1024)
                await out_file.write(content)  # async write file chunk

        resource = Resource(
            id=uuid.uuid4(),
            name=file_name,
            file_path=remove_dot_in_path(destination_file_path),
            file_type=file.content_type,
            file_size=_size,      # size of original file
            updated_by=updated_by,
        )
        resources.append(resource)
    db.add_all(resources)
    await db.commit()
    return resources
