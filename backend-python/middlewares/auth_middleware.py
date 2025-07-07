"""
认证中间件
Authentication Middleware
"""

import logging

from typing import Any, Dict

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_dvss.entity.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()

# JWT设置
SECRET_KEY = 'your-secret-key-change-in-production'  # 生产环境需要从环境变量读取
ALGORITHM = 'HS256'


def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    try:
        # 验证令牌
        payload = verify_token(credentials.credentials)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='无效的访问令牌',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        user_id = payload.get('sub')

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='无效的访问令牌',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        # 查询用户
        result = await db.execute(select(User).where(User.id == user_id).where(User.is_active))

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='用户不存在或已禁用',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Get current user error: {e}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='认证失败', headers={'WWW-Authenticate': 'Bearer'}
        )
