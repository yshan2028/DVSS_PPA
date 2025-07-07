"""
订单管理控制器
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from core.deps import get_current_user
from module_dvss.entity.user import User
from utils.response_util import PageResponse, ResponseUtil

from module_dvss.schemas.common_schema import ApiResponse
from module_dvss.schemas.order_schema import (
    EncryptedOrderResponse,
    OrderCreate,
    OrderDecrypt,
    OrderResponse,
    OrderStatistics,
    OrderUpdate,
)
from module_dvss.service.order_service import OrderService

router = APIRouter(prefix='/api/v1/orders', tags=['订单管理'])


@router.post('', response_model=ApiResponse[None])
async def create_order(
    order_data: OrderCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """创建原始订单"""
    try:
        result = await OrderService.create_order_services(db, order_data, current_user.id)
        return ResponseUtil.success(data=None, message=result.message)
    except Exception as e:
        return ResponseUtil.error(message=f'创建订单失败: {str(e)}')


@router.get('', response_model=PageResponse)
async def get_orders(
    page: int = Query(1, ge=1, description='页码'),
    size: int = Query(10, ge=1, le=100, description='每页大小'),
    status: Optional[str] = Query(None, description='订单状态'),
    user_id: Optional[int] = Query(None, description='用户ID'),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取订单列表"""
    try:
        filters = {}
        if status:
            filters['status'] = status
        if user_id:
            filters['user_id'] = user_id
            
        orders, total = await OrderService.get_order_list_services(db, page, size, current_user.id, filters)
        result = PageResponse(items=orders, total=total, page=page, size=size)
        return ResponseUtil.success(data=result, message='获取订单列表成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取订单列表失败: {str(e)}')


@router.get('/{order_id}', response_model=ApiResponse[OrderResponse])
async def get_order_detail(
    order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取订单详情"""
    try:
        order = await OrderService.get_order_by_id_services(db, order_id, current_user.id)
        if not order:
            raise HTTPException(status_code=404, detail='订单不存在')
        return ResponseUtil.success(data=order, message='获取订单详情成功')
    except HTTPException:
        raise
    except Exception as e:
        return ResponseUtil.error(message=f'获取订单详情失败: {str(e)}')


@router.put('/{order_id}', response_model=ApiResponse[None])
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新订单"""
    try:
        result = await OrderService.update_order_services(db, order_id, order_data, current_user.id)
        return ResponseUtil.success(data=None, message=result.message)
    except HTTPException:
        raise
    except Exception as e:
        return ResponseUtil.error(message=f'更新订单失败: {str(e)}')


@router.delete('/{order_id}')
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除订单"""
    try:
        result = await OrderService.delete_order_services(db, order_id, current_user.id)
        return ResponseUtil.success(message=result.message)
    except HTTPException:
        raise
    except Exception as e:
        return ResponseUtil.error(message=f'删除订单失败: {str(e)}')


@router.post('/{order_id}/process', response_model=ApiResponse[EncryptedOrderResponse])
async def process_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """处理订单（加密、分片）"""
    try:
        # 简化处理，这里可能需要调用加密和分片服务
        # encrypted_order = await OrderService.process_order_services(db, order_id)
        # return ResponseUtil.success(data=encrypted_order, message='订单处理成功')
        return ResponseUtil.error(message='订单处理功能暂未实现')
    except Exception as e:
        return ResponseUtil.error(message=f'订单处理失败: {str(e)}')


@router.post('/{order_id}/decrypt', response_model=ApiResponse[OrderResponse])
async def decrypt_order(
    order_id: int,
    request: OrderDecrypt,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """解密订单"""
    try:
        # 简化处理，这里可能需要调用解密服务
        # decrypted_order = await OrderService.decrypt_order_services(db, order_id, request)
        # return ResponseUtil.success(data=decrypted_order, message='订单解密成功')
        return ResponseUtil.error(message='订单解密功能暂未实现')
    except Exception as e:
        return ResponseUtil.error(message=f'订单解密失败: {str(e)}')


@router.get('/{order_id}/encrypted', response_model=ApiResponse[EncryptedOrderResponse])
async def get_encrypted_order(
    order_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """获取加密订单"""
    try:
        # 简化处理，这里可能需要调用获取加密订单的服务
        # encrypted_order = await OrderService.get_encrypted_order_services(db, order_id)
        # if not encrypted_order:
        #     raise HTTPException(status_code=404, detail='加密订单不存在')
        # return ResponseUtil.success(data=encrypted_order, message='获取加密订单成功')
        return ResponseUtil.error(message='获取加密订单功能暂未实现')
    except HTTPException:
        raise
    except Exception as e:
        return ResponseUtil.error(message=f'获取加密订单失败: {str(e)}')


@router.get('/stats/summary', response_model=ApiResponse[OrderStatistics])
async def get_order_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取订单统计信息"""
    try:
        stats = await OrderService.get_order_statistics_services(db)
        return ResponseUtil.success(data=stats, message='获取订单统计成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取订单统计失败: {str(e)}')
