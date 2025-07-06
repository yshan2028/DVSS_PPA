"""
用户服务层
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import secrets
import string

from module_dvss.entity.user import User
from module_dvss.entity.role import Role
from module_dvss.schemas.user_schema import UserCreate, UserUpdate
from module_dvss.dao.user_dao import UserDAO
from core.security import get_password_hash, verify_password
from utils.log_util import LogUtil

logger = LogUtil.get_logger("user_service")


class UserService:
    """用户服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_dao = UserDAO(db)
    
    async def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        try:
            # 创建用户实体
            user = User(
                username=user_data.username,
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                phone=user_data.phone,
                role_id=user_data.role_id,
                is_active=user_data.is_active if user_data.is_active is not None else True,
                is_superuser=user_data.is_superuser if user_data.is_superuser is not None else False
            )
            
            return await self.user_dao.create(user)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return await self.user_dao.get_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return await self.user_dao.get_by_username(username)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return await self.user_dao.get_by_email(email)
    
    async def get_users_paginated(
        self, 
        page: int = 1, 
        page_size: int = 20,
        username: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """分页获取用户列表"""
        return await self.user_dao.get_paginated(
            page=page,
            page_size=page_size,
            username=username,
            email=email,
            is_active=is_active
        )
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户"""
        try:
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 更新字段
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            return await self.user_dao.update(user)
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            return await self.user_dao.delete(user_id)
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise
    
    async def update_user_status(self, user_id: int, is_active: bool) -> User:
        """更新用户状态"""
        try:
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            user.is_active = is_active
            return await self.user_dao.update(user)
            
        except Exception as e:
            logger.error(f"Error updating user status {user_id}: {str(e)}")
            raise
    
    async def reset_password(self, user_id: int) -> str:
        """重置用户密码"""
        try:
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            # 生成临时密码
            temp_password = self._generate_temp_password()
            user.password_hash = get_password_hash(temp_password)
            
            await self.user_dao.update(user)
            return temp_password
            
        except Exception as e:
            logger.error(f"Error resetting password for user {user_id}: {str(e)}")
            raise
    
    async def change_password(self, user_id: int, new_password: str) -> bool:
        """修改用户密码"""
        try:
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                raise ValueError("用户不存在")
            
            user.password_hash = get_password_hash(new_password)
            await self.user_dao.update(user)
            return True
            
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {str(e)}")
            raise
    
    async def verify_password(self, user_id: int, password: str) -> bool:
        """验证用户密码"""
        try:
            user = await self.user_dao.get_by_id(user_id)
            if not user:
                return False
            
            return verify_password(password, user.password_hash)
            
        except Exception as e:
            logger.error(f"Error verifying password for user {user_id}: {str(e)}")
            return False
    
    def _generate_temp_password(self, length: int = 12) -> str:
        """生成临时密码"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
