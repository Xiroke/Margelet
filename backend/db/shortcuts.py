from sqlalchemy.ext.asyncio import AsyncSession
from db.dao import PermissionManager
from db.models import Permission
from typing import List


async def get_all_permissions(session: AsyncSession) -> List[Permission]:
    """Get all permissions (Used for creator role)"""
    return await PermissionManager.get_all(session)
