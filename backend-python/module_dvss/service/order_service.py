"""
订单服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from ..dao.order_dao import OrderDAO
from ..schemas.order_schema import (
    OrderCreate, OrderUpdate, OrderResponse, OrderList,
    OrderEncrypt, OrderBatchEncrypt, EncryptedOrderResponse,
    OrderSensitivityAnalysis, OrderStatistics, OrderDecrypt,
    DecryptionResult, OrderFieldValue, OrderDetailWithPermissions
)
from ..schemas.common_schema import PageResponse
from ..entity.original_order import OriginalOrder
from ..entity.encrypted_order import EncryptedOrder
from ..service.encryption_service import EncryptionService
from ..service.sensitivity_service import SensitivityService
from ..service.audit_service import AuditService
from utils.response_util import success_response, error_response
from utils.crypto_util import CryptoUtil
from exceptions.custom_exception import BusinessException


class OrderService:
    """订单服务"""
    
    def __init__(self, order_dao: OrderDAO, encryption_service: EncryptionService,
                 sensitivity_service: SensitivityService, audit_service: AuditService):
        self.order_dao = order_dao
        self.encryption_service = encryption_service
        self.sensitivity_service = sensitivity_service
        self.audit_service = audit_service
    
    async def create_order(self, order_data: OrderCreate, user_id: int) -> OrderResponse:
        """创建订单"""
        try:
            # 计算敏感度分值
            sensitivity_score = await self.sensitivity_service.calculate_order_sensitivity(
                order_data.dict()
            )
            
            # 创建订单实体
            order_entity = OriginalOrder(
                order_id=order_data.order_id,
                user_id=order_data.user_id,
                name=order_data.name,
                phone=order_data.phone,
                email=order_data.email,
                address=order_data.address,
                shipping_address=order_data.shipping_address,
                billing_address=order_data.billing_address,
                zip_code=order_data.zip_code,
                city=order_data.city,
                state=order_data.state,
                country=order_data.country,
                payment_info=order_data.payment_info,
                credit_card=order_data.credit_card,
                bank_account=order_data.bank_account,
                payment_method=order_data.payment_method,
                item_list=order_data.item_list,
                item_name=order_data.item_name,
                item_price=order_data.item_price,
                quantity=order_data.quantity,
                total_amount=order_data.total_amount,
                tax_amount=order_data.tax_amount,
                shipping_cost=order_data.shipping_cost,
                discount=order_data.discount,
                sensitivity_score=sensitivity_score,
                created_by=user_id
            )
            
            # 保存订单
            order = await self.order_dao.create(order_entity)
            
            # 记录审计日志
            await self.audit_service.log_operation(
                user_id=user_id,
                operation="CREATE_ORDER",
                resource_type="ORDER",
                resource_id=str(order.id),
                details=f"创建订单: {order.order_id}"
            )
            
            return OrderResponse.from_orm(order)
        except Exception as e:
            raise BusinessException(f"创建订单失败: {str(e)}")
    
    async def get_orders(self, page: int = 1, size: int = 10, 
                        status: Optional[str] = None, user_id: Optional[str] = None) -> PageResponse[OrderList]:
        """获取订单列表"""
        try:
            filters = {}
            if status:
                filters['status'] = status
            if user_id:
                filters['user_id'] = user_id
            
            orders, total = await self.order_dao.get_list(
                page=page, size=size, filters=filters
            )
            
            order_list = [OrderList.from_orm(order) for order in orders]
            
            return PageResponse(
                items=order_list,
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        except Exception as e:
            raise BusinessException(f"获取订单列表失败: {str(e)}")
    
    async def get_order_by_id(self, order_id: int, user_id: int) -> Optional[OrderDetailWithPermissions]:
        """获取订单详情（带权限控制）"""
        try:
            order = await self.order_dao.get_by_id(order_id)
            if not order:
                return None
            
            # 获取用户对各字段的权限
            field_permissions = await self.get_field_permissions(user_id, order_id)
            
            # 构建字段值列表
            fields = []
            order_dict = order.__dict__
            
            for field_name, value in order_dict.items():
                if field_name.startswith('_') or field_name in ['id', 'created_at', 'updated_at']:
                    continue
                
                permission = field_permissions.get(field_name, {})
                can_view = permission.get('can_view', True)
                can_decrypt = permission.get('can_decrypt', False)
                
                # 如果不能查看，则脱敏处理
                display_value = value
                if not can_view and value:
                    display_value = self._mask_sensitive_data(field_name, str(value))
                
                fields.append(OrderFieldValue(
                    field_name=field_name,
                    field_value=display_value,
                    is_encrypted=order.status == 'encrypted',
                    can_view=can_view,
                    can_decrypt=can_decrypt
                ))
            
            return OrderDetailWithPermissions(
                id=order.id,
                order_id=order.order_id,
                user_id=order.user_id,
                fields=fields,
                sensitivity_score=order.sensitivity_score,
                status=order.status,
                created_at=order.created_at,
                updated_at=order.updated_at
            )
        except Exception as e:
            raise BusinessException(f"获取订单详情失败: {str(e)}")
    
    async def update_order(self, order_id: int, order_data: OrderUpdate, user_id: int) -> Optional[OrderResponse]:
        """更新订单"""
        try:
            order = await self.order_dao.get_by_id(order_id)
            if not order:
                return None
            
            # 更新字段
            update_data = {k: v for k, v in order_data.dict(exclude_unset=True).items() if v is not None}
            
            # 重新计算敏感度分值
            if update_data:
                order_dict = order.__dict__.copy()
                order_dict.update(update_data)
                sensitivity_score = await self.sensitivity_service.calculate_order_sensitivity(order_dict)
                update_data['sensitivity_score'] = sensitivity_score
            
            updated_order = await self.order_dao.update(order_id, update_data)
            
            # 记录审计日志
            await self.audit_service.log_operation(
                user_id=user_id,
                operation="UPDATE_ORDER",
                resource_type="ORDER",
                resource_id=str(order_id),
                details=f"更新订单: {order.order_id}"
            )
            
            return OrderResponse.from_orm(updated_order)
        except Exception as e:
            raise BusinessException(f"更新订单失败: {str(e)}")
    
    async def delete_order(self, order_id: int, user_id: int) -> bool:
        """删除订单（软删除）"""
        try:
            order = await self.order_dao.get_by_id(order_id)
            if not order:
                return False
            
            # 软删除
            await self.order_dao.update(order_id, {'status': 'deleted'})
            
            # 记录审计日志
            await self.audit_service.log_operation(
                user_id=user_id,
                operation="DELETE_ORDER",
                resource_type="ORDER",
                resource_id=str(order_id),
                details=f"删除订单: {order.order_id}"
            )
            
            return True
        except Exception as e:
            raise BusinessException(f"删除订单失败: {str(e)}")
    
    async def encrypt_order(self, encrypt_data: OrderEncrypt, user_id: int) -> EncryptedOrderResponse:
        """加密订单"""
        try:
            order = await self.order_dao.get_by_id(encrypt_data.order_id)
            if not order:
                raise BusinessException("订单不存在")
            
            if order.status == 'encrypted':
                raise BusinessException("订单已经加密")
            
            # 准备加密数据
            sensitive_data = {
                'name': order.name,
                'phone': order.phone,
                'email': order.email,
                'address': order.address,
                'payment_info': order.payment_info,
                'credit_card': order.credit_card,
                'bank_account': order.bank_account
            }
            
            # 执行加密
            encrypted_result = await self.encryption_service.encrypt_data(
                data=sensitive_data,
                algorithm=encrypt_data.algorithm,
                k_value=encrypt_data.k_value,
                n_value=encrypt_data.n_value
            )
            
            # 创建加密订单记录
            encrypted_order = EncryptedOrder(
                original_order_id=order.id,
                order_id=order.order_id,
                encryption_algorithm=encrypt_data.algorithm,
                k_value=encrypt_data.k_value,
                n_value=encrypt_data.n_value,
                encrypted_data=encrypted_result['encrypted_data'],
                data_hash=encrypted_result['data_hash'],
                created_by=user_id
            )
            
            encrypted_order = await self.order_dao.create_encrypted_order(encrypted_order)
            
            # 更新原始订单状态
            await self.order_dao.update(order.id, {'status': 'encrypted'})
            
            # 记录审计日志
            await self.audit_service.log_operation(
                user_id=user_id,
                operation="ENCRYPT_ORDER",
                resource_type="ORDER",
                resource_id=str(order.id),
                details=f"加密订单: {order.order_id}, 算法: {encrypt_data.algorithm}, k={encrypt_data.k_value}, n={encrypt_data.n_value}"
            )
            
            return EncryptedOrderResponse.from_orm(encrypted_order)
        except Exception as e:
            raise BusinessException(f"订单加密失败: {str(e)}")
    
    async def decrypt_order(self, decrypt_data: OrderDecrypt, user_id: int) -> DecryptionResult:
        """解密订单"""
        try:
            encrypted_order = await self.order_dao.get_encrypted_order_by_id(decrypt_data.encrypted_order_id)
            if not encrypted_order:
                raise BusinessException("加密订单不存在")
            
            # 验证用户权限
            has_permission = await self.check_decrypt_permission(user_id, encrypted_order.original_order_id)
            if not has_permission:
                raise BusinessException("无权限解密此订单")
            
            # 执行解密
            decrypted_data = await self.encryption_service.decrypt_data(
                encrypted_data=encrypted_order.encrypted_data,
                algorithm=encrypted_order.encryption_algorithm,
                k_value=encrypted_order.k_value
            )
            
            # 过滤请求的字段
            if decrypt_data.requested_fields:
                decrypted_data = {
                    k: v for k, v in decrypted_data.items() 
                    if k in decrypt_data.requested_fields
                }
            
            # 记录解密日志
            await self.audit_service.log_operation(
                user_id=user_id,
                operation="DECRYPT_ORDER",
                resource_type="ORDER",
                resource_id=str(encrypted_order.original_order_id),
                details=f"解密订单: {encrypted_order.order_id}, 原因: {decrypt_data.reason}"
            )
            
            return DecryptionResult(
                order_id=encrypted_order.order_id,
                decrypted_data=decrypted_data,
                accessed_fields=list(decrypted_data.keys()),
                decryption_time=datetime.now(),
                operator_id=str(user_id)
            )
        except Exception as e:
            raise BusinessException(f"订单解密失败: {str(e)}")
    
    async def get_order_statistics(self) -> OrderStatistics:
        """获取订单统计信息"""
        try:
            stats = await self.order_dao.get_statistics()
            return OrderStatistics(**stats)
        except Exception as e:
            raise BusinessException(f"获取订单统计失败: {str(e)}")
    
    async def analyze_order_sensitivity(self, order_id: int) -> OrderSensitivityAnalysis:
        """分析订单敏感度"""
        try:
            order = await self.order_dao.get_by_id(order_id)
            if not order:
                raise BusinessException("订单不存在")
            
            analysis_result = await self.sensitivity_service.analyze_order_sensitivity(order)
            
            return OrderSensitivityAnalysis(
                order_id=order_id,
                overall_score=analysis_result['overall_score'],
                field_scores=analysis_result['field_scores'],
                risk_level=analysis_result['risk_level'],
                recommendations=analysis_result['recommendations']
            )
        except Exception as e:
            raise BusinessException(f"订单敏感度分析失败: {str(e)}")
    
    async def batch_encrypt_orders(self, encrypt_data: OrderBatchEncrypt, user_id: int) -> List[EncryptedOrderResponse]:
        """批量加密订单"""
        results = []
        failed_orders = []
        
        for order_id in encrypt_data.order_ids:
            try:
                order_encrypt = OrderEncrypt(
                    order_id=order_id,
                    algorithm=encrypt_data.algorithm,
                    k_value=encrypt_data.k_value,
                    n_value=encrypt_data.n_value
                )
                result = await self.encrypt_order(order_encrypt, user_id)
                results.append(result)
            except Exception as e:
                failed_orders.append({'order_id': order_id, 'error': str(e)})
        
        # 记录批量操作日志
        await self.audit_service.log_operation(
            user_id=user_id,
            operation="BATCH_ENCRYPT_ORDERS",
            resource_type="ORDER",
            resource_id=",".join(map(str, encrypt_data.order_ids)),
            details=f"批量加密 {len(results)} 个订单，失败 {len(failed_orders)} 个"
        )
        
        return results
    
    async def get_field_permissions(self, user_id: int, order_id: int) -> Dict[str, Dict[str, bool]]:
        """获取用户对订单字段的权限"""
        # 这里应该根据用户角色和字段配置来确定权限
        # 暂时返回默认权限
        return {
            'name': {'can_view': True, 'can_decrypt': True},
            'phone': {'can_view': True, 'can_decrypt': True},
            'email': {'can_view': True, 'can_decrypt': True},
            'address': {'can_view': True, 'can_decrypt': False},
            'payment_info': {'can_view': False, 'can_decrypt': False},
            'credit_card': {'can_view': False, 'can_decrypt': False},
            'bank_account': {'can_view': False, 'can_decrypt': False}
        }
    
    async def check_decrypt_permission(self, user_id: int, order_id: int) -> bool:
        """检查解密权限"""
        # 这里应该根据用户角色来判断是否有解密权限
        # 暂时返回True
        return True
    
    def _mask_sensitive_data(self, field_name: str, value: str) -> str:
        """脱敏处理敏感数据"""
        if field_name in ['phone']:
            return value[:3] + '*' * 4 + value[-4:] if len(value) > 7 else '*' * len(value)
        elif field_name in ['email']:
            if '@' in value:
                local, domain = value.split('@', 1)
                return local[:2] + '*' * (len(local) - 2) + '@' + domain
            return '*' * len(value)
        elif field_name in ['credit_card', 'bank_account']:
            return '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '*' * len(value)
        elif field_name in ['address']:
            return value[:10] + '*' * (len(value) - 10) if len(value) > 10 else '*' * len(value)
        else:
            return value
