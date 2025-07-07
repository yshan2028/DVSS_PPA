"""
敏感度配置实体模型
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .user import Base


class SensitivityConfig(Base):
    """敏感度配置实体"""

    __tablename__ = 'sensitivity_configs'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    config_name = Column(String(100), unique=True, nullable=False, index=True, comment='配置名称')
    config_data = Column(Text, nullable=False, comment='配置数据(YAML)')
    description = Column(Text, nullable=True, comment='配置描述')
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment='是否激活')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return f"<SensitivityConfig(id={self.id}, config_name='{self.config_name}', is_active={self.is_active})>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_name': self.config_name,
            'config_data': self.config_data,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
