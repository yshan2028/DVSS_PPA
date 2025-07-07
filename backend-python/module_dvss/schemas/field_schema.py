"""
字段管理相关数据模式
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class SensitivityLevel(str, Enum):
    """敏感度等级枚举"""

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class FieldType(str, Enum):
    """字段类型枚举"""

    STRING = 'string'
    NUMBER = 'number'
    DATE = 'date'
    EMAIL = 'email'
    PHONE = 'phone'
    ADDRESS = 'address'
    PAYMENT = 'payment'
    BOOLEAN = 'boolean'


class FieldCategory(str, Enum):
    """字段分类枚举"""

    PII = 'pii'  # 个人身份信息
    FINANCIAL = 'financial'  # 财务信息
    LOCATION = 'location'  # 位置信息
    BUSINESS = 'business'  # 业务信息
    CONTACT = 'contact'  # 联系信息


class FieldBase(BaseModel):
    """字段基础模式"""

    field_name: str = Field(..., min_length=1, max_length=100, description='字段名称')
    field_type: FieldType = Field(..., description='字段类型')
    sensitivity_level: SensitivityLevel = Field(..., description='敏感度等级')
    sensitivity_score: float = Field(..., ge=0.0, le=1.0, description='敏感度分值')
    category: FieldCategory = Field(..., description='字段分类')
    description: Optional[str] = Field(None, max_length=500, description='字段描述')
    is_required: bool = Field(False, description='是否必填')
    is_active: bool = Field(True, description='是否激活')

    @validator('sensitivity_score')
    def validate_sensitivity_score(cls, v, values):
        """验证敏感度分值与等级的一致性"""
        if 'sensitivity_level' in values:
            level = values['sensitivity_level']
            if level == SensitivityLevel.LOW and not (0.0 <= v < 0.3):
                raise ValueError('低敏感度等级的分值应在0.0-0.3之间')
            elif level == SensitivityLevel.MEDIUM and not (0.3 <= v < 0.6):
                raise ValueError('中敏感度等级的分值应在0.3-0.6之间')
            elif level == SensitivityLevel.HIGH and not (0.6 <= v < 0.9):
                raise ValueError('高敏感度等级的分值应在0.6-0.9之间')
            elif level == SensitivityLevel.CRITICAL and not (0.9 <= v <= 1.0):
                raise ValueError('关键敏感度等级的分值应在0.9-1.0之间')
        return v


class FieldCreate(FieldBase):
    """创建字段模式"""

    pass


class FieldUpdate(BaseModel):
    """更新字段模式"""

    field_name: Optional[str] = Field(None, min_length=1, max_length=100, description='字段名称')
    field_type: Optional[FieldType] = Field(None, description='字段类型')
    sensitivity_level: Optional[SensitivityLevel] = Field(None, description='敏感度等级')
    sensitivity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description='敏感度分值')
    category: Optional[FieldCategory] = Field(None, description='字段分类')
    description: Optional[str] = Field(None, max_length=500, description='字段描述')
    is_required: Optional[bool] = Field(None, description='是否必填')
    is_active: Optional[bool] = Field(None, description='是否激活')


class FieldResponse(FieldBase):
    """字段响应模式"""

    id: int = Field(..., description='字段ID')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')

    class Config:
        from_attributes = True


class FieldList(BaseModel):
    """字段列表模式"""

    id: int = Field(..., description='字段ID')
    field_name: str = Field(..., description='字段名称')
    field_type: FieldType = Field(..., description='字段类型')
    sensitivity_level: SensitivityLevel = Field(..., description='敏感度等级')
    sensitivity_score: float = Field(..., description='敏感度分值')
    category: FieldCategory = Field(..., description='字段分类')
    is_required: bool = Field(..., description='是否必填')
    is_active: bool = Field(..., description='是否激活')

    class Config:
        from_attributes = True


class FieldBatchUpdate(BaseModel):
    """批量更新字段模式"""

    field_ids: List[int] = Field(..., description='字段ID列表')
    sensitivity_level: Optional[SensitivityLevel] = Field(None, description='敏感度等级')
    sensitivity_score: Optional[float] = Field(None, ge=0.0, le=1.0, description='敏感度分值')
    category: Optional[FieldCategory] = Field(None, description='字段分类')
    is_active: Optional[bool] = Field(None, description='是否激活')


class FieldSensitivityAnalysis(BaseModel):
    """字段敏感度分析结果"""

    total_fields: int = Field(..., description='总字段数')
    low_sensitivity: int = Field(..., description='低敏感度字段数')
    medium_sensitivity: int = Field(..., description='中敏感度字段数')
    high_sensitivity: int = Field(..., description='高敏感度字段数')
    critical_sensitivity: int = Field(..., description='关键敏感度字段数')
    average_score: float = Field(..., description='平均敏感度分值')
    category_distribution: dict = Field(..., description='分类分布')


class FieldPermission(BaseModel):
    """字段权限模式"""

    field_id: int = Field(..., description='字段ID')
    field_name: str = Field(..., description='字段名称')
    can_view: bool = Field(..., description='可查看')
    can_decrypt: bool = Field(..., description='可解密')

    class Config:
        from_attributes = True
