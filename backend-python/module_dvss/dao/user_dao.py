"""
用户数据访问层 (DAO)
"""

from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from module_dvss.entity.user import User
from utils.log_util import LogUtil

logger = LogUtil.get_logger('user_dao')


class UserDAO:
    """用户数据访问对象"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        """创建用户"""
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error creating user: {str(e)}')
            raise

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        try:
            stmt = select(User).options(selectinload(User.role)).where(User.id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting user by id {user_id}: {str(e)}')
            raise

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        try:
            stmt = select(User).options(selectinload(User.role)).where(User.username == username)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting user by username {username}: {str(e)}')
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            stmt = select(User).options(selectinload(User.role)).where(User.email == email)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting user by email {email}: {str(e)}')
            raise

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        username: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """分页获取用户列表"""
        try:
            # 构建查询条件
            conditions = []
            if username:
                conditions.append(User.username.ilike(f'%{username}%'))
            if email:
                conditions.append(User.email.ilike(f'%{email}%'))
            if is_active is not None:
                conditions.append(User.is_active == is_active)

            # 构建基础查询
            base_stmt = select(User).options(selectinload(User.role))
            if conditions:
                base_stmt = base_stmt.where(and_(*conditions))

            # 获取总数
            count_stmt = select(func.count(User.id))
            if conditions:
                count_stmt = count_stmt.where(and_(*conditions))

            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 分页查询
            offset = (page - 1) * page_size
            stmt = base_stmt.offset(offset).limit(page_size).order_by(User.id.desc())

            result = await self.db.execute(stmt)
            users = result.scalars().all()

            return list(users), total

        except Exception as e:
            logger.error(f'Error getting paginated users: {str(e)}')
            raise

    async def update(self, user: User) -> User:
        """更新用户"""
        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error updating user {user.id}: {str(e)}')
            raise

    async def delete(self, user_id: int) -> bool:
        """删除用户"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                await self.db.delete(user)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error deleting user {user_id}: {str(e)}')
            raise

    async def get_all(self, is_active: Optional[bool] = None) -> List[User]:
        """获取所有用户"""
        try:
            stmt = select(User).options(selectinload(User.role))
            if is_active is not None:
                stmt = stmt.where(User.is_active == is_active)

            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f'Error getting all users: {str(e)}')
            raise

    async def get_total_count(self) -> int:
        """获取用户总数"""
        try:
            stmt = select(func.count(User.id))
            result = await self.db.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f'Error getting user count: {str(e)}')
            raise
