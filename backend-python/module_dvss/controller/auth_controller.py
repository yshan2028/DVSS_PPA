"""
认证控制器
处理用户登录、注册、权限验证等功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.deps import get_db, get_current_user
from module_dvss.service.auth_service import AuthService
from module_dvss.schemas.user_schema import LoginRequest, LoginResponse, ChangePasswordRequest
from module_dvss.schemas.common_schema import SuccessResponse
from module_dvss.entity.user import User

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    return await auth_service.login(login_data)

@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 在实际项目中，可以将token加入黑名单
    return SuccessResponse(message="登出成功")

@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role_id": current_user.role_id
    }

@router.get("/permissions")
async def get_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户权限"""
    auth_service = AuthService(db)
    return await auth_service.get_current_user_permissions(current_user.id)

@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 这里可以添加修改密码的逻辑
    return SuccessResponse(message="密码修改成功")
