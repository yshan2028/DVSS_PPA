"""
订单管理控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from ..schemas.order_schema import (
    OriginalOrderCreate, OriginalOrderUpdate, OriginalOrderResponse,
    EncryptedOrderResponse, OrderProcessRequest, OrderDecryptRequest,
    OrderListResponse, OrderStatsResponse
)
from ..schemas.common_schema import ApiResponse, PageResponse
from ..service.order_service import OrderService
from core.deps import get_order_service
from utils.response_util import success_response, error_response

router = APIRouter(prefix="/api/v1/orders", tags=["订单管理"])


@router.post("", response_model=ApiResponse[OriginalOrderResponse])
async def create_order(
    order_data: OriginalOrderCreate,
    service: OrderService = Depends(get_order_service)
):
    """创建原始订单"""
    try:
        order = await service.create_order(order_data)
        return success_response(data=order, message="订单创建成功")
    except Exception as e:
        return error_response(message=f"创建订单失败: {str(e)}")


@router.get("", response_model=ApiResponse[PageResponse[OriginalOrderResponse]])
async def get_orders(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    status: Optional[str] = Query(None, description="订单状态"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    service: OrderService = Depends(get_order_service)
):
    """获取订单列表"""
    try:
        result = await service.get_orders(
            page=page, size=size, status=status, user_id=user_id
        )
        return success_response(data=result, message="获取订单列表成功")
    except Exception as e:
        return error_response(message=f"获取订单列表失败: {str(e)}")


@router.get("/{order_id}", response_model=ApiResponse[OriginalOrderResponse])
async def get_order_detail(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """获取订单详情"""
    try:
        order = await service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        return success_response(data=order, message="获取订单详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取订单详情失败: {str(e)}")


@router.put("/{order_id}", response_model=ApiResponse[OriginalOrderResponse])
async def update_order(
    order_id: int,
    order_data: OriginalOrderUpdate,
    service: OrderService = Depends(get_order_service)
):
    """更新订单"""
    try:
        order = await service.update_order(order_id, order_data)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        return success_response(data=order, message="订单更新成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"更新订单失败: {str(e)}")


@router.delete("/{order_id}", response_model=ApiResponse)
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """删除订单"""
    try:
        success = await service.delete_order(order_id)
        if not success:
            raise HTTPException(status_code=404, detail="订单不存在")
        return success_response(message="订单删除成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"删除订单失败: {str(e)}")


@router.post("/{order_id}/process", response_model=ApiResponse[EncryptedOrderResponse])
async def process_order(
    order_id: int,
    process_data: OrderProcessRequest,
    service: OrderService = Depends(get_order_service)
):
    """处理订单（加密和分片）"""
    try:
        encrypted_order = await service.process_order(order_id, process_data)
        return success_response(data=encrypted_order, message="订单处理成功")
    except Exception as e:
        return error_response(message=f"订单处理失败: {str(e)}")


@router.post("/{order_id}/decrypt", response_model=ApiResponse[OriginalOrderResponse])
async def decrypt_order(
    order_id: int,
    decrypt_data: OrderDecryptRequest,
    service: OrderService = Depends(get_order_service)
):
    """解密订单数据"""
    try:
        decrypted_order = await service.decrypt_order(order_id, decrypt_data)
        return success_response(data=decrypted_order, message="订单解密成功")
    except Exception as e:
        return error_response(message=f"订单解密失败: {str(e)}")


@router.get("/{order_id}/encrypted", response_model=ApiResponse[EncryptedOrderResponse])
async def get_encrypted_order(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """获取加密订单数据"""
    try:
        encrypted_order = await service.get_encrypted_order(order_id)
        if not encrypted_order:
            raise HTTPException(status_code=404, detail="加密订单不存在")
        return success_response(data=encrypted_order, message="获取加密订单成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取加密订单失败: {str(e)}")


@router.get("/{order_id}/shards", response_model=ApiResponse[List[dict]])
async def get_order_shards(
    order_id: int,
    service: OrderService = Depends(get_order_service)
):
    """获取订单分片信息"""
    try:
        shards = await service.get_order_shards(order_id)
        return success_response(data=shards, message="获取订单分片成功")
    except Exception as e:
        return error_response(message=f"获取订单分片失败: {str(e)}")


@router.get("/stats/overview", response_model=ApiResponse[OrderStatsResponse])
async def get_order_stats(
    service: OrderService = Depends(get_order_service)
):
    """获取订单统计信息"""
    try:
        stats = await service.get_order_stats()
        return success_response(data=stats, message="获取订单统计成功")
    except Exception as e:
        return error_response(message=f"获取订单统计失败: {str(e)}")


@router.post("/batch-process", response_model=ApiResponse[List[EncryptedOrderResponse]])
async def batch_process_orders(
    order_ids: List[int],
    process_data: OrderProcessRequest,
    service: OrderService = Depends(get_order_service)
):
    """批量处理订单"""
    try:
        results = await service.batch_process_orders(order_ids, process_data)
        return success_response(data=results, message="批量处理订单成功")
    except Exception as e:
        return error_response(message=f"批量处理订单失败: {str(e)}")
