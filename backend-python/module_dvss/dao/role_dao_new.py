"""
角色数据访问层 (DAO)
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload

from module_dvss.entity.role import Role, RoleFieldPermission
from utils.log_util import LogUtil

logger = LogUtil.get_logger("role_dao")


class RoleDAO:
    """角色数据访问对象"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, role: Role) -> Role:
        """创建角色"""
        try:
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating role: {str(e)}")
            raise
    
    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        try:
            stmt = select(Role).where(Role.id == role_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting role by id {role_id}: {str(e)}")
            raise
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """根据名称获取角色"""
        try:
            stmt = select(Role).where(Role.name == name)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting role by name {name}: {str(e)}")
            raise
    
    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        name: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        """分页获取角色列表"""
        try:
            # 构建查询条件
            conditions = []
            if name:
                conditions.append(Role.name.ilike(f"%{name}%"))
            if is_active is not None:
                conditions.append(Role.is_active == is_active)
            
            # 构建基础查询
            base_stmt = select(Role)
            if conditions:
                base_stmt = base_stmt.where(and_(*conditions))
            
            # 获取总数
            count_stmt = select(func.count(Role.id))
            if conditions:
                count_stmt = count_stmt.where(and_(*conditions))
            
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()
            
            # 分页查询
            offset = (page - 1) * page_size
            stmt = base_stmt.offset(offset).limit(page_size).order_by(Role.id.desc())
            
            result = await self.db.execute(stmt)
            roles = result.scalars().all()
            
            return list(roles), total
            
        except Exception as e:
            logger.error(f"Error getting paginated roles: {str(e)}")
            raise
    
    async def update(self, role: Role) -> Role:
        """更新角色"""
        try:
            await self.db.commit()
            await self.db.refresh(role)
            return role
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating role {role.id}: {str(e)}")
            raise
    
    async def delete(self, role_id: int) -> bool:
        """删除角色"""
        try:
            role = await self.get_by_id(role_id)
            if role:
                await self.db.delete(role)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting role {role_id}: {str(e)}")
            raise
    
    async def get_permissions(self, role_id: int) -> List[RoleFieldPermission]:
        """获取角色权限"""
        try:
            stmt = select(RoleFieldPermission).where(RoleFieldPermission.role_id == role_id)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting permissions for role {role_id}: {str(e)}")
            raise
    
    async def create_permissions(self, permissions: List[RoleFieldPermission]) -> List[RoleFieldPermission]:
        """批量创建角色权限"""
        try:
            self.db.add_all(permissions)
            await self.db.commit()
            for perm in permissions:
                await self.db.refresh(perm)
            return permissions
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating permissions: {str(e)}")
            raise
    
    async def delete_permissions(self, role_id: int) -> bool:
        """删除角色所有权限"""
        try:
            stmt = delete(RoleFieldPermission).where(RoleFieldPermission.role_id == role_id)
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting permissions for role {role_id}: {str(e)}")
            raise
    
    async def get_all(self, is_active: Optional[bool] = None) -> List[Role]:
        """获取所有角色"""
        try:
            stmt = select(Role)
            if is_active is not None:
                stmt = stmt.where(Role.is_active == is_active)
            
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all roles: {str(e)}")
            raise
