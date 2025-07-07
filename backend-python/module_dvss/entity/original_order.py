"""
原始订单实体模型
"""

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class OriginalOrder(Base):
    """原始订单实体"""

    __tablename__ = 'original_orders'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    order_id = Column(String(100), unique=True, nullable=False, index=True, comment='订单编号')
    user_id = Column(String(100), nullable=False, index=True, comment='用户ID')

    # 个人信息字段
    name = Column(String(100), nullable=True, comment='姓名')
    phone = Column(String(20), nullable=True, comment='电话')
    email = Column(String(100), nullable=True, comment='邮箱')

    # 地址信息字段
    address = Column(Text, nullable=True, comment='地址')
    shipping_address = Column(Text, nullable=True, comment='配送地址')
    billing_address = Column(Text, nullable=True, comment='账单地址')
    zip_code = Column(String(20), nullable=True, comment='邮编')
    city = Column(String(100), nullable=True, comment='城市')
    state = Column(String(100), nullable=True, comment='州/省')
    country = Column(String(100), nullable=True, comment='国家')

    # 支付信息字段
    payment_info = Column(Text, nullable=True, comment='支付信息')
    credit_card = Column(String(20), nullable=True, comment='信用卡号')
    bank_account = Column(String(50), nullable=True, comment='银行账户')
    payment_method = Column(String(50), nullable=True, comment='支付方式')

    # 商品信息字段
    item_list = Column(Text, nullable=True, comment='商品列表(JSON)')
    item_name = Column(String(200), nullable=True, comment='商品名称')
    item_price = Column(Numeric(10, 2), nullable=True, comment='商品价格')
    quantity = Column(Integer, nullable=True, comment='数量')

    # 金额字段
    total_amount = Column(Numeric(10, 2), nullable=True, comment='总金额')
    tax_amount = Column(Numeric(10, 2), nullable=True, comment='税额')
    shipping_cost = Column(Numeric(10, 2), nullable=True, comment='运费')
    discount = Column(Numeric(10, 2), nullable=True, comment='折扣')

    # 系统字段
    sensitivity_score = Column(Numeric(3, 2), default=0.0, nullable=False, index=True, comment='敏感度分值')
    status = Column(String(20), default='active', nullable=False, index=True, comment='状态')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关系定义
    encrypted_orders = relationship('EncryptedOrder', back_populates='original_order', cascade='all, delete-orphan')

    def __repr__(self):
        return (
            f"<OriginalOrder(id={self.id}, order_id='{self.order_id}', "
            f"user_id='{self.user_id}', status='{self.status}')>"
        )

    def to_dict(self, include_sensitive=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'order_id': self.order_id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'zip_code': self.zip_code,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'payment_method': self.payment_method,
            'item_list': self.item_list,
            'item_name': self.item_name,
            'item_price': float(self.item_price) if self.item_price else None,
            'quantity': self.quantity,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'discount': float(self.discount) if self.discount else None,
            'sensitivity_score': float(self.sensitivity_score),
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

        # 根据权限决定是否包含敏感信息
        if include_sensitive:
            data.update({
                'payment_info': self.payment_info,
                'credit_card': self.credit_card,
                'bank_account': self.bank_account,
            })
        else:
            # 脱敏处理
            data.update({
                'payment_info': '***',
                'credit_card': self._mask_card_number(self.credit_card),
                'bank_account': self._mask_account_number(self.bank_account),
            })

        return data

    def _mask_card_number(self, card_number):
        """信用卡号脱敏"""
        if not card_number or len(card_number) <= 4:
            return card_number
        return '*' * (len(card_number) - 4) + card_number[-4:]

    def _mask_account_number(self, account_number):
        """银行账户脱敏"""
        if not account_number or len(account_number) <= 4:
            return account_number
        return '*' * (len(account_number) - 4) + account_number[-4:]

    def get_field_value(self, field_name):
        """获取字段值"""
        return getattr(self, field_name, None)

    def set_field_value(self, field_name, value):
        """设置字段值"""
        if hasattr(self, field_name):
            setattr(self, field_name, value)

    def get_sensitive_fields(self):
        """获取敏感字段列表"""
        return [
            'name',
            'phone',
            'email',
            'address',
            'shipping_address',
            'billing_address',
            'payment_info',
            'credit_card',
            'bank_account',
            'total_amount',
            'tax_amount',
        ]

    def calculate_sensitivity_score(self, field_scores):
        """计算敏感度分值"""
        total_score = 0.0
        field_count = 0

        for field_name, score in field_scores.items():
            field_value = self.get_field_value(field_name)
            if field_value is not None and field_value != '':
                total_score += score
                field_count += 1

        self.sensitivity_score = total_score / field_count if field_count > 0 else 0.0
        return float(self.sensitivity_score)
