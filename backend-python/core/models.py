from sqlalchemy import Column, String, DateTime, Boolean, Text, DECIMAL, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    department = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    role = relationship("Role", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSONB)
    field_access = Column(JSONB)  # 字段级别权限
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    users = relationship("User", back_populates="role")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(String(100))
    customer_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(Text)
    shipping_address = Column(Text)
    billing_address = Column(Text)
    item_list = Column(JSONB)
    payment_info = Column(JSONB)
    total_amount = Column(DECIMAL(10, 2))
    tax_amount = Column(DECIMAL(10, 2))
    shipping_cost = Column(DECIMAL(10, 2))
    discount = Column(DECIMAL(10, 2))
    sensitivity_score = Column(DECIMAL(5, 4))
    data_source = Column(String(50))  # alibaba, weee
    status = Column(String(20), default='active')  # active, deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    shard_indices = relationship("ShardIndex", back_populates="order")

class ShardIndex(Base):
    __tablename__ = "shard_index"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shard_id = Column(String(100), unique=True, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    shard_sequence = Column(Integer)  # 分片序号
    total_shards = Column(Integer)    # 总分片数
    threshold_k = Column(Integer)     # 重构阈值
    node_ip = Column(String(50))
    storage_path = Column(Text)
    checksum = Column(String(64))     # SHA256
    status = Column(String(20), default='active')  # active, deleted, corrupted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="shard_indices")

class SensitivityConfig(Base):
    __tablename__ = "sensitivity_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_name = Column(String(100), nullable=False)
    weight = Column(DECIMAL(3, 2), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SystemLoad(Base):
    __tablename__ = "system_load"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cpu_usage = Column(DECIMAL(5, 2))
    memory_usage = Column(DECIMAL(5, 2))
    disk_io = Column(DECIMAL(5, 2))
    network_io = Column(DECIMAL(5, 2))
    active_connections = Column(Integer)
    load_score = Column(DECIMAL(5, 4))
    threshold_k = Column(Integer)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, ENCRYPT, DECRYPT
    resource_type = Column(String(50))  # ORDER, SHARD, USER
    resource_id = Column(String(100))
    details = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    blockchain_tx_id = Column(String(100))  # 区块链交易ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tx_id = Column(String(100), unique=True, nullable=False)
    channel_name = Column(String(50))
    chaincode_name = Column(String(50))
    function_name = Column(String(50))
    args = Column(JSONB)
    response = Column(JSONB)
    block_number = Column(Integer)
    tx_timestamp = Column(DateTime(timezone=True))
    status = Column(String(20))  # success, failed, pending
    created_at = Column(DateTime(timezone=True), server_default=func.now())
