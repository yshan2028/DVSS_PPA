"""
权限管理和数据字段过滤服务
负责基于用户角色的字段级访问控制
"""
import logging
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import User, Role
import json

logger = logging.getLogger(__name__)

class PermissionService:
    """权限管理服务"""
    
    def __init__(self, postgres_session):
        self.postgres_session = postgres_session
        
        # 预定义角色权限
        self.role_permissions = {
            'admin': {
                'all_fields': True,
                'actions': ['create', 'read', 'update', 'delete', 'encrypt', 'decrypt', 'manage_users'],
                'data_sources': ['all']
            },
            'analyst': {
                'allowed_fields': [
                    'order_id', 'item_list', 'total_amount', 'tax_amount', 
                    'shipping_cost', 'discount', 'timestamp', 'data_source',
                    'sensitivity_score'
                ],
                'denied_fields': [
                    'customer_name', 'phone', 'email', 'address', 
                    'shipping_address', 'billing_address', 'payment_info', 'user_id'
                ],
                'actions': ['read', 'analyze'],
                'data_sources': ['alibaba', 'weee']
            },
            'viewer': {
                'allowed_fields': [
                    'order_id', 'item_list', 'timestamp', 'data_source'
                ],
                'denied_fields': [
                    'customer_name', 'phone', 'email', 'address', 
                    'shipping_address', 'billing_address', 'payment_info', 
                    'user_id', 'total_amount', 'tax_amount', 'payment_info'
                ],
                'actions': ['read'],
                'data_sources': ['alibaba', 'weee']
            },
            'finance': {
                'allowed_fields': [
                    'order_id', 'total_amount', 'tax_amount', 'shipping_cost',
                    'discount', 'timestamp', 'data_source', 'payment_info'
                ],
                'denied_fields': [
                    'customer_name', 'phone', 'email', 'address', 
                    'shipping_address', 'billing_address', 'user_id'
                ],
                'actions': ['read', 'financial_analysis'],
                'data_sources': ['alibaba', 'weee']
            }
        }
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户权限信息
        """
        try:
            async with self.postgres_session() as session:
                # 查询用户及其角色
                result = await session.execute(
                    select(User, Role)
                    .join(Role, User.role_id == Role.id)
                    .where(User.id == user_id)
                    .where(User.is_active == True)
                )
                
                user_role = result.first()
                
                if not user_role:
                    return {'error': 'User not found or inactive'}
                
                user, role = user_role
                
                # 获取角色权限
                base_permissions = self.role_permissions.get(role.name, {})
                
                # 如果角色有自定义权限配置，使用数据库中的配置
                if role.field_access:
                    custom_permissions = role.field_access
                    # 合并基础权限和自定义权限
                    permissions = {**base_permissions, **custom_permissions}
                else:
                    permissions = base_permissions
                
                return {
                    'user_id': str(user.id),
                    'username': user.username,
                    'role': role.name,
                    'permissions': permissions,
                    'department': user.department
                }
                
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return {'error': str(e)}
    
    async def check_field_access(self, user_id: str, field_name: str) -> bool:
        """
        检查用户是否有访问特定字段的权限
        
        Args:
            user_id: 用户ID
            field_name: 字段名
            
        Returns:
            是否有权限
        """
        permissions = await self.get_user_permissions(user_id)
        
        if 'error' in permissions:
            return False
        
        user_permissions = permissions.get('permissions', {})
        
        # 管理员有所有权限
        if user_permissions.get('all_fields', False):
            return True
        
        # 检查允许的字段
        allowed_fields = user_permissions.get('allowed_fields', [])
        if field_name in allowed_fields:
            return True
        
        # 检查拒绝的字段
        denied_fields = user_permissions.get('denied_fields', [])
        if field_name in denied_fields:
            return False
        
        # 默认允许（如果字段不在任何列表中）
        return True
    
    async def check_action_permission(self, user_id: str, action: str) -> bool:
        """
        检查用户是否有执行特定操作的权限
        
        Args:
            user_id: 用户ID
            action: 操作名称
            
        Returns:
            是否有权限
        """
        permissions = await self.get_user_permissions(user_id)
        
        if 'error' in permissions:
            return False
        
        user_permissions = permissions.get('permissions', {})
        allowed_actions = user_permissions.get('actions', [])
        
        return action in allowed_actions
    
    async def filter_order_data(self, user_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据用户权限过滤订单数据
        
        Args:
            user_id: 用户ID
            order_data: 原始订单数据
            
        Returns:
            过滤后的订单数据
        """
        permissions = await self.get_user_permissions(user_id)
        
        if 'error' in permissions:
            return {'error': permissions['error']}
        
        user_permissions = permissions.get('permissions', {})
        
        # 管理员返回所有数据
        if user_permissions.get('all_fields', False):
            return order_data
        
        filtered_data = {}
        allowed_fields = user_permissions.get('allowed_fields', [])
        denied_fields = user_permissions.get('denied_fields', [])
        
        for field, value in order_data.items():
            if self._is_field_allowed(field, allowed_fields, denied_fields):
                filtered_data[field] = value
            else:
                # 对敏感字段进行脱敏处理
                filtered_data[field] = self._mask_sensitive_field(field, value)
        
        return filtered_data
    
    def _is_field_allowed(self, field: str, allowed_fields: List[str], denied_fields: List[str]) -> bool:
        """检查字段是否被允许"""
        # 如果有允许列表，字段必须在其中
        if allowed_fields and field not in allowed_fields:
            return False
        
        # 如果在拒绝列表中，不允许
        if field in denied_fields:
            return False
        
        return True
    
    def _mask_sensitive_field(self, field: str, value: Any) -> str:
        """对敏感字段进行脱敏处理"""
        if value is None:
            return None
        
        # 脱敏规则
        masking_rules = {
            'customer_name': lambda v: self._mask_name(v),
            'phone': lambda v: self._mask_phone(v),
            'email': lambda v: self._mask_email(v),
            'address': lambda v: '***地址已隐藏***',
            'shipping_address': lambda v: '***地址已隐藏***',
            'billing_address': lambda v: '***地址已隐藏***',
            'payment_info': lambda v: '***支付信息已隐藏***',
            'user_id': lambda v: self._mask_user_id(v),
            'total_amount': lambda v: '***金额已隐藏***',
            'tax_amount': lambda v: '***金额已隐藏***'
        }
        
        if field in masking_rules:
            try:
                return masking_rules[field](value)
            except:
                return '***已隐藏***'
        
        return '***已隐藏***'
    
    def _mask_name(self, name: str) -> str:
        """脱敏姓名"""
        if isinstance(name, str) and len(name) >= 2:
            return name[0] + '*' * (len(name) - 1)
        return '***'
    
    def _mask_phone(self, phone: str) -> str:
        """脱敏电话号码"""
        if isinstance(phone, str) and len(phone) >= 7:
            return phone[:3] + '****' + phone[-4:]
        return '***'
    
    def _mask_email(self, email: str) -> str:
        """脱敏邮箱"""
        if isinstance(email, str) and '@' in email:
            parts = email.split('@')
            if len(parts[0]) >= 2:
                return parts[0][:2] + '***@' + parts[1]
        return '***'
    
    def _mask_user_id(self, user_id: str) -> str:
        """脱敏用户ID"""
        if isinstance(user_id, str) and len(user_id) >= 6:
            return user_id[:3] + '***' + user_id[-3:]
        return '***'
    
    async def get_accessible_data_sources(self, user_id: str) -> List[str]:
        """
        获取用户可访问的数据源
        
        Args:
            user_id: 用户ID
            
        Returns:
            可访问的数据源列表
        """
        permissions = await self.get_user_permissions(user_id)
        
        if 'error' in permissions:
            return []
        
        user_permissions = permissions.get('permissions', {})
        data_sources = user_permissions.get('data_sources', [])
        
        if 'all' in data_sources:
            return ['alibaba', 'weee', 'manual']  # 所有支持的数据源
        
        return data_sources
    
    async def filter_orders_by_permission(self, user_id: str, 
                                        orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据权限过滤订单列表
        
        Args:
            user_id: 用户ID
            orders: 订单列表
            
        Returns:
            过滤后的订单列表
        """
        # 获取可访问的数据源
        accessible_sources = await self.get_accessible_data_sources(user_id)
        
        filtered_orders = []
        
        for order in orders:
            # 检查数据源权限
            order_source = order.get('data_source', 'unknown')
            if order_source not in accessible_sources and 'all' not in accessible_sources:
                continue
            
            # 过滤字段
            filtered_order = await self.filter_order_data(user_id, order)
            
            if 'error' not in filtered_order:
                filtered_orders.append(filtered_order)
        
        return filtered_orders
    
    async def create_permission_report(self, user_id: str) -> Dict[str, Any]:
        """
        创建用户权限报告
        
        Args:
            user_id: 用户ID
            
        Returns:
            权限报告
        """
        permissions = await self.get_user_permissions(user_id)
        
        if 'error' in permissions:
            return permissions
        
        user_permissions = permissions.get('permissions', {})
        
        # 统计权限情况
        total_fields = [
            'order_id', 'user_id', 'customer_name', 'email', 'phone',
            'address', 'shipping_address', 'billing_address', 'item_list',
            'payment_info', 'total_amount', 'tax_amount', 'shipping_cost',
            'discount', 'sensitivity_score', 'data_source', 'timestamp'
        ]
        
        accessible_fields = []
        masked_fields = []
        
        for field in total_fields:
            allowed_fields = user_permissions.get('allowed_fields', [])
            denied_fields = user_permissions.get('denied_fields', [])
            
            if self._is_field_allowed(field, allowed_fields, denied_fields):
                accessible_fields.append(field)
            else:
                masked_fields.append(field)
        
        return {
            'user_info': {
                'user_id': permissions['user_id'],
                'username': permissions['username'],
                'role': permissions['role'],
                'department': permissions.get('department')
            },
            'field_access': {
                'total_fields': len(total_fields),
                'accessible_fields': accessible_fields,
                'accessible_count': len(accessible_fields),
                'masked_fields': masked_fields,
                'masked_count': len(masked_fields),
                'access_percentage': round(len(accessible_fields) / len(total_fields) * 100, 2)
            },
            'allowed_actions': user_permissions.get('actions', []),
            'data_sources': user_permissions.get('data_sources', []),
            'generated_at': logger.info.__module__  # 使用当前时间的简单替代
        }

class DataMaskingService:
    """数据脱敏服务"""
    
    def __init__(self):
        self.masking_strategies = {
            'name': self._mask_name,
            'phone': self._mask_phone,
            'email': self._mask_email,
            'address': self._mask_address,
            'payment': self._mask_payment,
            'id': self._mask_id,
            'amount': self._mask_amount
        }
    
    def apply_masking(self, data: Dict[str, Any], 
                     masking_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        应用脱敏规则
        
        Args:
            data: 原始数据
            masking_rules: 脱敏规则 {field_name: strategy}
            
        Returns:
            脱敏后的数据
        """
        masked_data = data.copy()
        
        for field, strategy in masking_rules.items():
            if field in masked_data and strategy in self.masking_strategies:
                masked_data[field] = self.masking_strategies[strategy](masked_data[field])
        
        return masked_data
    
    def _mask_name(self, value: Any) -> str:
        """脱敏姓名"""
        if not isinstance(value, str) or len(value) < 2:
            return '***'
        return value[0] + '*' * (len(value) - 1)
    
    def _mask_phone(self, value: Any) -> str:
        """脱敏电话"""
        if not isinstance(value, str) or len(value) < 7:
            return '***'
        return value[:3] + '****' + value[-4:]
    
    def _mask_email(self, value: Any) -> str:
        """脱敏邮箱"""
        if not isinstance(value, str) or '@' not in value:
            return '***'
        parts = value.split('@')
        if len(parts[0]) >= 2:
            return parts[0][:2] + '***@' + parts[1]
        return '***@' + parts[1]
    
    def _mask_address(self, value: Any) -> str:
        """脱敏地址"""
        return '***地址已隐藏***'
    
    def _mask_payment(self, value: Any) -> str:
        """脱敏支付信息"""
        return '***支付信息已隐藏***'
    
    def _mask_id(self, value: Any) -> str:
        """脱敏ID"""
        if not isinstance(value, str) or len(value) < 6:
            return '***'
        return value[:3] + '***' + value[-3:]
    
    def _mask_amount(self, value: Any) -> str:
        """脱敏金额"""
        return '***金额已隐藏***'
