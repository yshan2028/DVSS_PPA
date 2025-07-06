"""
字段管理控制器
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db, get_current_user
from module_dvss.schemas.field_schema import (
    FieldCreate,
    FieldUpdate,
    FieldResponse,
    FieldList,
    FieldBatchUpdate,
    FieldSensitivityAnalysis,
    FieldPermission
)
from module_dvss.schemas.common_schema import CommonResponse, PaginatedResponse
from module_dvss.service.field_service import FieldService
from module_dvss.entity.user import User
from utils.response_util import ResponseUtil

router = APIRouter(prefix="/fields", tags=["字段管理"])


@router.post("/", response_model=CommonResponse[FieldResponse], summary="创建字段")
async def create_field(
    field_data: FieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新字段"""
    field_service = FieldService(db)
    
    try:
        field = await field_service.create_field(field_data)
        return ResponseUtil.success(data=field, message="字段创建成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建字段失败"
        )


@router.get("/", response_model=PaginatedResponse[FieldList], summary="获取字段列表")
async def get_fields_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="字段分类"),
    sensitivity_level: Optional[str] = Query(None, description="敏感度等级"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取字段列表"""
    field_service = FieldService(db)
    
    try:
        fields, total = await field_service.get_fields_list(
            page=page,
            size=size,
            category=category,
            sensitivity_level=sensitivity_level,
            is_active=is_active,
            search=search
        )
        
        return ResponseUtil.paginated_success(
            data=fields,
            total=total,
            page=page,
            size=size,
            message="获取字段列表成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取字段列表失败"
        )


@router.get("/{field_id}", response_model=CommonResponse[FieldResponse], summary="获取字段详情")
async def get_field_detail(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取字段详情"""
    field_service = FieldService(db)
    
    field = await field_service.get_field_by_id(field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="字段不存在"
        )
    
    return ResponseUtil.success(data=field, message="获取字段详情成功")


@router.put("/{field_id}", response_model=CommonResponse[FieldResponse], summary="更新字段")
async def update_field(
    field_id: int,
    field_data: FieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新字段"""
    field_service = FieldService(db)
    
    try:
        field = await field_service.update_field(field_id, field_data)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字段不存在"
            )
        
        return ResponseUtil.success(data=field, message="字段更新成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新字段失败"
        )


@router.delete("/{field_id}", response_model=CommonResponse, summary="删除字段")
async def delete_field(
    field_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除字段"""
    field_service = FieldService(db)
    
    try:
        success = await field_service.delete_field(field_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="字段不存在"
            )
        
        return ResponseUtil.success(message="字段删除成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除字段失败"
        )


@router.post("/batch-update", response_model=CommonResponse, summary="批量更新字段")
async def batch_update_fields(
    batch_data: FieldBatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量更新字段"""
    field_service = FieldService(db)
    
    try:
        count = await field_service.batch_update_fields(batch_data)
        return ResponseUtil.success(
            data={"updated_count": count},
            message=f"批量更新成功，影响 {count} 条记录"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量更新字段失败"
        )


@router.get("/analysis/sensitivity", response_model=CommonResponse[FieldSensitivityAnalysis], summary="获取敏感度分析")
async def get_sensitivity_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取字段敏感度分析"""
    field_service = FieldService(db)
    
    try:
        analysis = await field_service.get_sensitivity_analysis()
        return ResponseUtil.success(data=analysis, message="获取敏感度分析成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取敏感度分析失败"
        )


@router.get("/category/{category}", response_model=CommonResponse[List[FieldResponse]], summary="根据分类获取字段")
async def get_fields_by_category(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据分类获取字段"""
    field_service = FieldService(db)
    
    try:
        fields = await field_service.get_fields_by_category(category)
        return ResponseUtil.success(data=fields, message="获取分类字段成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取分类字段失败"
        )


@router.get("/active/all", response_model=CommonResponse[List[FieldResponse]], summary="获取所有激活字段")
async def get_active_fields(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有激活字段"""
    field_service = FieldService(db)
    
    try:
        fields = await field_service.get_active_fields()
        return ResponseUtil.success(data=fields, message="获取激活字段成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取激活字段失败"
        )


@router.get("/permissions/role/{role_id}", response_model=CommonResponse[List[FieldPermission]], summary="获取角色字段权限")
async def get_role_field_permissions(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取角色的字段权限"""
    field_service = FieldService(db)
    
    try:
        permissions = await field_service.get_role_field_permissions(role_id)
        return ResponseUtil.success(data=permissions, message="获取角色字段权限成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色字段权限失败"
        )


@router.post("/permissions/role/{role_id}", response_model=CommonResponse, summary="设置角色字段权限")
async def set_role_field_permissions(
    role_id: int,
    permissions: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置角色字段权限"""
    field_service = FieldService(db)
    
    try:
        success = await field_service.set_role_field_permissions(role_id, permissions)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="设置角色字段权限失败"
            )
        
        return ResponseUtil.success(message="设置角色字段权限成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="设置角色字段权限失败"
        )
