"""
FastAPI Dependencies - 依赖注入配置
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from services.auth_service import AuthService
from services.rbac_service import RBACService
from services.data_service import DataService
from services.encryption_service import EncryptionService
from services.dvss_service import DVSSAnalysisService
from models import User

# 安全模式
security = HTTPBearer()

# 全局服务实例
_auth_service = None
_rbac_service = None
_data_service = None
_encryption_service = None
_dvss_service = None


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service


def get_rbac_service() -> RBACService:
    """获取RBAC服务实例"""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


def get_data_service() -> DataService:
    """获取数据服务实例"""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service


def get_encryption_service() -> EncryptionService:
    """获取加密服务实例"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def get_dvss_service() -> DVSSAnalysisService:
    """获取DVSS分析服务实例"""
    global _dvss_service
    if _dvss_service is None:
        _dvss_service = DVSSAnalysisService()
    return _dvss_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """获取当前用户（从JWT令牌）"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被禁用"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证验证失败",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级用户权限"
        )
    return current_user


def require_permission(resource: str, action: str):
    """权限检查装饰器工厂"""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        rbac_service: RBACService = Depends(get_rbac_service)
    ) -> User:
        has_permission = await rbac_service.check_permission(current_user, resource, action)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要 {resource}:{action} 权限"
            )
        return current_user
    
    return permission_checker


# 常用权限检查器
require_data_read = require_permission("data", "read")
require_data_write = require_permission("data", "write")
require_data_decrypt = require_permission("data", "decrypt")
require_user_admin = require_permission("user", "admin")
require_audit_read = require_permission("audit", "read")
require_system_admin = require_permission("system", "admin")
require_dvss_analyze = require_permission("dvss", "analyze")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """获取可选用户（允许未认证访问）"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user if user and user.is_active else None
    except:
        return None
