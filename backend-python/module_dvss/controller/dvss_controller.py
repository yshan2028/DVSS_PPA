"""
DVSS核心控制器
处理订单上传、查询、删除等核心功能
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from module_dvss.service.dvss_service import DVSSService
from module_dvss.schemas.order_schema import (
    OrderQueryRequest, OrderDeleteRequest, OrderResponse
)
from module_dvss.schemas.common_schema import ApiResponse, PageRequest
from core.deps import get_db, get_current_user
from utils.response_util import success_response, error_response
from exceptions.custom_exception import NotFoundError, ValidationError, AuthorizationError
from utils.log_util import LogUtil

logger = LogUtil.get_logger("dvss_controller")
router = APIRouter(prefix="/api/v1/dvss", tags=["DVSS核心"])


@router.post("/upload", response_model=ApiResponse[Dict[str, Any]])
async def upload_orders(
    file: UploadFile = File(..., description="订单文件"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """上传订单文件"""
    try:
        if not file.filename:
            raise ValidationError("文件名不能为空")
        
        # 检查文件类型
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise ValidationError("只支持CSV和Excel文件格式")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 处理订单上传
        dvss_service = DVSSService(db)
        result = await dvss_service.process_order_upload(
            file_data=file_content,
            filename=file.filename,
            current_user_id=current_user.id
        )
        
        return success_response(data=result, message="订单上传成功")
        
    except ValidationError as e:
        return error_response(message=str(e), code=400)
    except AuthorizationError as e:
        return error_response(message=str(e), code=403)
    except Exception as e:
        logger.error(f"订单上传失败: {str(e)}")
        return error_response(message=f"订单上传失败: {str(e)}")


@router.post("/query", response_model=ApiResponse[Dict[str, Any]])
async def query_orders(
    request: OrderQueryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """查询订单"""
    try:
        dvss_service = DVSSService(db)
        result = await dvss_service.query_orders(
            request=request,
            current_user_id=current_user.id
        )
        
        return success_response(data=result.dict(), message="查询成功")
        
    except AuthorizationError as e:
        return error_response(message=str(e), code=403)
    except Exception as e:
        logger.error(f"订单查询失败: {str(e)}")
        return error_response(message=f"订单查询失败: {str(e)}")


@router.delete("/orders", response_model=ApiResponse[Dict[str, Any]])
async def delete_orders(
    request: OrderDeleteRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除订单"""
    try:
        dvss_service = DVSSService(db)
        result = await dvss_service.delete_orders(
            request=request,
            current_user_id=current_user.id
        )
        
        return success_response(data=result, message="订单删除成功")
        
    except AuthorizationError as e:
        return error_response(message=str(e), code=403)
    except NotFoundError as e:
        return error_response(message=str(e), code=404)
    except Exception as e:
        logger.error(f"订单删除失败: {str(e)}")
        return error_response(message=f"订单删除失败: {str(e)}")


@router.get("/statistics", response_model=ApiResponse[Dict[str, Any]])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取DVSS统计信息"""
    try:
        dvss_service = DVSSService(db)
        stats = await dvss_service.get_statistics(current_user_id=current_user.id)
        
        return success_response(data=stats, message="获取统计信息成功")
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return error_response(message=f"获取统计信息失败: {str(e)}")


@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def health_check():
    """健康检查"""
    return success_response(
        data={
            "status": "healthy",
            "service": "DVSS Core",
            "timestamp": "2025-01-06T00:00:00Z"
        },
        message="服务正常"
    )
