"""
敏感度分析服务
"""

import re

from datetime import datetime
from typing import Any, Dict, List, Optional

from exceptions.custom_exception import DVSSException
from module_dvss.dao.field_dao import FieldDAO


class SensitivityService:
    """敏感度分析服务"""

    def __init__(self, field_dao: FieldDAO):
        self.field_dao = field_dao
        self.pii_patterns = {
            'phone': r'(\+?1[-.\s]?)?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'bank_account': r'\b\d{8,17}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'driver_license': r'\b[A-Z]{1,2}\d{6,8}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'date_of_birth': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'address': (
                r'\b\d+\s+[\w\s]+(?:st|street|ave|avenue|rd|road|blvd|boulevard|'
                r'dr|drive|ln|lane|ct|court|pl|place)\b'
            ),
        }

        self.sensitivity_weights = {
            'pii': 0.8,  # 个人身份信息
            'financial': 0.9,  # 金融信息
            'health': 0.95,  # 健康信息
            'location': 0.7,  # 位置信息
            'contact': 0.6,  # 联系信息
            'biometric': 1.0,  # 生物特征
            'business': 0.5,  # 商业信息
            'system': 0.4,  # 系统信息
        }

        self.field_categories = {
            'name': 'pii',
            'first_name': 'pii',
            'last_name': 'pii',
            'full_name': 'pii',
            'phone': 'contact',
            'email': 'contact',
            'address': 'location',
            'shipping_address': 'location',
            'billing_address': 'location',
            'zip_code': 'location',
            'city': 'location',
            'state': 'location',
            'country': 'location',
            'credit_card': 'financial',
            'bank_account': 'financial',
            'payment_info': 'financial',
            'ssn': 'pii',
            'passport': 'pii',
            'driver_license': 'pii',
            'date_of_birth': 'pii',
            'medical_record': 'health',
            'diagnosis': 'health',
            'prescription': 'health',
            'fingerprint': 'biometric',
            'facial_image': 'biometric',
            'voice_print': 'biometric',
            'company': 'business',
            'department': 'business',
            'salary': 'financial',
            'password': 'system',
            'api_key': 'system',
            'token': 'system',
        }

    async def calculate_order_sensitivity(self, order_data: Dict[str, Any]) -> float:
        """计算订单整体敏感度分值"""
        try:
            total_score = 0.0
            field_count = 0
            field_scores = {}

            for field_name, field_value in order_data.items():
                if field_value is None or field_name.startswith('_'):
                    continue

                # 计算字段敏感度
                field_score = await self.calculate_field_sensitivity(field_name, field_value)
                field_scores[field_name] = field_score

                total_score += field_score
                field_count += 1

            # 计算平均分值
            if field_count == 0:
                return 0.0

            average_score = total_score / field_count

            # 应用数据量调整因子（数据越多，敏感度稍微提高）
            volume_factor = min(1.1, 1.0 + (field_count - 5) * 0.01)

            # 应用关联性调整（多个高敏感度字段同时存在时提高分值）
            high_sensitivity_fields = [score for score in field_scores.values() if score > 0.7]
            if len(high_sensitivity_fields) >= 3:
                correlation_factor = 1.1
            elif len(high_sensitivity_fields) >= 2:
                correlation_factor = 1.05
            else:
                correlation_factor = 1.0

            final_score = min(1.0, average_score * volume_factor * correlation_factor)

            return round(final_score, 3)

        except Exception as e:
            raise DVSSException(f'计算订单敏感度失败: {str(e)}')

    async def calculate_field_sensitivity(self, field_name: str, field_value: Any) -> float:
        """计算单个字段的敏感度分值"""
        try:
            if field_value is None:
                return 0.0

            # 首先查看是否有预定义的字段配置
            field_config = await self.get_field_config(field_name)
            if field_config:
                return field_config.sensitivity_score

            # 基于字段名称的敏感度
            name_score = await self._analyze_field_name_sensitivity(field_name)

            # 基于字段值的敏感度
            value_score = await self._analyze_field_value_sensitivity(str(field_value))

            # 取较高的分值
            final_score = max(name_score, value_score)

            return min(1.0, final_score)

        except Exception:
            return 0.5  # 默认中等敏感度

    async def _analyze_field_name_sensitivity(self, field_name: str) -> float:
        """基于字段名称分析敏感度"""
        field_name_lower = field_name.lower()

        # 检查是否匹配预定义类别
        category = self.field_categories.get(field_name_lower)
        if category:
            return self.sensitivity_weights[category]

        # 基于关键词匹配
        high_sensitivity_keywords = [
            'password',
            'secret',
            'private',
            'confidential',
            'classified',
            'ssn',
            'social_security',
            'tax_id',
            'passport',
            'license',
            'credit',
            'debit',
            'account',
            'routing',
            'bank',
            'payment',
            'medical',
            'health',
            'diagnosis',
            'prescription',
            'treatment',
            'biometric',
            'fingerprint',
            'facial',
            'retina',
            'voice',
        ]

        medium_sensitivity_keywords = [
            'name',
            'phone',
            'email',
            'address',
            'location',
            'contact',
            'birth',
            'age',
            'gender',
            'marital',
            'occupation',
            'company',
            'salary',
            'income',
            'education',
            'religion',
            'ethnicity',
        ]

        low_sensitivity_keywords = [
            'id',
            'number',
            'code',
            'reference',
            'status',
            'type',
            'date',
            'time',
            'amount',
            'quantity',
            'description',
            'notes',
        ]

        for keyword in high_sensitivity_keywords:
            if keyword in field_name_lower:
                return 0.9

        for keyword in medium_sensitivity_keywords:
            if keyword in field_name_lower:
                return 0.6

        for keyword in low_sensitivity_keywords:
            if keyword in field_name_lower:
                return 0.3

        return 0.5  # 默认中等敏感度

    async def _analyze_field_value_sensitivity(self, field_value: str) -> float:
        """基于字段值分析敏感度"""
        if not field_value or len(field_value.strip()) == 0:
            return 0.0

        max_score = 0.0

        # 使用正则表达式检测敏感信息模式
        for pattern_name, pattern in self.pii_patterns.items():
            if re.search(pattern, field_value, re.IGNORECASE):
                if pattern_name in ['ssn', 'credit_card', 'bank_account']:
                    max_score = max(max_score, 0.95)
                elif pattern_name in ['phone', 'email']:
                    max_score = max(max_score, 0.7)
                elif pattern_name in ['address', 'date_of_birth']:
                    max_score = max(max_score, 0.6)
                else:
                    max_score = max(max_score, 0.5)

        # 检测其他敏感模式
        sensitive_patterns = [
            (r'\b(?:visa|mastercard|amex|discover)\b', 0.9),
            (r'\b(?:password|secret|private|confidential)\b', 0.95),
            (r'\b(?:admin|administrator|root|system)\b', 0.8),
            (r'\b\d{3}-\d{2}-\d{4}\b', 0.95),  # SSN格式
            (r'\b[A-Z]{2}\d{6,9}\b', 0.8),  # 护照号格式
        ]

        for pattern, score in sensitive_patterns:
            if re.search(pattern, field_value, re.IGNORECASE):
                max_score = max(max_score, score)

        # 基于长度和复杂性的启发式分析
        if len(field_value) > 100:
            max_score = max(max_score, 0.4)  # 长文本可能包含敏感信息

        return max_score

    async def analyze_order_sensitivity(self, order) -> Dict[str, Any]:
        """分析订单敏感度（详细分析）"""
        try:
            order_dict = order.__dict__ if hasattr(order, '__dict__') else order

            field_scores = {}
            risk_factors = []
            recommendations = []

            for field_name, field_value in order_dict.items():
                if field_name.startswith('_') or field_value is None:
                    continue

                field_score = await self.calculate_field_sensitivity(field_name, field_value)
                field_scores[field_name] = field_score

                # 收集风险因素
                if field_score >= 0.8:
                    risk_factors.append(f'高敏感度字段: {field_name}')
                    recommendations.append(f'建议对字段 {field_name} 进行加密保护')

            # 计算整体敏感度
            overall_score = await self.calculate_order_sensitivity(order_dict)

            # 确定风险等级
            if overall_score >= 0.8:
                risk_level = '高风险'
                recommendations.append('建议立即进行数据加密和分片存储')
                recommendations.append('限制访问权限，仅授权人员可查看')
            elif overall_score >= 0.6:
                risk_level = '中风险'
                recommendations.append('建议对敏感字段进行脱敏处理')
                recommendations.append('实施访问控制和审计日志')
            elif overall_score >= 0.3:
                risk_level = '低风险'
                recommendations.append('建议定期检查数据访问情况')
            else:
                risk_level = '极低风险'
                recommendations.append('继续保持数据保护措施')

            # 检查数据关联风险
            if self._has_identity_linkage_risk(field_scores):
                risk_factors.append('存在身份关联风险')
                recommendations.append('避免同时存储多个身份标识符')

            return {
                'overall_score': overall_score,
                'field_scores': field_scores,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': list(set(recommendations)),  # 去重
            }

        except Exception as e:
            raise DVSSException(f'订单敏感度分析失败: {str(e)}')

    async def analyze_orders(self, orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分析订单的敏感度"""
        results = []
        for order in orders:
            sensitivity_score = await self.analyze_data_sensitivity(order)
            results.append({
                'order_id': order.get('id', order.get('order_id')),
                'sensitivity_score': sensitivity_score['overall_score'],
                'sensitive_fields': sensitivity_score['sensitive_fields'],
                'risk_level': self._get_risk_level(sensitivity_score['overall_score']),
            })
        return results

    async def get_sensitivity_statistics(self) -> Dict[str, Any]:
        """获取敏感度统计信息"""
        return {
            'total_analyzed_orders': 0,
            'high_sensitivity_count': 0,
            'medium_sensitivity_count': 0,
            'low_sensitivity_count': 0,
            'avg_sensitivity_score': 0.0,
        }

    def _get_risk_level(self, score: float) -> str:
        """根据敏感度分数获取风险等级"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'

    def _has_identity_linkage_risk(self, field_scores: Dict[str, float]) -> bool:
        """检查是否存在身份关联风险"""
        identity_fields = ['name', 'phone', 'email', 'address', 'ssn', 'credit_card']
        high_score_identity_fields = 0

        for field_name, score in field_scores.items():
            if any(identity_field in field_name.lower() for identity_field in identity_fields):
                if score >= 0.6:
                    high_score_identity_fields += 1

        return high_score_identity_fields >= 3

    async def get_field_config(self, field_name: str) -> Optional[Any]:
        """获取字段配置"""
        try:
            # 这里应该从数据库获取字段配置
            # 暂时返回None，使用默认分析逻辑
            return None
        except Exception:
            return None

    async def update_sensitivity_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """更新敏感度阈值"""
        try:
            # 验证阈值合理性
            for category, threshold in thresholds.items():
                if not 0.0 <= threshold <= 1.0:
                    raise DVSSException(f'阈值必须在0-1之间: {category}={threshold}')

            # 更新权重配置
            self.sensitivity_weights.update(thresholds)

            return True
        except Exception as e:
            raise DVSSException(f'更新敏感度阈值失败: {str(e)}')

    async def get_sensitivity_report(self, order_ids: List[int]) -> Dict[str, Any]:
        """生成敏感度报告"""
        try:
            total_orders = len(order_ids)
            high_risk_count = 0
            medium_risk_count = 0
            low_risk_count = 0

            field_sensitivity_stats = {}
            common_risk_factors = []

            # 这里应该批量分析订单
            # 暂时返回模拟数据

            return {
                'total_orders': total_orders,
                'risk_distribution': {'high': high_risk_count, 'medium': medium_risk_count, 'low': low_risk_count},
                'field_sensitivity_stats': field_sensitivity_stats,
                'common_risk_factors': common_risk_factors,
                'generated_at': datetime.now().isoformat(),
            }

        except Exception as e:
            raise DVSSException(f'生成敏感度报告失败: {str(e)}')

    def get_supported_categories(self) -> List[str]:
        """获取支持的敏感度类别"""
        return list(self.sensitivity_weights.keys())

    def get_pii_patterns(self) -> Dict[str, str]:
        """获取PII检测模式"""
        return self.pii_patterns.copy()

    async def analyze_data_sensitivity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据的敏感度"""
        try:
            sensitive_fields = []
            field_scores = {}
            total_score = 0.0

            for field_name, field_value in data.items():
                if field_value is None:
                    continue

                # 检查字段敏感度
                sensitivity_score = await self.calculate_field_sensitivity(field_name, str(field_value))
                field_scores[field_name] = sensitivity_score

                if sensitivity_score > 0.5:
                    sensitive_fields.append({
                        'field': field_name,
                        'score': sensitivity_score,
                        'category': self.field_categories.get(field_name, 'unknown'),
                    })

                total_score += sensitivity_score

            # 计算整体敏感度分数
            overall_score = min(1.0, total_score / len(data) if data else 0.0)

            return {
                'overall_score': overall_score,
                'sensitive_fields': sensitive_fields,
                'field_scores': field_scores,
                'total_fields': len(data),
                'sensitive_count': len(sensitive_fields),
            }
        except Exception as e:
            raise DVSSException(f'分析数据敏感度失败: {str(e)}')
