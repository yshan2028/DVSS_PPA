"""
角色服务层
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from module_dvss.entity.role import Role
from module_dvss.entity.order_field import RoleFieldPermission
from module_dvss.entity.user import User
from module_dvss.schemas.role_schema import RoleCreate, RoleUpdate, RolePermissionCreate
from module_dvss.dao.role_dao import RoleDAO
from utils.log_util import LogUtil

logger = LogUtil.get_logger("role_service")


class RoleService:
    """角色服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_dao = RoleDAO(db)
    
    async def create_role(self, role_data: RoleCreate) -> Role:
        """创建角色"""
        try:
            role = Role(
                name=role_data.name,
                description=role_data.description,
                is_active=role_data.is_active
            )
            
            return await self.role_dao.create(role)
            
        except Exception as e:
            logger.error(f"Error creating role: {str(e)}")
            raise
    
    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return await self.role_dao.get_by_id(role_id)
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        return await self.role_dao.get_by_name(name)
    
    async def get_roles_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        """分页获取角色列表"""
        return await self.role_dao.get_paginated(
            page=page,
            page_size=page_size,
            name=name,
            is_active=is_active
        )
    
    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        """更新角色"""
        try:
            role = await self.role_dao.get_by_id(role_id)
            if not role:
                raise ValueError("角色不存在")
            
            # 更新字段
            update_data = role_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(role, field):
                    setattr(role, field, value)
            
            return await self.role_dao.update(role)
            
        except Exception as e:
            logger.error(f"Error updating role {role_id}: {str(e)}")
            raise
    
    async def delete_role(self, role_id: int) -> bool:
        """删除角色"""
        try:
            return await self.role_dao.delete(role_id)
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {str(e)}")
            raise
    
    async def count_users_by_role(self, role_id: int) -> int:
        """统计使用此角色的用户数量"""
        try:
            stmt = select(func.count(User.id)).where(User.role_id == role_id)
            result = await self.db.execute(stmt)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error counting users by role {role_id}: {str(e)}")
            raise
    
    async def set_role_permissions(self, role_id: int, permissions: List[RolePermissionCreate]) -> List[RoleFieldPermission]:
        """设置角色字段权限"""
        try:
            # 删除现有权限
            await self.role_dao.delete_permissions(role_id)
            
            # 创建新权限
            new_permissions = []
            for perm_data in permissions:
                permission = RoleFieldPermission(
                    role_id=role_id,
                    field_id=perm_data.field_id,
                    can_view=perm_data.can_view,
                    can_decrypt=perm_data.can_decrypt
                )
                new_permissions.append(permission)
            
            return await self.role_dao.create_permissions(new_permissions)
            
        except Exception as e:
            logger.error(f"Error setting role permissions for role {role_id}: {str(e)}")
            raise
    
    async def get_role_permissions(self, role_id: int) -> List[RoleFieldPermission]:
        """获取角色权限"""
        return await self.role_dao.get_permissions(role_id)
