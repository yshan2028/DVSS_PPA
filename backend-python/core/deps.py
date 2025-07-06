"""
依赖注入模块
提供数据库会话、认证等依赖
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from core.security import security_manager
from module_dvss.dao.user_dao import UserDAO
from module_dvss.dao.role_dao import RoleDAO
from module_dvss.dao.field_dao import FieldDAO
from module_dvss.dao.order_dao import OrderDAO
from module_dvss.dao.log_dao import LogDAO
from module_dvss.service.user_service import UserService
from module_dvss.service.role_service import RoleService
from module_dvss.service.field_service import FieldService
from module_dvss.service.order_service import OrderService
from module_dvss.service.encryption_service import EncryptionService
from module_dvss.service.sensitivity_service import SensitivityService
from module_dvss.service.audit_service import AuditService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户"""
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效",
        )
    
    user_dao = UserDAO(db)
    user = await user_dao.get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user

def require_permission(permission: str):
    """权限检查装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以添加权限检查逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# DAO 依赖注入
async def get_user_dao() -> UserDAO:
    """获取用户DAO"""
    return UserDAO()

async def get_role_dao() -> RoleDAO:
    """获取角色DAO"""
    return RoleDAO()

async def get_field_dao() -> FieldDAO:
    """获取字段DAO"""
    return FieldDAO()

async def get_order_dao() -> OrderDAO:
    """获取订单DAO"""
    return OrderDAO()

async def get_log_dao() -> LogDAO:
    """获取日志DAO"""
    return LogDAO()

# Service 依赖注入
async def get_user_service(
    user_dao: UserDAO = Depends(get_user_dao),
    role_dao: RoleDAO = Depends(get_role_dao)
) -> UserService:
    """获取用户服务"""
    return UserService(user_dao, role_dao)

async def get_role_service(
    role_dao: RoleDAO = Depends(get_role_dao)
) -> RoleService:
    """获取角色服务"""
    return RoleService(role_dao)

async def get_field_service(
    field_dao: FieldDAO = Depends(get_field_dao)
) -> FieldService:
    """获取字段服务"""
    return FieldService(field_dao)

async def get_encryption_service() -> EncryptionService:
    """获取加密服务"""
    return EncryptionService()

async def get_sensitivity_service(
    field_dao: FieldDAO = Depends(get_field_dao)
) -> SensitivityService:
    """获取敏感度服务"""
    return SensitivityService(field_dao)

async def get_audit_service(
    log_dao: LogDAO = Depends(get_log_dao)
) -> AuditService:
    """获取审计服务"""
    return AuditService(log_dao)

async def get_order_service(
    order_dao: OrderDAO = Depends(get_order_dao),
    encryption_service: EncryptionService = Depends(get_encryption_service),
    sensitivity_service: SensitivityService = Depends(get_sensitivity_service),
    audit_service: AuditService = Depends(get_audit_service)
) -> OrderService:
    """获取订单服务"""
    return OrderService(order_dao, encryption_service, sensitivity_service, audit_service)
