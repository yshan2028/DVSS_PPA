"""
订单字段实体模型
"""

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class OrderField(Base):
    """订单字段实体"""

    __tablename__ = 'order_fields'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    field_name = Column(String(100), unique=True, nullable=False, index=True, comment='字段名称')
    field_type = Column(String(50), nullable=False, comment='字段类型')
    sensitivity_level = Column(String(20), nullable=False, index=True, comment='敏感度等级')
    sensitivity_score = Column(Float, nullable=False, index=True, comment='敏感度分值')
    category = Column(String(50), nullable=False, index=True, comment='字段分类')
    description = Column(Text, nullable=True, comment='字段描述')
    is_required = Column(Boolean, default=False, nullable=False, comment='是否必填')
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment='是否激活')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 与角色字段权限的关系
    role_permissions = relationship('RoleFieldPermission', back_populates='field', cascade='all, delete-orphan')

    def __repr__(self):
        return (
            f"<OrderField(id={self.id}, field_name='{self.field_name}', sensitivity_level='{self.sensitivity_level}')>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'field_name': self.field_name,
            'field_type': self.field_type,
            'sensitivity_level': self.sensitivity_level,
            'sensitivity_score': self.sensitivity_score,
            'category': self.category,
            'description': self.description,
            'is_required': self.is_required,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class RoleFieldPermission(Base):
    """角色字段权限实体"""

    __tablename__ = 'role_field_permissions'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True, comment='角色ID')
    field_id = Column(
        Integer, ForeignKey('order_fields.id', ondelete='CASCADE'), nullable=False, index=True, comment='字段ID'
    )
    can_view = Column(Boolean, default=False, nullable=False, comment='可查看')
    can_decrypt = Column(Boolean, default=False, nullable=False, comment='可解密')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')

    # 关系定义
    role = relationship('Role', back_populates='field_permissions')
    field = relationship('OrderField', back_populates='role_permissions')

    def __repr__(self):
        return (
            f'<RoleFieldPermission(role_id={self.role_id}, field_id={self.field_id}, '
            f'can_view={self.can_view}, can_decrypt={self.can_decrypt})>'
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'role_id': self.role_id,
            'field_id': self.field_id,
            'can_view': self.can_view,
            'can_decrypt': self.can_decrypt,
            'created_at': self.created_at,
        }
