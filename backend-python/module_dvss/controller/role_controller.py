"""
角色管理控制器
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from module_dvss.entity.user import User
from module_dvss.schemas.common_schema import ApiResponse, PageResponse
from module_dvss.schemas.role_schema import (
    RoleCreate,
    RoleList,
    RolePermissionCreate,
    RolePermissionResponse,
    RoleResponse,
    RoleUpdate,
)
from module_dvss.service.role_service import RoleService
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/roles', tags=['角色管理'])


@router.post('/', response_model=ApiResponse[RoleResponse], summary='创建角色')
async def create_role(
    role_data: RoleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """创建新角色"""
    role_service = RoleService(db)

    # 检查角色名是否已存在
    existing_role = await role_service.get_role_by_name(role_data.name)
    if existing_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='角色名已存在')

    role = await role_service.create_role(role_data)
    return ResponseUtil.success(RoleResponse.from_orm(role), '角色创建成功')


@router.get('/', response_model=PageResponse, summary='获取角色列表')
async def get_roles(
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(20, ge=1, le=100, description='每页数量'),
    name: Optional[str] = Query(None, description='角色名筛选'),
    is_active: Optional[bool] = Query(None, description='激活状态筛选'),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取角色列表（支持分页和筛选）"""
    role_service = RoleService(db)

    roles, total = await role_service.get_roles_paginated(
        page=page, page_size=page_size, name=name, is_active=is_active
    )

    role_list = [RoleList.from_orm(role) for role in roles]

    return ResponseUtil.paginated_success(
        data=role_list, total=total, page=page, size=page_size, message='获取角色列表成功'
    )


@router.get('/{role_id}', response_model=ApiResponse[RoleResponse], summary='获取角色详情')
async def get_role(role_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取角色详情"""
    role_service = RoleService(db)

    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')

    return ResponseUtil.success(RoleResponse.from_orm(role), '获取角色详情成功')


@router.put('/{role_id}', response_model=ApiResponse[RoleResponse], summary='更新角色')
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新角色信息"""
    role_service = RoleService(db)

    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')

    # 检查角色名是否已被其他角色使用
    if role_data.name and role_data.name != role.name:
        existing_role = await role_service.get_role_by_name(role_data.name)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='角色名已被其他角色使用')

    updated_role = await role_service.update_role(role_id, role_data)
    return ResponseUtil.success(RoleResponse.from_orm(updated_role), '角色更新成功')


@router.delete('/{role_id}', response_model=ApiResponse, summary='删除角色')
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除角色"""
    role_service = RoleService(db)

    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')

    # 检查是否有用户使用此角色
    users_count = await role_service.count_users_by_role(role_id)
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f'无法删除角色，仍有 {users_count} 个用户使用此角色'
        )

    await role_service.delete_role(role_id)
    return ResponseUtil.success(None, '角色删除成功')


@router.post(
    '/{role_id}/permissions', response_model=ApiResponse[List[RolePermissionResponse]], summary='设置角色字段权限'
)
async def set_role_permissions(
    role_id: int,
    permissions: List[RolePermissionCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """设置角色字段权限"""
    role_service = RoleService(db)

    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')

    result_permissions = await role_service.set_role_permissions(role_id, permissions)
    permission_responses = [RolePermissionResponse.from_orm(perm) for perm in result_permissions]

    return ResponseUtil.success(permission_responses, '角色权限设置成功')


@router.get('/{role_id}/permissions', response_model=ApiResponse[List[RolePermissionResponse]], summary='获取角色权限')
async def get_role_permissions(
    role_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取角色权限"""
    role_service = RoleService(db)

    role = await role_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='角色不存在')

    permissions = await role_service.get_role_permissions(role_id)
    permission_responses = [RolePermissionResponse.from_orm(perm) for perm in permissions]

    return ResponseUtil.success(permission_responses, '获取角色权限成功')
