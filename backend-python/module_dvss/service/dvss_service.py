"""
DVSS核心服务层
Service Layer - 处理DVSS核心业务逻辑，包括订单处理、分片、加密等
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import pandas as pd
import json
import asyncio

from module_dvss.dao.order_dao import OrderDao
from module_dvss.dao.shard_dao import ShardDao
from module_dvss.dao.user_dao import UserDao
from module_dvss.dao.field_dao import FieldDao
from module_dvss.dao.log_dao import LogDao
from module_dvss.service.encryption_service import EncryptionService
from module_dvss.service.sensitivity_service import SensitivityService
from module_dvss.service.audit_service import AuditService
from module_dvss.schemas.order_schema import (
    OrderCreateRequest, OrderResponse, OrderQueryRequest,
    OrderDeleteRequest, OrderBatchRequest
)
from module_dvss.schemas.shard_schema import ShardCreateRequest, ShardResponse
from module_dvss.schemas.common_schema import PageRequest, PageResponse
from module_dvss.entity.original_order import OriginalOrder
from module_dvss.entity.encrypted_order import EncryptedOrder
from module_dvss.entity.shard_info import ShardInfo
from exceptions.custom_exception import NotFoundError, ValidationError, AuthorizationError
from utils.log_util import LogUtil
from utils.crypto_util import CryptoUtil

logger = LogUtil.get_logger("dvss_service")

class DVSSService:
    """DVSS核心服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.order_dao = OrderDao(db)
        self.shard_dao = ShardDao(db)
        self.user_dao = UserDao(db)
        self.field_dao = FieldDao(db)
        self.log_dao = LogDao(db)
        self.encryption_service = EncryptionService(db)
        self.sensitivity_service = SensitivityService(db)
        self.audit_service = AuditService(db)
        self.crypto_util = CryptoUtil()
    
    async def process_order_upload(self, file_data: bytes, filename: str, current_user_id: int) -> Dict[str, Any]:
        """
        处理订单文件上传
        
        Args:
            file_data: 文件数据
            filename: 文件名
            current_user_id: 当前用户ID
            
        Returns:
            Dict: 处理结果
        """
        try:
            logger.info(f"用户 {current_user_id} 开始上传订单文件: {filename}")
            
            # 解析文件数据
            orders_data = await self._parse_order_file(file_data, filename)
            
            # 验证订单数据
            validated_orders = await self._validate_orders(orders_data, current_user_id)
            
            # 敏感度分析
            sensitivity_results = await self.sensitivity_service.analyze_orders(validated_orders)
            
            # 加密处理
            encrypted_orders = await self.encryption_service.encrypt_orders(
                validated_orders, sensitivity_results
            )
            
            # 数据分片
            shard_results = await self._create_shards(encrypted_orders, current_user_id)
            
            # 保存到数据库
            saved_orders = await self._save_orders(encrypted_orders, current_user_id)
            
            # 记录审计日志
            await self.audit_service.log_order_upload(
                user_id=current_user_id,
                order_count=len(saved_orders),
                filename=filename,
                details={
                    'sensitivity_results': sensitivity_results,
                    'shard_count': len(shard_results)
                }
            )
            
            result = {
                'order_count': len(saved_orders),
                'encrypted_count': len(encrypted_orders),
                'shard_count': len(shard_results),
                'sensitivity_stats': sensitivity_results.get('stats', {}),
                'upload_time': datetime.now().isoformat()
            }
            
            logger.info(f"用户 {current_user_id} 订单上传完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"订单上传失败: {str(e)}")
            await self.audit_service.log_error(
                user_id=current_user_id,
                operation="order_upload",
                error=str(e),
                details={'filename': filename}
            )
            raise
    
    async def query_orders(self, request: OrderQueryRequest, current_user_id: int) -> PageResponse:
        """
        查询订单
        
        Args:
            request: 查询请求
            current_user_id: 当前用户ID
            
        Returns:
            PageResponse: 查询结果
        """
        try:
            logger.info(f"用户 {current_user_id} 开始查询订单")
            
            # 权限检查
            await self._check_query_permission(request, current_user_id)
            
            # 执行查询
            orders, total = await self.order_dao.query_orders(
                page_request=request.page,
                filters=request.filters,
                user_id=current_user_id
            )
            
            # 解密敏感字段（如果有权限）
            decrypted_orders = await self._decrypt_order_fields(orders, current_user_id)
            
            # 记录查询日志
            await self.audit_service.log_order_query(
                user_id=current_user_id,
                query_params=request.dict(),
                result_count=len(orders)
            )
            
            return PageResponse(
                items=decrypted_orders,
                total=total,
                page=request.page.page,
                size=request.page.size
            )
            
        except Exception as e:
            logger.error(f"订单查询失败: {str(e)}")
            raise
    
    async def delete_orders(self, request: OrderDeleteRequest, current_user_id: int) -> Dict[str, Any]:
        """
        删除订单
        
        Args:
            request: 删除请求
            current_user_id: 当前用户ID
            
        Returns:
            Dict: 删除结果
        """
        try:
            logger.info(f"用户 {current_user_id} 开始删除订单")
            
            # 权限检查
            await self._check_delete_permission(request.order_ids, current_user_id)
            
            # 获取要删除的订单信息
            orders_to_delete = await self.order_dao.get_orders_by_ids(request.order_ids)
            
            # 删除相关分片
            await self._delete_order_shards(request.order_ids)
            
            # 删除订单
            deleted_count = await self.order_dao.delete_orders(request.order_ids)
            
            # 记录删除日志
            await self.audit_service.log_order_deletion(
                user_id=current_user_id,
                order_ids=request.order_ids,
                deleted_count=deleted_count
            )
            
            result = {
                'deleted_count': deleted_count,
                'order_ids': request.order_ids,
                'delete_time': datetime.now().isoformat()
            }
            
            logger.info(f"用户 {current_user_id} 订单删除完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"订单删除失败: {str(e)}")
            raise
    
    async def get_statistics(self, current_user_id: int) -> Dict[str, Any]:
        """
        获取DVSS统计信息
        
        Args:
            current_user_id: 当前用户ID
            
        Returns:
            Dict: 统计信息
        """
        try:
            # 获取订单统计
            order_stats = await self.order_dao.get_order_statistics(current_user_id)
            
            # 获取分片统计
            shard_stats = await self.shard_dao.get_shard_statistics(current_user_id)
            
            # 获取加密统计
            encryption_stats = await self.encryption_service.get_encryption_statistics()
            
            # 获取敏感度统计
            sensitivity_stats = await self.sensitivity_service.get_sensitivity_statistics()
            
            return {
                'orders': order_stats,
                'shards': shard_stats,
                'encryption': encryption_stats,
                'sensitivity': sensitivity_stats,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise
    
    async def _parse_order_file(self, file_data: bytes, filename: str) -> List[Dict[str, Any]]:
        """解析订单文件"""
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file_data)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_data)
            else:
                raise ValidationError("不支持的文件格式")
            
            return df.to_dict('records')
            
        except Exception as e:
            raise ValidationError(f"文件解析失败: {str(e)}")
    
    async def _validate_orders(self, orders_data: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
        """验证订单数据"""
        validated_orders = []
        
        for order_data in orders_data:
            # 基本字段验证
            if not order_data.get('order_id'):
                raise ValidationError("订单ID不能为空")
            
            # 字段配置验证
            field_configs = await self.field_dao.get_active_fields()
            for field_config in field_configs:
                field_name = field_config.field_name
                if field_config.is_required and not order_data.get(field_name):
                    raise ValidationError(f"必填字段 {field_name} 不能为空")
            
            validated_orders.append(order_data)
        
        return validated_orders
    
    async def _create_shards(self, encrypted_orders: List[Dict[str, Any]], user_id: int) -> List[ShardInfo]:
        """创建数据分片"""
        shards = []
        
        # 根据配置创建分片
        shard_size = 1000  # 每个分片的订单数量
        for i in range(0, len(encrypted_orders), shard_size):
            shard_data = encrypted_orders[i:i + shard_size]
            
            shard_request = ShardCreateRequest(
                order_ids=[order['order_id'] for order in shard_data],
                shard_type="data",
                metadata={
                    'order_count': len(shard_data),
                    'created_by': user_id
                }
            )
            
            shard = await self.shard_dao.create_shard(shard_request.dict(), user_id)
            shards.append(shard)
        
        return shards
    
    async def _save_orders(self, encrypted_orders: List[Dict[str, Any]], user_id: int) -> List[EncryptedOrder]:
        """保存加密订单"""
        saved_orders = []
        
        for order_data in encrypted_orders:
            order_request = OrderCreateRequest(
                order_id=order_data['order_id'],
                encrypted_data=order_data,
                user_id=user_id
            )
            
            saved_order = await self.order_dao.create_order(order_request.dict())
            saved_orders.append(saved_order)
        
        return saved_orders
    
    async def _check_query_permission(self, request: OrderQueryRequest, user_id: int):
        """检查查询权限"""
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthorizationError("用户不存在")
        
        # 根据用户角色检查权限
        if user.role.name not in ['admin', 'data_analyst']:
            # 普通用户只能查询自己的数据
            if request.filters and request.filters.get('user_id') != user_id:
                raise AuthorizationError("无权限查询其他用户的数据")
    
    async def _check_delete_permission(self, order_ids: List[str], user_id: int):
        """检查删除权限"""
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthorizationError("用户不存在")
        
        # 只有管理员可以删除数据
        if user.role.name != 'admin':
            raise AuthorizationError("无权限删除数据")
    
    async def _decrypt_order_fields(self, orders: List[EncryptedOrder], user_id: int) -> List[Dict[str, Any]]:
        """解密订单字段（根据权限）"""
        user = await self.user_dao.get_user_by_id(user_id)
        decrypted_orders = []
        
        for order in orders:
            order_dict = {
                'id': order.id,
                'order_id': order.order_id,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }
            
            # 根据用户权限解密字段
            if user.role.name == 'admin':
                # 管理员可以看到所有字段
                order_dict.update(await self.encryption_service.decrypt_order(order))
            else:
                # 其他用户只能看到非敏感字段
                order_dict.update(await self.encryption_service.decrypt_non_sensitive_fields(order))
            
            decrypted_orders.append(order_dict)
        
        return decrypted_orders
    
    async def _delete_order_shards(self, order_ids: List[str]):
        """删除订单相关的分片"""
        for order_id in order_ids:
            shards = await self.shard_dao.get_shards_by_order_id(order_id)
            for shard in shards:
                await self.shard_dao.delete_shard(shard.id)
