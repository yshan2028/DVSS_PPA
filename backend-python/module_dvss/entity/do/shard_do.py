"""
数据分片相关数据对象 (DO)
Data Object - 对应数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.get_db import Base
import enum

class ShardType(enum.Enum):
    """分片类型枚举"""
    ORIGINAL = "original"  # 原始数据
    ENCRYPTED = "encrypted"  # 加密数据
    THRESHOLD = "threshold"  # 门限秘密分享
    BACKUP = "backup"  # 备份数据

class ShardStatus(enum.Enum):
    """分片状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CORRUPTED = "corrupted"
    LOST = "lost"
    ARCHIVED = "archived"

class PermissionType(enum.Enum):
    """权限类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    AUDIT = "audit"

class DataShard(Base):
    """
    数据分片表
    """
    __tablename__ = "data_shards"

    id = Column(Integer, primary_key=True, index=True, comment="分片ID")
    shard_id = Column(String(64), unique=True, nullable=False, index=True, comment="分片唯一标识")
    original_file_name = Column(String(255), nullable=False, comment="原始文件名")
    original_file_hash = Column(String(64), nullable=False, comment="原始文件SHA256哈希")
    shard_index = Column(Integer, nullable=False, comment="分片索引")
    total_shards = Column(Integer, nullable=False, comment="总分片数")
    threshold = Column(Integer, nullable=False, comment="门限值")
    
    # 分片基本信息
    shard_type = Column(String(20), nullable=False, comment="分片类型")
    shard_size = Column(Integer, nullable=False, comment="分片大小(字节)")
    shard_hash = Column(String(64), nullable=False, comment="分片哈希值")
    storage_path = Column(String(500), nullable=True, comment="存储路径")
    storage_node = Column(String(100), nullable=True, comment="存储节点")
    
    # 加密信息
    encryption_algorithm = Column(String(50), nullable=True, comment="加密算法")
    encryption_key_hash = Column(String(64), nullable=True, comment="加密密钥哈希")
    zkp_proof = Column(Text, nullable=True, comment="零知识证明")
    
    # 所有者和权限
    owner_id = Column(Integer, ForeignKey("dvss_users.id"), nullable=False, comment="所有者ID")
    access_policy = Column(JSON, nullable=True, comment="访问策略(JSON格式)")
    
    # 状态和元数据
    status = Column(String(20), default="active", nullable=False, comment="分片状态")
    version = Column(Integer, default=1, comment="版本号")
    metadata = Column(JSON, nullable=True, comment="元数据(JSON格式)")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    last_accessed = Column(DateTime(timezone=True), nullable=True, comment="最后访问时间")
    access_count = Column(Integer, default=0, comment="访问次数")
    
    # 关联关系
    owner = relationship("DvssUser", backref="owned_shards")
    permissions = relationship("ShardPermission", back_populates="shard", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="shard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataShard(id={self.id}, shard_id='{self.shard_id}', owner_id={self.owner_id})>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "shard_id": self.shard_id,
            "original_file_name": self.original_file_name,
            "original_file_hash": self.original_file_hash,
            "shard_index": self.shard_index,
            "total_shards": self.total_shards,
            "threshold": self.threshold,
            "shard_type": self.shard_type,
            "shard_size": self.shard_size,
            "shard_hash": self.shard_hash,
            "storage_path": self.storage_path,
            "storage_node": self.storage_node,
            "encryption_algorithm": self.encryption_algorithm,
            "owner_id": self.owner_id,
            "status": self.status,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "access_count": self.access_count
        }

class ShardPermission(Base):
    """
    分片权限表
    """
    __tablename__ = "shard_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    shard_id = Column(Integer, ForeignKey("data_shards.id"), nullable=False, comment="分片ID")
    user_id = Column(Integer, ForeignKey("dvss_users.id"), nullable=False, comment="用户ID")
    permission_type = Column(String(20), nullable=False, comment="权限类型")
    granted_by = Column(Integer, ForeignKey("dvss_users.id"), nullable=False, comment="授权者ID")
    
    # 权限配置
    can_read = Column(Boolean, default=False, comment="读权限")
    can_write = Column(Boolean, default=False, comment="写权限")
    can_delete = Column(Boolean, default=False, comment="删除权限")
    can_share = Column(Boolean, default=False, comment="分享权限")
    can_audit = Column(Boolean, default=False, comment="审计权限")
    
    # 有效期
    valid_from = Column(DateTime(timezone=True), nullable=True, comment="生效时间")
    valid_until = Column(DateTime(timezone=True), nullable=True, comment="失效时间")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    # 关联关系
    shard = relationship("DataShard", back_populates="permissions")
    user = relationship("DvssUser", foreign_keys=[user_id], backref="shard_permissions")
    granter = relationship("DvssUser", foreign_keys=[granted_by], backref="granted_permissions")
    
    def __repr__(self):
        return f"<ShardPermission(id={self.id}, shard_id={self.shard_id}, user_id={self.user_id})>"

class AccessLog(Base):
    """
    访问日志表
    """
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    shard_id = Column(Integer, ForeignKey("data_shards.id"), nullable=False, comment="分片ID")
    user_id = Column(Integer, ForeignKey("dvss_users.id"), nullable=False, comment="用户ID")
    
    # 访问信息
    action = Column(String(50), nullable=False, comment="操作类型")
    result = Column(String(20), nullable=False, comment="操作结果(success/failure)")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    
    # 详细信息
    request_data = Column(JSON, nullable=True, comment="请求数据")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    error_message = Column(Text, nullable=True, comment="错误信息")
    execution_time = Column(Float, nullable=True, comment="执行时间(秒)")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    
    # 关联关系
    shard = relationship("DataShard", back_populates="access_logs")
    user = relationship("DvssUser", backref="access_logs")
    
    def __repr__(self):
        return f"<AccessLog(id={self.id}, shard_id={self.shard_id}, user_id={self.user_id}, action='{self.action}')>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "shard_id": self.shard_id,
            "user_id": self.user_id,
            "action": self.action,
            "result": self.result,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_data": self.request_data,
            "response_data": self.response_data,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
