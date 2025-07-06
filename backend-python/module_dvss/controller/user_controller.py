"""
用户管理模块控制器
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from typing import List, Optional, Dict, Any
from config.get_db import get_db, Session
from module_dvss.entity.vo.user_vo import (
    UserCreateRequest, 
    UserUpdateRequest, 
    UserPasswordChangeRequest
)
from module_dvss.service.user_service import UserService
from utils.response_util import ResponseUtil
from utils.log_util import LogUtil

logger = LogUtil.get_logger("user_controller")

router = APIRouter()

@router.get("/", summary="获取用户列表")
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    username: Optional[str] = Query(None, description="用户名筛选"),
    db: Session = Depends(get_db)
):
    """获取用户列表（支持分页和筛选）"""
    try:
        user_service = UserService(db)
        
        # 简单实现，实际应该在service层实现分页
        users = user_service.get_all_users()
        
        # 应用筛选
        if username:
            users = [user for user in users if username.lower() in user.username.lower()]
        
        # 简单分页
        total = len(users)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_users = users[start_idx:end_idx]
        
        return ResponseUtil.success({
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
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