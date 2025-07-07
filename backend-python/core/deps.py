"""
依赖注入模块
提供数据库会话、认证等依赖
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from exceptions.custom_exception import AuthenticationError, AuthorizationError
from module_dvss.entity.user import User
from module_dvss.service.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户

    Args:
        credentials: HTTP认证凭据
        db: 数据库会话

    Returns:
        User: 当前用户对象

    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        user = await auth_service.verify_token(token)
        return user

    except (AuthenticationError, AuthorizationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token验证失败',
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        User: 活跃用户对象

    Raises:
        HTTPException: 用户未激活时抛出403错误
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='用户未激活')
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    获取管理员用户

    Args:
        current_user: 当前用户

    Returns:
        User: 管理员用户对象

    Raises:
        HTTPException: 非管理员用户时抛出403错误
    """
    if not current_user.role or current_user.role.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='需要管理员权限')
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), 
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取可选的当前用户（用于不需要强制认证的接口）

    Args:
        credentials: HTTP认证凭据（可选）
        db: 数据库会话

    Returns:
        Optional[User]: 用户对象或None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        return await auth_service.verify_token(token)
    except Exception:
        return None
