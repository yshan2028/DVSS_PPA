"""
数据敏感度分析模块
负责计算订单数据的敏感度分数
"""
import yaml
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SensitivityAnalyzer:
    """敏感度分析器"""
    
    def __init__(self, config_path: str = "/app/config/sensitivity.yaml"):
        self.config_path = config_path
        self.field_weights = {}
        self.sensitivity_levels = {}
        self.field_categories = {}
        self.load_config()
    
    def load_config(self):
        """加载敏感度配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.field_weights = config.get('field_weights', {})
            self.sensitivity_levels = config.get('sensitivity_levels', {})
            self.field_categories = config.get('field_categories', {})
            
            logger.info(f"Loaded sensitivity config from {self.config_path}")
            
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            self._set_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_default_config()
    
    def _set_default_config(self):
        """设置默认配置"""
        self.field_weights = {
            'user_id': 0.8, 'name': 0.9, 'phone': 0.9, 'email': 0.8,
            'address': 0.9, 'payment_info': 1.0, 'total_amount': 0.6,
            'order_id': 0.1, 'item_list': 0.3, 'timestamp': 0.1
        }
        self.sensitivity_levels = {
            'low': 0.3, 'medium': 0.6, 'high': 0.8, 'critical': 0.9
        }
    
    def calculate_order_sensitivity(self, order_data: Dict[str, Any]) -> float:
        """
        计算单个订单的敏感度分数
        
        Args:
            order_data: 订单数据字典
            
        Returns:
            敏感度分数 (0-1)
        """
        total_weight = 0.0
        present_weight = 0.0
        
        for field, weight in self.field_weights.items():
            total_weight += weight
            
            # 检查字段是否存在且有值
            if field in order_data and order_data[field] is not None:
                field_value = order_data[field]
                
                # 根据字段类型调整权重
                adjusted_weight = self._adjust_weight_by_content(field, field_value, weight)
                present_weight += adjusted_weight
        
        # 计算敏感度分数
        if total_weight == 0:
            return 0.0
        
        sensitivity_score = present_weight / total_weight
        return min(max(sensitivity_score, 0.0), 1.0)  # 确保在0-1范围内
    
    def _adjust_weight_by_content(self, field: str, value: Any, base_weight: float) -> float:
        """
        根据字段内容调整权重
        
        Args:
            field: 字段名
            value: 字段值
            base_weight: 基础权重
            
        Returns:
            调整后的权重
        """
        if value is None or value == "":
            return 0.0
        
        # 支付信息特殊处理
        if field == 'payment_info':
            if isinstance(value, dict):
                # 信用卡信息权重最高
                if 'credit_card' in value or 'card_number' in value:
                    return base_weight * 1.2
                elif 'bank_account' in value:
                    return base_weight * 1.1
                else:
                    return base_weight * 0.8
        
        # 地址信息长度影响权重
        elif field in ['address', 'shipping_address', 'billing_address']:
            if isinstance(value, str):
                length_factor = min(len(value) / 50, 1.2)  # 地址越详细权重越高
                return base_weight * length_factor
        
        # 联系信息格式检查
        elif field == 'phone':
            if isinstance(value, str) and len(value) >= 10:
                return base_weight
            else:
                return base_weight * 0.5
        
        elif field == 'email':
            if isinstance(value, str) and '@' in value:
                return base_weight
            else:
                return base_weight * 0.5
        
        return base_weight
    
    def get_sensitivity_level(self, score: float) -> str:
        """
        根据分数获取敏感度等级
        
        Args:
            score: 敏感度分数
            
        Returns:
            敏感度等级 (low, medium, high, critical)
        """
        if score >= self.sensitivity_levels.get('critical', 0.9):
            return 'critical'
        elif score >= self.sensitivity_levels.get('high', 0.8):
            return 'high'
        elif score >= self.sensitivity_levels.get('medium', 0.6):
            return 'medium'
        else:
            return 'low'
    
    def analyze_batch(self, orders_df: pd.DataFrame) -> pd.DataFrame:
        """
        批量分析订单敏感度
        
        Args:
            orders_df: 订单数据DataFrame
            
        Returns:
            带敏感度分数的DataFrame
        """
        sensitivity_scores = []
        sensitivity_levels = []
        
        for _, row in orders_df.iterrows():
            order_data = row.to_dict()
            score = self.calculate_order_sensitivity(order_data)
            level = self.get_sensitivity_level(score)
            
            sensitivity_scores.append(score)
            sensitivity_levels.append(level)
        
        orders_df['sensitivity_score'] = sensitivity_scores
        orders_df['sensitivity_level'] = sensitivity_levels
        
        return orders_df
    
    def get_field_categories_for_user(self, user_role: str) -> Dict[str, List[str]]:
        """
        根据用户角色获取可访问的字段分类
        
        Args:
            user_role: 用户角色
            
        Returns:
            可访问的字段分类
        """
        # 这里可以根据具体需求实现角色权限逻辑
        if user_role == 'admin':
            return self.field_categories
        elif user_role == 'analyst':
            # 分析师不能访问PII和金融信息
            return {k: v for k, v in self.field_categories.items() 
                   if k not in ['pii', 'financial']}
        elif user_role == 'viewer':
            # 查看者只能访问业务信息
            return {k: v for k, v in self.field_categories.items() 
                   if k == 'business'}
        else:
            return {}
    
    def filter_fields_by_permission(self, order_data: Dict[str, Any], 
                                   allowed_fields: List[str]) -> Dict[str, Any]:
        """
        根据权限过滤订单字段
        
        Args:
            order_data: 原始订单数据
            allowed_fields: 允许访问的字段列表
            
        Returns:
            过滤后的订单数据
        """
        filtered_data = {}
        
        for field, value in order_data.items():
            if field in allowed_fields:
                filtered_data[field] = value
            else:
                # 对敏感字段进行脱敏处理
                filtered_data[field] = self._mask_sensitive_field(field, value)
        
        return filtered_data
    
    def _mask_sensitive_field(self, field: str, value: Any) -> str:
        """
        对敏感字段进行脱敏处理
        
        Args:
            field: 字段名
            value: 字段值
            
        Returns:
            脱敏后的值
        """
        if value is None:
            return None
        
        if field in ['phone']:
            if isinstance(value, str) and len(value) >= 7:
                return value[:3] + '****' + value[-4:]
        elif field in ['email']:
            if isinstance(value, str) and '@' in value:
                parts = value.split('@')
                return parts[0][:2] + '***@' + parts[1]
        elif field in ['name', 'customer_name']:
            if isinstance(value, str) and len(value) >= 2:
                return value[0] + '*' * (len(value) - 1)
        elif field in ['address', 'shipping_address', 'billing_address']:
            return '***隐藏***'
        elif field in ['payment_info']:
            return '***隐藏***'
        
        return '***'
    
    def export_sensitivity_report(self, orders_df: pd.DataFrame, 
                                 output_path: str = None) -> Dict[str, Any]:
        """
        导出敏感度分析报告
        
        Args:
            orders_df: 订单数据DataFrame
            output_path: 输出文件路径
            
        Returns:
            分析报告
        """
        if 'sensitivity_score' not in orders_df.columns:
            orders_df = self.analyze_batch(orders_df)
        
        report = {
            'total_orders': len(orders_df),
            'average_sensitivity': orders_df['sensitivity_score'].mean(),
            'sensitivity_distribution': {
                'critical': len(orders_df[orders_df['sensitivity_score'] >= 0.9]),
                'high': len(orders_df[(orders_df['sensitivity_score'] >= 0.8) & 
                                    (orders_df['sensitivity_score'] < 0.9)]),
                'medium': len(orders_df[(orders_df['sensitivity_score'] >= 0.6) & 
                                      (orders_df['sensitivity_score'] < 0.8)]),
                'low': len(orders_df[orders_df['sensitivity_score'] < 0.6])
            },
            'top_sensitive_orders': orders_df.nlargest(10, 'sensitivity_score')[
                ['order_id', 'sensitivity_score']].to_dict('records'),
            'field_analysis': self._analyze_field_presence(orders_df)
        }
        
        if output_path:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return report
    
    def _analyze_field_presence(self, orders_df: pd.DataFrame) -> Dict[str, Dict]:
        """分析字段存在情况"""
        field_analysis = {}
        
        for field in self.field_weights.keys():
            if field in orders_df.columns:
                non_null_count = orders_df[field].notna().sum()
                presence_rate = non_null_count / len(orders_df)
                
                field_analysis[field] = {
                    'presence_rate': presence_rate,
                    'weight': self.field_weights[field],
                    'impact': presence_rate * self.field_weights[field]
                }
        
        return field_analysis
