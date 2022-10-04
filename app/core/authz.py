# import resource
# from typing import Any
# from fastapi import Depends, HTTPException
# from app.deps.users import current_user
# from app.models.user import User
# from app.deps.db import get_async_session
# from sqlalchemy.ext.asyncio.session import AsyncSession

# class Authz:
#     def __init__(self, permisson):
#         self.user = None
#         self.permisson = permisson

#     async def __call__(self, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
#         self.user = user
#         role_id = self.user.user_type_id
#         # if self.user.role not in self.permissions and self.permissions:
#         #     raise HTTPException(status_code=403,
#         #                         detail=f'Permission not granted')

