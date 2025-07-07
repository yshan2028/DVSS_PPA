"""
操作日志实体模型
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class OperationLog(Base):
    """操作日志实体"""

    __tablename__ = 'operation_logs'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True, comment='操作用户ID')
    operation_type = Column(String(50), nullable=False, index=True, comment='操作类型')
    resource_type = Column(String(50), nullable=False, index=True, comment='资源类型')
    resource_id = Column(String(100), nullable=True, index=True, comment='资源ID')
    operation_detail = Column(Text, nullable=True, comment='操作详情(JSON)')
    ip_address = Column(String(45), nullable=True, comment='IP地址')
    user_agent = Column(Text, nullable=True, comment='用户代理')
    status = Column(String(20), nullable=False, index=True, comment='状态')
    error_message = Column(Text, nullable=True, comment='错误信息')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')

    # 关系定义
    user = relationship('User')

    def __repr__(self):
        return (
            f'<OperationLog(id={self.id}, user_id={self.user_id}, '
            f"operation_type='{self.operation_type}', status='{self.status}')>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operation_type': self.operation_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'operation_detail': self.operation_detail,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at,
        }
