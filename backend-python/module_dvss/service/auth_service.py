"""
认证服务
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import security_manager
from module_dvss.dao.user_dao import UserDAO
from module_dvss.schemas.user_schema import LoginRequest, LoginResponse, UserResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_dao = UserDAO(db)
    
    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """用户登录"""
        # 验证用户
        user = self.user_dao.get_by_username(login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not security_manager.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 生成令牌
        access_token = security_manager.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = security_manager.create_access_token(
            data={"sub": str(user.id), "type": "refresh"}
        )
        
        # 更新最后登录时间
        self.user_dao.update_last_login(user.id)
        
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
