"""
订单管理相关数据模式
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class OrderStatus(str, Enum):
    """订单状态枚举"""

    ACTIVE = 'active'
    DELETED = 'deleted'
    ENCRYPTED = 'encrypted'
    SHARDED = 'sharded'


class PaymentMethod(str, Enum):
    """支付方式枚举"""

    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    BANK_TRANSFER = 'bank_transfer'
    PAYPAL = 'paypal'
    ALIPAY = 'alipay'
    WECHAT_PAY = 'wechat_pay'


class OrderBase(BaseModel):
    """订单基础模式"""

    order_id: str = Field(..., min_length=1, max_length=100, description='订单编号')
    user_id: str = Field(..., min_length=1, max_length=100, description='用户ID')
    name: Optional[str] = Field(None, max_length=100, description='姓名')
    phone: Optional[str] = Field(None, max_length=20, description='电话')
    email: Optional[EmailStr] = Field(None, description='邮箱')
    address: Optional[str] = Field(None, max_length=500, description='地址')
    shipping_address: Optional[str] = Field(None, max_length=500, description='配送地址')
    billing_address: Optional[str] = Field(None, max_length=500, description='账单地址')
    zip_code: Optional[str] = Field(None, max_length=20, description='邮编')
    city: Optional[str] = Field(None, max_length=100, description='城市')
    state: Optional[str] = Field(None, max_length=100, description='州/省')
    country: Optional[str] = Field(None, max_length=100, description='国家')
    payment_info: Optional[str] = Field(None, max_length=500, description='支付信息')
    credit_card: Optional[str] = Field(None, max_length=20, description='信用卡号')
    bank_account: Optional[str] = Field(None, max_length=50, description='银行账户')
    payment_method: Optional[PaymentMethod] = Field(None, description='支付方式')
    item_list: Optional[str] = Field(None, description='商品列表(JSON)')
    item_name: Optional[str] = Field(None, max_length=200, description='商品名称')
    item_price: Optional[Decimal] = Field(None, ge=0, description='商品价格')
    quantity: Optional[int] = Field(None, ge=1, description='数量')
    total_amount: Optional[Decimal] = Field(None, ge=0, description='总金额')
    tax_amount: Optional[Decimal] = Field(None, ge=0, description='税额')
    shipping_cost: Optional[Decimal] = Field(None, ge=0, description='运费')
    discount: Optional[Decimal] = Field(None, ge=0, description='折扣')

    @validator('credit_card')
    def mask_credit_card(cls, v):
        """信用卡号脱敏"""
        if v and len(v) > 4:
            return '*' * (len(v) - 4) + v[-4:]
        return v

    @validator('bank_account')
    def mask_bank_account(cls, v):
        """银行账户脱敏"""
        if v and len(v) > 4:
            return '*' * (len(v) - 4) + v[-4:]
        return v


class OrderCreate(OrderBase):
    """创建订单模式"""

    pass


class OrderUpdate(BaseModel):
    """更新订单模式"""

    name: Optional[str] = Field(None, max_length=100, description='姓名')
    phone: Optional[str] = Field(None, max_length=20, description='电话')
    email: Optional[EmailStr] = Field(None, description='邮箱')
    address: Optional[str] = Field(None, max_length=500, description='地址')
    shipping_address: Optional[str] = Field(None, max_length=500, description='配送地址')
    billing_address: Optional[str] = Field(None, max_length=500, description='账单地址')
    zip_code: Optional[str] = Field(None, max_length=20, description='邮编')
    city: Optional[str] = Field(None, max_length=100, description='城市')
    state: Optional[str] = Field(None, max_length=100, description='州/省')
    country: Optional[str] = Field(None, max_length=100, description='国家')
    payment_method: Optional[PaymentMethod] = Field(None, description='支付方式')
    item_name: Optional[str] = Field(None, max_length=200, description='商品名称')
    item_price: Optional[Decimal] = Field(None, ge=0, description='商品价格')
    quantity: Optional[int] = Field(None, ge=1, description='数量')
    total_amount: Optional[Decimal] = Field(None, ge=0, description='总金额')
    tax_amount: Optional[Decimal] = Field(None, ge=0, description='税额')
    shipping_cost: Optional[Decimal] = Field(None, ge=0, description='运费')
    discount: Optional[Decimal] = Field(None, ge=0, description='折扣')


class OrderResponse(OrderBase):
    """订单响应模式"""

    id: int = Field(..., description='订单ID')
    sensitivity_score: float = Field(..., description='敏感度分值')
    status: OrderStatus = Field(..., description='订单状态')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """订单列表模式"""

    id: int = Field(..., description='订单ID')
    order_id: str = Field(..., description='订单编号')
    user_id: str = Field(..., description='用户ID')
    name: Optional[str] = Field(None, description='姓名')
    total_amount: Optional[Decimal] = Field(None, description='总金额')
    sensitivity_score: float = Field(..., description='敏感度分值')
    status: OrderStatus = Field(..., description='订单状态')
    created_at: datetime = Field(..., description='创建时间')

    class Config:
        from_attributes = True


class OrderUpload(BaseModel):
    """订单上传模式"""

    file_type: str = Field(..., description='文件类型', pattern='^(csv|json)$')
    data: List[Dict[str, Any]] = Field(..., description='订单数据')


class OrderEncrypt(BaseModel):
    """订单加密模式"""

    order_id: int = Field(..., description='订单ID')
    algorithm: str = Field('AES-256-GCM', description='加密算法')
    k_value: int = Field(..., ge=2, description='分片阈值')
    n_value: int = Field(..., ge=3, description='分片总数')

    @validator('n_value')
    def validate_n_k_relation(cls, v, values):
        """验证n和k的关系"""
        if 'k_value' in values and v <= values['k_value']:
            raise ValueError('分片总数必须大于分片阈值')
        return v


class OrderBatchEncrypt(BaseModel):
    """批量加密订单模式"""

    order_ids: List[int] = Field(..., description='订单ID列表')
    algorithm: str = Field('AES-256-GCM', description='加密算法')
    k_value: int = Field(..., ge=2, description='分片阈值')
    n_value: int = Field(..., ge=3, description='分片总数')


class OrderSensitivityAnalysis(BaseModel):
    """订单敏感度分析结果"""

    order_id: int = Field(..., description='订单ID')
    overall_score: float = Field(..., description='整体敏感度分值')
    field_scores: Dict[str, float] = Field(..., description='字段敏感度分值')
    risk_level: str = Field(..., description='风险等级')
    recommendations: List[str] = Field(..., description='建议')


class OrderFieldValue(BaseModel):
    """订单字段值模式"""

    field_name: str = Field(..., description='字段名称')
    field_value: Any = Field(..., description='字段值')
    is_encrypted: bool = Field(False, description='是否已加密')
    can_view: bool = Field(True, description='是否可查看')
    can_decrypt: bool = Field(False, description='是否可解密')


class OrderDetailWithPermissions(BaseModel):
    """带权限的订单详情"""

    id: int = Field(..., description='订单ID')
    order_id: str = Field(..., description='订单编号')
    user_id: str = Field(..., description='用户ID')
    fields: List[OrderFieldValue] = Field(..., description='字段值列表')
    sensitivity_score: float = Field(..., description='敏感度分值')
    status: OrderStatus = Field(..., description='订单状态')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')


class OrderStatistics(BaseModel):
    """订单统计信息"""

    total_orders: int = Field(..., description='总订单数')
    active_orders: int = Field(..., description='活跃订单数')
    encrypted_orders: int = Field(..., description='已加密订单数')
    average_sensitivity: float = Field(..., description='平均敏感度')
    high_risk_orders: int = Field(..., description='高风险订单数')
    sensitivity_distribution: Dict[str, int] = Field(..., description='敏感度分布')


class EncryptedOrderBase(BaseModel):
    """加密订单基础模式"""

    original_order_id: int = Field(..., description='原始订单ID')
    order_id: str = Field(..., description='订单编号')
    encryption_algorithm: str = Field(..., description='加密算法')
    k_value: int = Field(..., description='分片阈值')
    n_value: int = Field(..., description='分片总数')
    data_hash: str = Field(..., description='数据哈希值')


class EncryptedOrderResponse(EncryptedOrderBase):
    """加密订单响应模式"""

    id: int = Field(..., description='加密订单ID')
    encrypted_data: str = Field(..., description='加密后的数据')
    status: str = Field(..., description='状态')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')

    class Config:
        from_attributes = True


class EncryptedOrderList(BaseModel):
    """加密订单列表模式"""

    id: int = Field(..., description='加密订单ID')
    original_order_id: int = Field(..., description='原始订单ID')
    order_id: str = Field(..., description='订单编号')
    encryption_algorithm: str = Field(..., description='加密算法')
    k_value: int = Field(..., description='分片阈值')
    n_value: int = Field(..., description='分片总数')
    status: str = Field(..., description='状态')
    created_at: datetime = Field(..., description='创建时间')

    class Config:
        from_attributes = True


class OrderDecrypt(BaseModel):
    """订单解密模式"""

    encrypted_order_id: int = Field(..., description='加密订单ID')
    reason: str = Field(..., min_length=5, max_length=500, description='解密原因')
    requested_fields: Optional[List[str]] = Field(None, description='请求解密的字段')


class DecryptionResult(BaseModel):
    """解密结果"""

    order_id: str = Field(..., description='订单编号')
    decrypted_data: Dict[str, Any] = Field(..., description='解密后的数据')
    accessed_fields: List[str] = Field(..., description='已访问的字段')
    decryption_time: datetime = Field(..., description='解密时间')
    operator_id: str = Field(..., description='操作员ID')
