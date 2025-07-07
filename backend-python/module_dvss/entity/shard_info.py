"""
分片信息实体模型
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .user import Base


class ShardInfo(Base):
    """分片信息实体"""

    __tablename__ = 'shard_info'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    encrypted_order_id = Column(
        Integer, ForeignKey('encrypted_orders.id'), nullable=False, index=True, comment='加密订单ID'
    )
    shard_id = Column(String(128), unique=True, nullable=False, index=True, comment='分片ID')
    shard_index = Column(Integer, nullable=False, comment='分片索引')
    shard_data = Column(Text, nullable=False, comment='分片数据')
    storage_node = Column(String(100), nullable=True, comment='存储节点')
    storage_location = Column(String(200), nullable=True, comment='存储位置')
    checksum = Column(String(128), nullable=False, comment='校验和')
    status = Column(String(20), default='active', nullable=False, index=True, comment='状态')

    # 分片算法相关字段
    threshold = Column(Integer, nullable=True, comment='重构阈值')
    total_shards = Column(Integer, nullable=True, comment='总分片数')
    algorithm = Column(String(50), nullable=True, comment='分片算法')

    # 关联用户信息
    user_id = Column(Integer, nullable=True, comment='用户ID')
    original_order_id = Column(Integer, nullable=True, comment='原始订单ID')

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关系定义
    encrypted_order = relationship('EncryptedOrder', back_populates='shards')

    def __repr__(self):
        return (
            f"<ShardInfo(id={self.id}, shard_id='{self.shard_id}', "
            f"shard_index={self.shard_index}, status='{self.status}')>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'encrypted_order_id': self.encrypted_order_id,
            'shard_id': self.shard_id,
            'shard_index': self.shard_index,
            'shard_data': self.shard_data,
            'storage_node': self.storage_node,
            'storage_location': self.storage_location,
            'checksum': self.checksum,
            'status': self.status,
            'threshold': self.threshold,
            'total_shards': self.total_shards,
            'algorithm': self.algorithm,
            'user_id': self.user_id,
            'original_order_id': self.original_order_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class StorageNode(Base):
    """存储节点实体"""

    __tablename__ = 'storage_nodes'

    id = Column(Integer, primary_key=True, index=True, comment='主键ID')
    node_name = Column(String(100), unique=True, nullable=False, index=True, comment='节点名称')
    node_address = Column(String(200), nullable=False, comment='节点地址')
    node_type = Column(String(50), nullable=False, comment='节点类型')
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment='是否激活')
    capacity_used = Column(Integer, default=0, comment='已用容量')
    capacity_total = Column(Integer, default=0, comment='总容量')
    last_health_check = Column(DateTime(timezone=True), nullable=True, comment='最后健康检查时间')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return (
            f"<StorageNode(id={self.id}, node_name='{self.node_name}', "
            f"node_type='{self.node_type}', is_active={self.is_active})>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'node_name': self.node_name,
            'node_address': self.node_address,
            'node_type': self.node_type,
            'is_active': self.is_active,
            'capacity_used': self.capacity_used,
            'capacity_total': self.capacity_total,
            'capacity_usage_percent': (self.capacity_used / self.capacity_total * 100)
            if self.capacity_total > 0
            else 0,
            'last_health_check': self.last_health_check,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
