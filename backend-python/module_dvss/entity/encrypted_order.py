"""
加密订单实体模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .user import Base


class EncryptedOrder(Base):
    """加密订单实体"""
    __tablename__ = "encrypted_orders"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    original_order_id = Column(Integer, ForeignKey("original_orders.id"), nullable=False, index=True, comment="原始订单ID")
    order_id = Column(String(100), nullable=False, index=True, comment="订单编号")
    encrypted_data = Column(Text, nullable=False, comment="加密后的数据")
    encryption_algorithm = Column(String(50), nullable=False, comment="加密算法")
    k_value = Column(Integer, nullable=False, comment="分片阈值")
    n_value = Column(Integer, nullable=False, comment="分片总数")
    data_hash = Column(String(128), nullable=False, comment="数据哈希值")
    status = Column(String(20), default="encrypted", nullable=False, index=True, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系定义
    original_order = relationship("OriginalOrder", back_populates="encrypted_orders")
    shards = relationship("ShardInfo", back_populates="encrypted_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EncryptedOrder(id={self.id}, order_id='{self.order_id}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'original_order_id': self.original_order_id,
            'order_id': self.order_id,
            'encrypted_data': self.encrypted_data,
            'encryption_algorithm': self.encryption_algorithm,
            'k_value': self.k_value,
            'n_value': self.n_value,
            'data_hash': self.data_hash,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
