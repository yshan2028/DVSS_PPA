"""
用户管理控制器
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from core.deps import get_current_user
from module_dvss.schemas.user_schema import (
    UserCreate, 
    UserUpdate, 
    UserResponse,
    UserPasswordChange,
    UserList
)
from module_dvss.schemas.common_schema import CommonResponse, PaginatedResponse
from module_dvss.service.user_service import UserService
from module_dvss.entity.user import User
from utils.response_util import ResponseUtil

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.post("/", response_model=CommonResponse[UserResponse], summary="创建用户")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新用户"""
    user_service = UserService(db)
    
    # 检查用户名是否已存在
    existing_user = await user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = await user_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    user = await user_service.create_user(user_data)
    return ResponseUtil.success(UserResponse.from_orm(user), "用户创建成功")


@router.get("/", response_model=PaginatedResponse[UserList], summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名筛选"),
    email: Optional[str] = Query(None, description="邮箱筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（支持分页和筛选）"""
    user_service = UserService(db)
    
    users, total = await user_service.get_users_paginated(
        page=page,
        page_size=page_size,
        username=username,
        email=email,
        is_active=is_active
    )
    
    user_list = [UserList.from_orm(user) for user in users]
    
    return ResponseUtil.paginated_success(
        data=user_list,
        total=total,
        page=page,
        page_size=page_size,
        message="获取用户列表成功"
    )


@router.get("/{user_id}", response_model=CommonResponse[UserResponse], summary="获取用户详情")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户详情"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ResponseUtil.success(UserResponse.from_orm(user), "获取用户详情成功")


@router.put("/{user_id}", response_model=CommonResponse[UserResponse], summary="更新用户")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = await user_service.get_user_by_email(user_data.email)
        if existing_email and existing_email.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
    
    updated_user = await user_service.update_user(user_id, user_data)
    return ResponseUtil.success(UserResponse.from_orm(updated_user), "用户更新成功")


@router.delete("/{user_id}", response_model=CommonResponse[None], summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    await user_service.delete_user(user_id)
    return ResponseUtil.success(None, "用户删除成功")


@router.post("/{user_id}/reset-password", response_model=CommonResponse[None], summary="重置密码")
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重置用户密码"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    new_password = await user_service.reset_password(user_id)
    return ResponseUtil.success(
        {"temp_password": new_password}, 
        "密码重置成功，请使用临时密码登录后修改"
    )


@router.put("/{user_id}/status", response_model=CommonResponse[UserResponse], summary="启用/禁用用户")
async def toggle_user_status(
    user_id: int,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """启用/禁用用户"""
    user_service = UserService(db)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能禁用自己
    if user_id == current_user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己"
        )
    
    updated_user = await user_service.update_user_status(user_id, is_active)
    status_text = "启用" if is_active else "禁用"
    return ResponseUtil.success(
        UserResponse.from_orm(updated_user), 
        f"用户{status_text}成功"
    )


@router.post("/change-password", response_model=CommonResponse[None], summary="修改密码")
async def change_password(
    password_data: UserPasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改当前用户密码"""
    user_service = UserService(db)
    
    # 验证旧密码
    if not await user_service.verify_password(current_user.id, password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    await user_service.change_password(current_user.id, password_data.new_password)
    return ResponseUtil.success(None, "密码修改成功")
                    "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                }
                for user in paginated_users
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        return ResponseUtil.server_error("获取用户列表失败")


@router.post("/", summary="创建用户")
def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """创建新用户"""
    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data)
        
        return ResponseUtil.success({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }, "用户创建成功")
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return ResponseUtil.server_error("创建用户失败")


@router.get("/{user_id}", summary="获取用户详情")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取指定用户的详细信息"""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return ResponseUtil.success({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "organization": user.organization,
            "department": user.department,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "is_active": user.is_active,
            "phone": user.phone,
            "address": user.address,
            "notes": user.notes,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        return ResponseUtil.server_error("获取用户信息失败")


@router.put("/{user_id}", summary="更新用户信息")
def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    try:
        user_service = UserService(db)
        user = user_service.update_user(user_id, user_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return ResponseUtil.success({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "is_active": user.is_active,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }, "用户信息更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        return ResponseUtil.server_error("更新用户信息失败")


@router.delete("/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """删除用户"""
    try:
        user_service = UserService(db)
        success = user_service.delete_user(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return ResponseUtil.success(None, "用户删除成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        return ResponseUtil.server_error("删除用户失败")


@router.post("/{user_id}/change-password", summary="修改用户密码")
def change_password(
    user_id: int,
    password_data: UserPasswordChangeRequest,
    db: Session = Depends(get_db)
):
    """修改用户密码"""
    try:
        user_service = UserService(db)
        success = user_service.change_password(user_id, password_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在或密码错误"
            )
        
        return ResponseUtil.success(None, "密码修改成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        return ResponseUtil.server_error("修改密码失败")