"""
DVSS 主要API控制器
处理订单上传、查询、删除等核心功能
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import pandas as pd
import json
import asyncio
from datetime import datetime
import httpx

from core.database import get_db
from core.redis_client import get_redis
from core.models import Order, User, AuditLog
from module_dvss.service.sensitivity_analyzer import SensitivityAnalyzer
from module_dvss.service.monitoring_service import DynamicThresholdCalculator
from module_dvss.service.sharding_service import ShardingService
from module_dvss.service.permission_service import PermissionService
from utils.response_util import success_response, error_response
from middlewares.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/dvss", tags=["DVSS Core"])
security = HTTPBearer()

# 依赖注入
async def get_services(
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis)
):
    """获取服务实例"""
    from core.database import get_mongodb
    mongodb = await get_mongodb()
    
    return {
        'sensitivity_analyzer': SensitivityAnalyzer(),
        'threshold_calculator': DynamicThresholdCalculator(redis_client=redis),
        'sharding_service': ShardingService(mongodb, db, redis),
        'permission_service': PermissionService(db)
    }

@router.post("/upload_order")
async def upload_order(
    request: Request,
    order_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    services = Depends(get_services)
):
    """
    上传订单数据并进行分片加密
    """
    try:
        # 1. 权限检查
        permission_service = services['permission_service']
        has_permission = await permission_service.check_action_permission(
            str(current_user.id), 'create'
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有创建订单的权限"
            )
        
        # 2. 数据验证
        if not order_data.get('order_id'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单ID不能为空"
            )
        
        # 检查订单是否已存在
        existing_order = await db.execute(
            select(Order).where(Order.order_id == order_data['order_id'])
        )
        if existing_order.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="订单已存在"
            )
        
        # 3. 敏感度分析
        sensitivity_analyzer = services['sensitivity_analyzer']
        sensitivity_score = sensitivity_analyzer.calculate_order_sensitivity(order_data)
        
        # 4. 计算动态阈值k
        threshold_calculator = services['threshold_calculator']
        k_value = await threshold_calculator.get_current_k(sensitivity_score)
        
        # 5. 创建订单记录
        order = Order(
            order_id=order_data['order_id'],
            user_id=order_data.get('user_id'),
            customer_name=order_data.get('customer_name'),
            email=order_data.get('email'),
            phone=order_data.get('phone'),
            address=order_data.get('address'),
            shipping_address=order_data.get('shipping_address'),
            billing_address=order_data.get('billing_address'),
            item_list=order_data.get('item_list'),
            payment_info=order_data.get('payment_info'),
            total_amount=order_data.get('total_amount'),
            tax_amount=order_data.get('tax_amount'),
            shipping_cost=order_data.get('shipping_cost'),
            discount=order_data.get('discount'),
            sensitivity_score=sensitivity_score,
            data_source=order_data.get('data_source', 'manual'),
            status='active'
        )
        
        db.add(order)
        await db.commit()
        await db.refresh(order)
        
        # 6. 分片加密
        sharding_service = services['sharding_service']
        # 准备用于分片的数据（包含数据库ID）
        order_for_sharding = {**order_data, 'id': str(order.id)}
        
        shards_info = await sharding_service.encrypt_and_shard_order(
            order_for_sharding, k_value, n=5
        )
        
        # 7. 记录到区块链
        blockchain_tx_id = await record_to_blockchain(
            'CREATE_ORDER',
            {
                'order_id': order_data['order_id'],
                'sensitivity_score': sensitivity_score,
                'k_value': k_value,
                'shards_count': len(shards_info),
                'user_id': str(current_user.id)
            }
        )
        
        # 8. 审计日志
        await log_audit_action(
            db, current_user.id, 'CREATE', 'ORDER', order_data['order_id'],
            {
                'sensitivity_score': sensitivity_score,
                'k_value': k_value,
                'shards_created': len(shards_info)
            },
            request.client.host, request.headers.get('user-agent'),
            blockchain_tx_id
        )
        
        return success_response({
            'order_id': order_data['order_id'],
            'sensitivity_score': sensitivity_score,
            'k_value': k_value,
            'shards_created': len(shards_info),
            'blockchain_tx_id': blockchain_tx_id,
            'message': '订单上传并加密成功'
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading order: {e}")
        await db.rollback()
        return error_response(f"上传订单失败: {str(e)}")

@router.get("/get_order/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    services = Depends(get_services)
):
    """
    获取订单数据（分片重构和权限过滤）
    """
    try:
        # 1. 权限检查
        permission_service = services['permission_service']
        has_permission = await permission_service.check_action_permission(
            str(current_user.id), 'read'
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有读取订单的权限"
            )
        
        # 2. 检查订单是否存在
        order_result = await db.execute(
            select(Order).where(Order.order_id == order_id).where(Order.status == 'active')
        )
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 3. 检查数据源权限
        accessible_sources = await permission_service.get_accessible_data_sources(
            str(current_user.id)
        )
        
        if order.data_source not in accessible_sources and 'all' not in accessible_sources:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有访问此数据源的权限"
            )
        
        # 4. 分片重构
        sharding_service = services['sharding_service']
        try:
            reconstruction_result = await sharding_service.reconstruct_order_data(str(order.id))
            reconstructed_data = reconstruction_result['order_data']
            reconstruction_info = reconstruction_result['reconstruction_info']
        except Exception as e:
            logger.error(f"Error reconstructing order {order_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="数据重构失败"
            )
        
        # 5. 基于权限过滤数据
        filtered_data = await permission_service.filter_order_data(
            str(current_user.id), reconstructed_data
        )
        
        # 6. 记录到区块链
        blockchain_tx_id = await record_to_blockchain(
            'READ_ORDER',
            {
                'order_id': order_id,
                'user_id': str(current_user.id),
                'fields_accessed': list(filtered_data.keys())
            }
        )
        
        # 7. 审计日志
        await log_audit_action(
            db, current_user.id, 'READ', 'ORDER', order_id,
            {
                'reconstruction_info': reconstruction_info,
                'fields_accessed': len(filtered_data)
            },
            '', '', blockchain_tx_id
        )
        
        return success_response({
            'order_data': filtered_data,
            'reconstruction_info': reconstruction_info,
            'blockchain_tx_id': blockchain_tx_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        return error_response(f"获取订单失败: {str(e)}")

@router.delete("/delete_order/{order_id}")
async def delete_order(
    order_id: str,
    soft_delete: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    services = Depends(get_services)
):
    """
    删除订单（软删除或硬删除）
    """
    try:
        # 1. 权限检查
        permission_service = services['permission_service']
        has_permission = await permission_service.check_action_permission(
            str(current_user.id), 'delete'
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有删除订单的权限"
            )
        
        # 2. 检查订单是否存在
        order_result = await db.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = order_result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在"
            )
        
        # 3. 更新订单状态
        if soft_delete:
            await db.execute(
                update(Order)
                .where(Order.order_id == order_id)
                .values(status='deleted', updated_at=datetime.now())
            )
        else:
            await db.execute(
                delete(Order).where(Order.order_id == order_id)
            )
        
        # 4. 删除分片
        sharding_service = services['sharding_service']
        shards_deleted = await sharding_service.delete_shards(str(order.id), soft_delete)
        
        # 5. 记录到区块链
        blockchain_tx_id = await record_to_blockchain(
            'DELETE_ORDER',
            {
                'order_id': order_id,
                'user_id': str(current_user.id),
                'soft_delete': soft_delete,
                'shards_deleted': shards_deleted
            }
        )
        
        # 6. 审计日志
        await log_audit_action(
            db, current_user.id, 'DELETE', 'ORDER', order_id,
            {
                'soft_delete': soft_delete,
                'shards_deleted': shards_deleted
            },
            '', '', blockchain_tx_id
        )
        
        await db.commit()
        
        return success_response({
            'message': f"订单{'软删除' if soft_delete else '硬删除'}成功",
            'order_id': order_id,
            'shards_deleted': shards_deleted,
            'blockchain_tx_id': blockchain_tx_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {e}")
        await db.rollback()
        return error_response(f"删除订单失败: {str(e)}")

@router.get("/orders")
async def list_orders(
    page: int = 1,
    size: int = 20,
    data_source: str = None,
    sensitivity_level: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    services = Depends(get_services)
):
    """
    获取订单列表（基于权限过滤）
    """
    try:
        # 1. 权限检查
        permission_service = services['permission_service']
        has_permission = await permission_service.check_action_permission(
            str(current_user.id), 'read'
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有读取订单的权限"
            )
        
        # 2. 构建查询
        query = select(Order).where(Order.status == 'active')
        
        # 数据源过滤
        accessible_sources = await permission_service.get_accessible_data_sources(
            str(current_user.id)
        )
        
        if 'all' not in accessible_sources:
            query = query.where(Order.data_source.in_(accessible_sources))
        
        if data_source:
            query = query.where(Order.data_source == data_source)
        
        # 敏感度级别过滤
        if sensitivity_level:
            sensitivity_ranges = {
                'low': (0.0, 0.3),
                'medium': (0.3, 0.6),
                'high': (0.6, 0.8),
                'critical': (0.8, 1.0)
            }
            
            if sensitivity_level in sensitivity_ranges:
                min_score, max_score = sensitivity_ranges[sensitivity_level]
                query = query.where(
                    Order.sensitivity_score >= min_score,
                    Order.sensitivity_score < max_score
                )
        
        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        # 执行查询
        result = await db.execute(query)
        orders = result.scalars().all()
        
        # 3. 过滤字段
        filtered_orders = []
        for order in orders:
            order_dict = {
                'id': str(order.id),
                'order_id': order.order_id,
                'user_id': order.user_id,
                'customer_name': order.customer_name,
                'email': order.email,
                'phone': order.phone,
                'address': order.address,
                'item_list': order.item_list,
                'total_amount': float(order.total_amount) if order.total_amount else None,
                'sensitivity_score': float(order.sensitivity_score) if order.sensitivity_score else None,
                'data_source': order.data_source,
                'created_at': order.created_at.isoformat() if order.created_at else None
            }
            
            filtered_order = await permission_service.filter_order_data(
                str(current_user.id), order_dict
            )
            filtered_orders.append(filtered_order)
        
        return success_response({
            'orders': filtered_orders,
            'pagination': {
                'page': page,
                'size': size,
                'total': len(filtered_orders)
            },
            'filters': {
                'data_source': data_source,
                'sensitivity_level': sensitivity_level,
                'accessible_sources': accessible_sources
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        return error_response(f"获取订单列表失败: {str(e)}")

@router.post("/upload_csv")
async def upload_csv_orders(
    file: UploadFile = File(...),
    data_source: str = "manual",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    services = Depends(get_services)
):
    """
    批量上传CSV订单数据
    """
    try:
        # 1. 权限检查
        permission_service = services['permission_service']
        has_permission = await permission_service.check_action_permission(
            str(current_user.id), 'create'
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有创建订单的权限"
            )
        
        # 2. 验证文件格式
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持CSV文件"
            )
        
        # 3. 读取CSV文件
        contents = await file.read()
        
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV文件格式错误: {str(e)}"
            )
        
        # 4. 验证必要字段
        required_fields = ['order_id']
        missing_fields = [field for field in required_fields if field not in df.columns]
        
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"缺少必要字段: {missing_fields}"
            )
        
        # 5. 批量处理
        sensitivity_analyzer = services['sensitivity_analyzer']
        threshold_calculator = services['threshold_calculator']
        sharding_service = services['sharding_service']
        
        # 敏感度分析
        df_with_sensitivity = sensitivity_analyzer.analyze_batch(df)
        
        processed_orders = []
        failed_orders = []
        
        for _, row in df_with_sensitivity.iterrows():
            try:
                order_data = row.to_dict()
                order_data['data_source'] = data_source
                
                # 检查订单是否已存在
                existing_order = await db.execute(
                    select(Order).where(Order.order_id == order_data['order_id'])
                )
                
                if existing_order.scalar_one_or_none():
                    failed_orders.append({
                        'order_id': order_data['order_id'],
                        'error': '订单已存在'
                    })
                    continue
                
                # 创建订单
                order = Order(
                    order_id=order_data['order_id'],
                    user_id=order_data.get('user_id'),
                    customer_name=order_data.get('customer_name'),
                    email=order_data.get('email'),
                    phone=order_data.get('phone'),
                    address=order_data.get('address'),
                    item_list=order_data.get('item_list'),
                    total_amount=order_data.get('total_amount'),
                    sensitivity_score=order_data['sensitivity_score'],
                    data_source=data_source,
                    status='active'
                )
                
                db.add(order)
                await db.flush()  # 获取ID但不提交
                
                # 分片加密
                k_value = await threshold_calculator.get_current_k(order_data['sensitivity_score'])
                order_for_sharding = {**order_data, 'id': str(order.id)}
                
                shards_info = await sharding_service.encrypt_and_shard_order(
                    order_for_sharding, k_value, n=5
                )
                
                processed_orders.append({
                    'order_id': order_data['order_id'],
                    'sensitivity_score': order_data['sensitivity_score'],
                    'k_value': k_value,
                    'shards_created': len(shards_info)
                })
                
            except Exception as e:
                failed_orders.append({
                    'order_id': order_data.get('order_id', 'unknown'),
                    'error': str(e)
                })
                continue
        
        await db.commit()
        
        # 6. 记录到区块链
        blockchain_tx_id = await record_to_blockchain(
            'BATCH_UPLOAD',
            {
                'total_orders': len(df),
                'processed_orders': len(processed_orders),
                'failed_orders': len(failed_orders),
                'data_source': data_source,
                'user_id': str(current_user.id)
            }
        )
        
        return success_response({
            'processed_orders': processed_orders,
            'failed_orders': failed_orders,
            'summary': {
                'total': len(df),
                'success': len(processed_orders),
                'failed': len(failed_orders)
            },
            'blockchain_tx_id': blockchain_tx_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        await db.rollback()
        return error_response(f"CSV上传失败: {str(e)}")

# 辅助函数
async def record_to_blockchain(action: str, data: Dict[str, Any]) -> str:
    """记录操作到区块链"""
    try:
        # 调用Go后端的区块链接口
        go_backend_url = "http://backend-go:8001"  # Docker环境
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{go_backend_url}/api/v1/blockchain/record",
                json={
                    'action': action,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('transaction_id', 'unknown')
            else:
                logger.error(f"Blockchain recording failed: {response.text}")
                return 'failed'
                
    except Exception as e:
        logger.error(f"Error recording to blockchain: {e}")
        return 'error'

async def log_audit_action(
    db: AsyncSession,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Dict[str, Any],
    ip_address: str,
    user_agent: str,
    blockchain_tx_id: str
):
    """记录审计日志"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            blockchain_tx_id=blockchain_tx_id
        )
        
        db.add(audit_log)
        # 不在这里提交，让调用者决定
        
    except Exception as e:
        logger.error(f"Error logging audit action: {e}")

# 导入io模块用于CSV处理
import io
