"""
用户服务层 (Service)
处理用户相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt

from module_dvss.dao.user_dao import UserDao
from module_dvss.entity.do.user_do import DvssUser, UserRole, UserStatus
from module_dvss.entity.vo.user_vo import (
    UserCreateRequest, UserUpdateRequest, UserPasswordChangeRequest,
    UserLoginRequest, UserLoginResponse, UserDetailResponse, 
    UserBaseResponse, UserListResponse, UserStatsResponse
)
from exceptions.custom_exception import (
    AuthenticationError, AuthorizationError, ValidationError, 
    NotFoundError, ConflictError, BusinessError
)
from utils.pwd_util import PwdUtil
from utils.log_util import LogUtil, audit_logger
from core.config import settings

logger = LogUtil.get_logger("user_service")

class UserService:
    """用户服务"""
    
    def __init__(self, db: Optional[Session] = None):
        from config.get_db import get_db
        if db is None:
            db = next(get_db())
        self.db = db
        self.user_dao = UserDao(db)
    
    def create_user(self, user_request: UserCreateRequest, creator_id: Optional[int] = None) -> UserDetailResponse:
        """
        创建用户
        
        Args:
            user_request: 用户创建请求
            creator_id: 创建者ID
            
        Returns:
            UserDetailResponse: 用户详细信息
            
        Raises:
            ValidationError: 数据验证失败
            ConflictError: 用户名或邮箱已存在
        """
        try:
            # 验证密码强度
            is_valid, message = PwdUtil.validate_password_strength(user_request.password)
            if not is_valid:
                raise ValidationError(message)
            
            # 检查用户名和邮箱是否已存在
            existing_user = self.user_dao.get_user_by_username(user_request.username)
            if existing_user:
                raise ConflictError("用户名已存在")
            
            existing_email = self.user_dao.get_user_by_email(user_request.email)
            if existing_email:
                raise ConflictError("邮箱已存在")
            
            # 准备用户数据
            user_data = user_request.dict(exclude={'password'})
            user_data['password_hash'] = PwdUtil.hash_password(user_request.password)
            user_data['created_by'] = creator_id
            user_data['status'] = UserStatus.ACTIVE
            
            # 创建用户
            user = self.user_dao.create_user(user_data)
            
            # 记录审计日志
            audit_logger.log_user_action("CREATE_USER", creator_id or 0, user.id, {
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            })
            
            logger.info(f"User created successfully: {user.username}")
            
            return UserDetailResponse.from_orm(user)
            
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise BusinessError(f"创建用户失败: {str(e)}")
    
    def authenticate_user(self, login_request: UserLoginRequest) -> UserLoginResponse:
        """
        用户认证登录
        
        Args:
            login_request: 登录请求
            
        Returns:
            UserLoginResponse: 登录响应
            
        Raises:
            AuthenticationError: 认证失败
        """
        try:
            # 获取用户
            user = self.user_dao.get_user_by_username(login_request.username)
            if not user:
                raise AuthenticationError("用户名或密码错误")
            
            # 检查账户状态
            if user.status != UserStatus.ACTIVE:
                raise AuthenticationError("账户已被禁用")
            
            # 检查账户是否被锁定
            if self.user_dao.is_account_locked(user.id):
                raise AuthenticationError("账户已被锁定，请稍后再试")
            
            # 验证密码
            if not PwdUtil.verify_password(login_request.password, user.password_hash):
                # 增加登录失败次数
                attempts = self.user_dao.increment_login_attempts(user.id)
                logger.warning(f"Login failed for user {user.username}, attempts: {attempts}")
                raise AuthenticationError("用户名或密码错误")
            
            # 更新最后登录时间
            self.user_dao.update_last_login(user.id)
            
            # 生成JWT令牌
            token_data = {
                "user_id": user.id,
                "username": user.username,
                "role": user.role.value,
                "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            }
            
            access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            
            # 记录安全日志
            LogUtil.log_security("USER_LOGIN", user.id, details=f"Login successful for {user.username}")
            
            # 记录审计日志
            audit_logger.log_user_action("LOGIN", user.id, user.id, {
                "login_time": datetime.now().isoformat()
            })
            
            logger.info(f"User authenticated successfully: {user.username}")
            
            return UserLoginResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_info=UserDetailResponse.from_orm(user)
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise AuthenticationError("登录失败")
    
    def authenticate_user(self, username: str, password: str) -> Optional[DvssUser]:
        """
        简单的用户认证方法 (用于登录)
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[DvssUser]: 认证成功返回用户对象，失败返回None
        """
        try:
            # 获取用户
            user = self.user_dao.get_user_by_username(username)
            if not user:
                return None
            
            # 检查账户状态
            if user.status != UserStatus.ACTIVE:
                return None
            
            # 验证密码
            if not PwdUtil.verify_password(password, user.password_hash):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[DvssUser]:
        """根据用户名获取用户"""
        return self.user_dao.get_user_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[DvssUser]:
        """根据邮箱获取用户"""  
        return self.user_dao.get_user_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[DvssUser]:
        """根据ID获取用户"""
        return self.user_dao.get_user_by_id(user_id)
    
    def get_user_by_id(self, user_id: int, requester_id: Optional[int] = None) -> UserDetailResponse:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            requester_id: 请求者ID
            
        Returns:
            UserDetailResponse: 用户详细信息
            
        Raises:
            NotFoundError: 用户不存在
            AuthorizationError: 权限不足
        """
        try:
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            
            # 权限检查：只有本人或管理员可以查看详细信息
            if requester_id and requester_id != user_id:
                requester = self.user_dao.get_user_by_id(requester_id)
                if not requester or requester.role != UserRole.ADMIN:
                    raise AuthorizationError("权限不足")
            
            return UserDetailResponse.from_orm(user)
            
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            raise BusinessError(f"获取用户失败: {str(e)}")
    
    def update_user(self, user_id: int, update_request: UserUpdateRequest, 
                   updater_id: Optional[int] = None) -> UserDetailResponse:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_request: 更新请求
            updater_id: 更新者ID
            
        Returns:
            UserDetailResponse: 更新后的用户信息
            
        Raises:
            NotFoundError: 用户不存在
            AuthorizationError: 权限不足
        """
        try:
            # 检查用户是否存在
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            
            # 权限检查：只有本人或管理员可以更新
            if updater_id and updater_id != user_id:
                updater = self.user_dao.get_user_by_id(updater_id)
                if not updater or updater.role != UserRole.ADMIN:
                    raise AuthorizationError("权限不足")
            
            # 准备更新数据
            update_data = update_request.dict(exclude_unset=True)
            update_data['updated_by'] = updater_id
            
            # 更新用户
            updated_user = self.user_dao.update_user(user_id, update_data)
            
            # 记录审计日志
            audit_logger.log_user_action("UPDATE_USER", updater_id or 0, user_id, update_data)
            
            logger.info(f"User updated successfully: {updated_user.username}")
            
            return UserDetailResponse.from_orm(updated_user)
            
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise BusinessError(f"更新用户失败: {str(e)}")
    
    def change_password(self, user_id: int, password_request: UserPasswordChangeRequest) -> bool:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            password_request: 密码修改请求
            
        Returns:
            bool: 修改成功返回True
            
        Raises:
            NotFoundError: 用户不存在
            AuthenticationError: 旧密码错误
            ValidationError: 新密码不符合要求
        """
        try:
            # 获取用户
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            
            # 验证旧密码
            if not PwdUtil.verify_password(password_request.old_password, user.password_hash):
                raise AuthenticationError("旧密码错误")
            
            # 验证新密码强度
            is_valid, message = PwdUtil.validate_password_strength(password_request.new_password)
            if not is_valid:
                raise ValidationError(message)
            
            # 更新密码
            new_password_hash = PwdUtil.hash_password(password_request.new_password)
            self.user_dao.update_user(user_id, {'password_hash': new_password_hash})
            
            # 记录安全日志
            LogUtil.log_security("PASSWORD_CHANGE", user_id, details="Password changed successfully")
            
            # 记录审计日志
            audit_logger.log_user_action("CHANGE_PASSWORD", user_id, user_id, {
                "change_time": datetime.now().isoformat()
            })
            
            logger.info(f"Password changed successfully for user: {user.username}")
            
            return True
            
        except (NotFoundError, AuthenticationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            raise BusinessError(f"修改密码失败: {str(e)}")
    
    def delete_user(self, user_id: int, deleter_id: Optional[int] = None) -> bool:
        """
        删除用户 (软删除)
        
        Args:
            user_id: 用户ID
            deleter_id: 删除者ID
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            NotFoundError: 用户不存在
            AuthorizationError: 权限不足
        """
        try:
            # 检查用户是否存在
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise NotFoundError("用户不存在")
            
            # 权限检查：只有管理员可以删除
            if deleter_id:
                deleter = self.user_dao.get_user_by_id(deleter_id)
                if not deleter or deleter.role != UserRole.ADMIN:
                    raise AuthorizationError("权限不足")
            
            # 不能删除自己
            if deleter_id == user_id:
                raise ValidationError("不能删除自己的账户")
            
            # 软删除用户
            result = self.user_dao.delete_user(user_id)
            
            # 记录审计日志
            audit_logger.log_user_action("DELETE_USER", deleter_id or 0, user_id, {
                "username": user.username,
                "email": user.email
            })
            
            logger.info(f"User deleted successfully: {user.username}")
            
            return result
            
        except (NotFoundError, AuthorizationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            raise BusinessError(f"删除用户失败: {str(e)}")
    
    def list_users(self, page: int = 1, page_size: int = 20, 
                  filters: Optional[Dict[str, Any]] = None, 
                  requester_id: Optional[int] = None) -> UserListResponse:
        """
        获取用户列表
        
        Args:
            page: 页码
            page_size: 每页大小
            filters: 过滤条件
            requester_id: 请求者ID
            
        Returns:
            UserListResponse: 用户列表响应
            
        Raises:
            AuthorizationError: 权限不足
        """
        try:
            # 权限检查：只有管理员可以查看用户列表
            if requester_id:
                requester = self.user_dao.get_user_by_id(requester_id)
                if not requester or requester.role != UserRole.ADMIN:
                    raise AuthorizationError("权限不足")
            
            # 获取用户列表
            users, total, page, page_size = self.user_dao.list_users(page, page_size, filters)
            
            # 转换为响应对象
            user_responses = [UserBaseResponse.from_orm(user) for user in users]
            
            return UserListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=user_responses
            )
            
        except AuthorizationError:
            raise
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            raise BusinessError(f"获取用户列表失败: {str(e)}")
    
    def get_user_stats(self, requester_id: Optional[int] = None) -> UserStatsResponse:
        """
        获取用户统计信息
        
        Args:
            requester_id: 请求者ID
            
        Returns:
            UserStatsResponse: 用户统计响应
            
        Raises:
            AuthorizationError: 权限不足
        """
        try:
            # 权限检查：只有管理员可以查看统计信息
            if requester_id:
                requester = self.user_dao.get_user_by_id(requester_id)
                if not requester or requester.role != UserRole.ADMIN:
                    raise AuthorizationError("权限不足")
            
            # 获取统计信息
            stats = self.user_dao.get_user_stats()
            
            return UserStatsResponse(**stats)
            
        except AuthorizationError:
            raise
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            raise BusinessError(f"获取用户统计失败: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            Dict[str, Any]: 解码后的令牌数据
            
        Raises:
            AuthenticationError: 令牌无效
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # 检查用户是否仍然存在且活跃
            user = self.user_dao.get_user_by_id(payload.get('user_id'))
            if not user or user.status != UserStatus.ACTIVE:
                raise AuthenticationError("用户状态异常")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.JWTError:
            raise AuthenticationError("令牌无效")
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise AuthenticationError("令牌验证失败")
    
    def get_all_users(self) -> List[DvssUser]:
        """获取所有用户"""
        return self.user_dao.get_all_users()
    
    def update_user(self, user_id: int, user_data: UserUpdateRequest) -> Optional[DvssUser]:
        """更新用户信息"""
        try:
            return self.user_dao.update_user(user_id, user_data)
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            return self.user_dao.delete_user(user_id)
        except Exception as e:
            logger.error(f"Delete user error: {e}")
            return False
    
    def change_password(self, user_id: int, password_data: UserPasswordChangeRequest) -> bool:
        """修改用户密码"""
        try:
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                return False
                
            # 验证当前密码
            if not PwdUtil.verify_password(password_data.current_password, user.password_hash):
                return False
                
            # 更新密码
            new_password_hash = PwdUtil.hash_password(password_data.new_password)
            return self.user_dao.update_password(user_id, new_password_hash)
        except Exception as e:
            logger.error(f"Change password error: {e}")
            return False