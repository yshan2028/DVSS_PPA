"""
认证服务层
Service Layer - 处理用户认证相关的业务逻辑
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import jwt
import bcrypt

from module_dvss.dao.user_dao import UserDAO
from module_dvss.schemas.user_schema import LoginRequest, LoginResponse, UserResponse
from module_dvss.entity.user import User
from exceptions.custom_exception import AuthenticationError, AuthorizationError
from utils.log_util import LogUtil
from config.settings import Settings

logger = LogUtil.get_logger("auth_service")
settings = Settings()

class AuthService:
    """认证服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_dao = UserDAO(db)
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        用户登录
        
        Args:
            login_data: 登录请求数据
            
        Returns:
            LoginResponse: 登录响应数据
            
        Raises:
            AuthenticationError: 认证失败
        """
        try:
            logger.info(f"用户尝试登录: {login_data.username}")
            
            # 验证用户
            user = await self.user_dao.get_user_by_username(login_data.username)
            if not user:
                raise AuthenticationError("用户名或密码错误")
            
            # 验证密码
            if not self._verify_password(login_data.password, user.password_hash):
                raise AuthenticationError("用户名或密码错误")
            
            # 检查用户状态
            if not user.is_active:
                raise AuthorizationError("用户已被禁用")
            
            # 生成令牌
            access_token = self._create_access_token({
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.name if user.role else None
            })
            
            refresh_token = self._create_refresh_token({
                "sub": str(user.id),
                "username": user.username
            })
            
            # 更新最后登录时间
            await self.user_dao.update_last_login(user.id)
            
            # 构造响应
            response = LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    nickname=user.nickname,
                    is_active=user.is_active,
                    role=user.role.name if user.role else None,
                    last_login=user.last_login,
                    created_at=user.created_at
                )
            )
            
            logger.info(f"用户 {login_data.username} 登录成功")
            return response
            
        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            raise AuthenticationError("登录失败")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Dict: 新的令牌信息
            
        Raises:
            AuthenticationError: 令牌无效
        """
        try:
            # 验证刷新令牌
            payload = self._decode_token(refresh_token)
            user_id = int(payload.get("sub"))
            
            # 获取用户信息
            user = await self.user_dao.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise AuthenticationError("用户不存在或已被禁用")
            
            # 生成新的访问令牌
            new_access_token = self._create_access_token({
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.name if user.role else None
            })
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
            
        except Exception as e:
            logger.error(f"刷新令牌失败: {str(e)}")
            raise AuthenticationError("令牌刷新失败")
    
    async def verify_token(self, token: str) -> User:
        """
        验证访问令牌
        
        Args:
            token: 访问令牌
            
        Returns:
            User: 用户对象
            
        Raises:
            AuthenticationError: 令牌无效
        """
        try:
            # 解码令牌
            payload = self._decode_token(token)
            user_id = int(payload.get("sub"))
            
            # 获取用户信息
            user = await self.user_dao.get_user_by_id(user_id)
            if not user:
                raise AuthenticationError("用户不存在")
            
            if not user.is_active:
                raise AuthorizationError("用户已被禁用")
            
            return user
            
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            raise AuthenticationError("令牌验证失败")
    
    async def logout(self, user_id: int) -> bool:
        """
        用户登出
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 登出是否成功
        """
        try:
            logger.info(f"用户 {user_id} 登出")
            # 这里可以添加登出逻辑，比如将令牌加入黑名单等
            # 目前只记录日志
            return True
            
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            return False
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def _create_access_token(self, data: Dict[str, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    def _decode_token(self, token: str) -> Dict[str, Any]:
        """解码令牌"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.JWTError:
            raise AuthenticationError("令牌无效")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_info=UserResponse.from_orm(user)
        )
    
    async def get_current_user_permissions(self, user_id: int) -> dict:
        """获取用户权限"""
        user = self.user_dao.get_by_id(user_id)
        if not user or not user.role:
            return {"permissions": [], "field_permissions": {}}
        
        # 获取角色权限
        permissions = []
        field_permissions = {}
        
        for fp in user.role.field_permissions:
            field_permissions[fp.field_id] = {
                "can_view": fp.can_view,
                "can_decrypt": fp.can_decrypt
            }
        
        return {
            "permissions": permissions,
            "field_permissions": field_permissions
        }
