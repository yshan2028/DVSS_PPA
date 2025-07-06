"""
用户数据访问对象 (DAO)
Data Access Object - 处理用户相关的数据库操作
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from module_dvss.entity.do.user_do import SysUser
from module_dvss.entity.do.role_do import SysRole
from utils.log_util import LogUtil

logger = LogUtil.get_logger("user_dao")


class UserDao:
    """用户数据访问对象"""
    
    @staticmethod
    async def select_user_list(db: AsyncSession, query_db: SysUser, page_obj: Dict[str, Any]) -> List[SysUser]:
        """
        获取用户列表
        
        Args:
            db: 数据库会话
            query_db: 查询条件对象
            page_obj: 分页参数
            
        Returns:
            List[SysUser]: 用户列表
        """
        try:
            stmt = select(SysUser).options(selectinload(SysUser.roles))
            
            # 构建查询条件
            conditions = []
            if query_db.username:
                conditions.append(SysUser.username.like(f"%{query_db.username}%"))
            if query_db.email:
                conditions.append(SysUser.email.like(f"%{query_db.email}%"))
            if query_db.phone:
                conditions.append(SysUser.phone.like(f"%{query_db.phone}%"))
            if query_db.status is not None:
                conditions.append(SysUser.status == query_db.status)
            if query_db.user_type is not None:
                conditions.append(SysUser.user_type == query_db.user_type)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # 排序
            stmt = stmt.order_by(SysUser.created_at.desc())
            
            # 分页
            if page_obj.get("page") and page_obj.get("size"):
                offset = (page_obj["page"] - 1) * page_obj["size"]
                stmt = stmt.offset(offset).limit(page_obj["size"])
            
            result = await db.execute(stmt)
            return result.scalars().all()
        
        except Exception as e:
            logger.error(f"查询用户列表失败: {str(e)}")
            raise e
    
    @staticmethod
    async def count_user_list(db: AsyncSession, query_db: SysUser) -> int:
        """
        统计用户数量
        
        Args:
            db: 数据库会话
            query_db: 查询条件对象
            
        Returns:
            int: 用户总数
        """
        try:
            stmt = select(func.count(SysUser.id))
            
            # 构建查询条件
            conditions = []
            if query_db.username:
                conditions.append(SysUser.username.like(f"%{query_db.username}%"))
            if query_db.email:
                conditions.append(SysUser.email.like(f"%{query_db.email}%"))
            if query_db.phone:
                conditions.append(SysUser.phone.like(f"%{query_db.phone}%"))
            if query_db.status is not None:
                conditions.append(SysUser.status == query_db.status)
            if query_db.user_type is not None:
                conditions.append(SysUser.user_type == query_db.user_type)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await db.execute(stmt)
            return result.scalar() or 0
        
        except Exception as e:
            logger.error(f"统计用户数量失败: {str(e)}")
            raise e
                    raise ConflictError("邮箱已存在")
            
            # 创建用户对象
            user = DvssUser(**user_data)
            
            # 添加到会话
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created successfully: {user.username}")
            return user
            
        except (ConflictError, DatabaseError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise DatabaseError(f"创建用户失败: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> Optional[DvssUser]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[DvssUser]: 用户对象或None
        """
        try:
            return self.db.query(DvssUser).filter(DvssUser.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            raise DatabaseError(f"获取用户失败: {str(e)}")
    
    def get_user_by_username(self, username: str) -> Optional[DvssUser]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[DvssUser]: 用户对象或None
        """
        try:
            return self.db.query(DvssUser).filter(DvssUser.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise DatabaseError(f"获取用户失败: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[DvssUser]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            Optional[DvssUser]: 用户对象或None
        """
        try:
            return self.db.query(DvssUser).filter(DvssUser.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise DatabaseError(f"获取用户失败: {str(e)}")
    
    def update_user(self, user_id: int, update_data: dict) -> DvssUser:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_data: 更新数据
            
        Returns:
            DvssUser: 更新后的用户对象
            
        Raises:
            NotFoundError: 用户不存在
            DatabaseError: 数据库操作失败
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            
            user.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User updated successfully: {user.username}")
            return user
            
        except (NotFoundError, DatabaseError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user {user_id}: {e}")
            raise DatabaseError(f"更新用户失败: {str(e)}")
    
    def get_all_users(self) -> List[DvssUser]:
        """获取所有用户"""
        try:
            return self.db.query(DvssUser).filter(
                DvssUser.status != UserStatus.DELETED
            ).all()
        except Exception as e:
            logger.error(f"Get all users error: {e}")
            raise DatabaseError(f"获取用户列表失败: {str(e)}")
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.status = UserStatus.DELETED
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete user error: {e}")
            raise DatabaseError(f"删除用户失败: {str(e)}")
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """更新用户密码"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.password_hash = password_hash
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update password error: {e}")
            raise DatabaseError(f"更新密码失败: {str(e)}")
    
    def list_users(self, page: int = 1, page_size: int = 20, 
                   filters: Optional[dict] = None) -> Tuple[List[DvssUser], int, int, int]:
        """
        分页获取用户列表
        
        Args:
            page: 页码
            page_size: 每页大小
            filters: 过滤条件
            
        Returns:
            Tuple[List[DvssUser], int, int, int]: (用户列表, 总数, 页码, 每页大小)
        """
        try:
            query = self.db.query(DvssUser).filter(DvssUser.status != UserStatus.DELETED)
            
            # 应用过滤条件
            if filters:
                if filters.get('keyword'):
                    keyword = f"%{filters['keyword']}%"
                    query = query.filter(
                        or_(
                            DvssUser.username.ilike(keyword),
                            DvssUser.email.ilike(keyword),
                            DvssUser.full_name.ilike(keyword),
                            DvssUser.organization.ilike(keyword)
                        )
                    )
                
                if filters.get('role'):
                    query = query.filter(DvssUser.role == filters['role'])
                
                if filters.get('status'):
                    query = query.filter(DvssUser.status == filters['status'])
                
                if filters.get('organization'):
                    query = query.filter(DvssUser.organization == filters['organization'])
                
                if filters.get('department'):
                    query = query.filter(DvssUser.department == filters['department'])
            
            # 排序
            query = query.order_by(desc(DvssUser.created_at))
            
            # 分页
            return PageUtil.paginate(query, page, page_size)
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise DatabaseError(f"获取用户列表失败: {str(e)}")
    
    def update_last_login(self, user_id: int) -> bool:
        """
        更新最后登录时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 更新成功返回True
        """
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.last_login = datetime.now()
                user.login_attempts = 0  # 重置登录尝试次数
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating last login for user {user_id}: {e}")
            return False
    
    def increment_login_attempts(self, user_id: int) -> int:
        """
        增加登录尝试次数
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 当前登录尝试次数
        """
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.login_attempts = (user.login_attempts or 0) + 1
                
                # 如果登录尝试次数过多，锁定账户
                if user.login_attempts >= 5:
                    user.account_locked_until = datetime.now() + timedelta(minutes=30)
                
                self.db.commit()
                return user.login_attempts
            return 0
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing login attempts for user {user_id}: {e}")
            return 0
    
    def is_account_locked(self, user_id: int) -> bool:
        """
        检查账户是否被锁定
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 账户是否被锁定
        """
        try:
            user = self.get_user_by_id(user_id)
            if user and user.account_locked_until:
                if user.account_locked_until > datetime.now():
                    return True
                else:
                    # 锁定时间已过，清除锁定
                    user.account_locked_until = None
                    user.login_attempts = 0
                    self.db.commit()
            return False
            
        except Exception as e:
            logger.error(f"Error checking account lock for user {user_id}: {e}")
            return False
    
    def get_user_stats(self) -> dict:
        """
        获取用户统计信息
        
        Returns:
            dict: 统计信息
        """
        try:
            total_users = self.db.query(DvssUser).filter(DvssUser.status != UserStatus.DELETED).count()
            active_users = self.db.query(DvssUser).filter(DvssUser.status == UserStatus.ACTIVE).count()
            inactive_users = self.db.query(DvssUser).filter(DvssUser.status == UserStatus.INACTIVE).count()
            admin_users = self.db.query(DvssUser).filter(DvssUser.role == UserRole.ADMIN).count()
            
            # 本月新增用户
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_users_this_month = self.db.query(DvssUser).filter(
                and_(
                    DvssUser.created_at >= start_of_month,
                    DvssUser.status != UserStatus.DELETED
                )
            ).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "admin_users": admin_users,
                "regular_users": total_users - admin_users,
                "new_users_this_month": new_users_this_month
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise DatabaseError(f"获取用户统计失败: {str(e)}")
