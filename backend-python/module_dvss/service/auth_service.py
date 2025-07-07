from datetime import datetime, timedelta
from typing import Any, Dict

import bcrypt
import jwt

from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from config.settings import Settings
from exceptions.custom_exception import AuthenticationError, AuthorizationError
from module_dvss.entity.user import User
from module_dvss.schemas.user_schema import LoginRequest, LoginResponse, UserResponse
from utils.log_util import LogUtil

logger = LogUtil.get_logger('auth_service')
settings = Settings()


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        try:
            logger.info(f'用户尝试登录: {login_data.username}')

            user = self.db.query(User).filter(User.username == login_data.username).first()
            logger.info(f'数据库查询结果: user={"存在" if user else "不存在"}')

            if not user:
                logger.warning(f'用户 {login_data.username} 不存在')
                raise AuthenticationError('用户名或密码错误')

            if not self._verify_password(login_data.password, user.password_hash):
                logger.warning(f'用户 {login_data.username} 密码错误')
                raise AuthenticationError('用户名或密码错误')

            if not user.is_active:
                raise AuthorizationError('用户已被禁用')

            access_token = self._create_access_token({
                'sub': str(user.id),
                'username': user.username,
                'role': user.role.name if user.role else None,
            })
            refresh_token = self._create_refresh_token({
                'sub': str(user.id),
                'username': user.username,
            })

            # 更新最后登录时间（统一使用 UTC）
            user.last_login = datetime.utcnow()
            self.db.commit()

            user_resp = UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                role_id=user.role.id if user.role else None,
                created_at=user.created_at,
                last_login=user.last_login,
            )

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type='bearer',
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user_resp,
                user_info=user_resp,  # 同样返回一份给 user_info
            )

        except (AuthenticationError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f'登录失败，详细错误: {e}', exc_info=True)
            raise AuthenticationError('登录失败')

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        try:
            payload = self._decode_token(refresh_token)
            user_id = int(payload.get('sub'))

            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise AuthenticationError('用户不存在或已被禁用')

            new_access_token = self._create_access_token({
                'sub': str(user.id),
                'username': user.username,
                'role': user.role.name if user.role else None,
            })

            return {
                'access_token': new_access_token,
                'token_type': 'bearer',
                'expires_in': settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }

        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.error(f'刷新令牌失败: {e}')
            raise AuthenticationError('令牌无效或已过期')
        except Exception as e:
            logger.error(f'刷新令牌失败: {e}', exc_info=True)
            raise AuthenticationError('令牌刷新失败')

    async def verify_token(self, token: str):
        try:
            payload = self._decode_token(token)
            user_id = int(payload.get('sub'))

            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise AuthenticationError('用户不存在')
            if not user.is_active:
                raise AuthorizationError('用户已被禁用')

            return user

        except (ExpiredSignatureError, InvalidTokenError) as e:
            logger.error(f'令牌验证失败: {e}')
            raise AuthenticationError('令牌无效或已过期')
        except Exception as e:
            logger.error(f'令牌验证失败: {e}', exc_info=True)
            raise AuthenticationError('令牌验证失败')

    @staticmethod
    async def logout(user_id: int) -> bool:
        try:
            logger.info(f'用户 {user_id} 登出')
            return True
        except Exception as e:
            logger.error(f'用户登出失败: {e}')
            return False

    @staticmethod
    def _verify_password(plain_password: str, hashed_password) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f'密码验证异常: {e}')
            return False

    @staticmethod
    def _create_access_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({'exp': expire, 'type': 'access'})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def _create_refresh_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({'exp': expire, 'type': 'refresh'})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def _decode_token(token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except ExpiredSignatureError:
            raise AuthenticationError('令牌已过期')
        except InvalidTokenError:
            raise AuthenticationError('令牌无效')

    async def get_current_user_permissions(self, user_id: int) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.role:
            return {'permissions': [], 'field_permissions': {}}

        permissions = []
        field_permissions = {}
        for fp in user.role.field_permissions:
            field_permissions[fp.field_id] = {'can_view': fp.can_view, 'can_decrypt': fp.can_decrypt}
        return {'permissions': permissions, 'field_permissions': field_permissions}
