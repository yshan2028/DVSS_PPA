"""
角色实体模型
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class Role(Base):
    """角色实体"""

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    name = Column(String(100), unique=True, nullable=False, index=True, comment='角色名称')
    description = Column(Text, nullable=True, comment='角色描述')
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment='是否激活')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关系定义
    users = relationship('User', back_populates='role')
    field_permissions = relationship('RoleFieldPermission', back_populates='role', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', is_active={self.is_active})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
