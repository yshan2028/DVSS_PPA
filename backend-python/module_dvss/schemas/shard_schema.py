"""
分片管理相关数据模式
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ShardStatus(str, Enum):
    """分片状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CORRUPTED = "corrupted"
    MIGRATING = "migrating"
    DELETED = "deleted"


class NodeStatus(str, Enum):
    """节点状态枚举"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class ShardInfoBase(BaseModel):
    """分片信息基础模型"""
    order_id: int = Field(..., description="订单ID")
    shard_index: int = Field(..., ge=0, description="分片索引")
    shard_data: str = Field(..., description="分片数据")
    node_id: str = Field(..., description="存储节点ID")
    storage_path: str = Field(..., description="存储路径")
    checksum: str = Field(..., description="校验和")
    k_value: int = Field(..., ge=2, description="分片阈值")
    n_value: int = Field(..., ge=3, description="分片总数")


class ShardInfoCreate(ShardInfoBase):
    """创建分片信息请求"""
    pass


class ShardInfoUpdate(BaseModel):
    """更新分片信息请求"""
    node_id: Optional[str] = Field(None, description="存储节点ID")
    storage_path: Optional[str] = Field(None, description="存储路径")
    status: Optional[ShardStatus] = Field(None, description="分片状态")
    checksum: Optional[str] = Field(None, description="校验和")


class ShardInfoResponse(ShardInfoBase):
    """分片信息响应"""
    id: int = Field(..., description="分片ID")
    status: ShardStatus = Field(..., description="分片状态")
    size_bytes: int = Field(..., description="分片大小（字节）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_verified: Optional[datetime] = Field(None, description="最后验证时间")
    verification_status: Optional[str] = Field(None, description="验证状态")

    class Config:
        from_attributes = True


class ShardListResponse(BaseModel):
    """分片列表响应"""
    total: int = Field(..., description="总数")
    items: List[ShardInfoResponse] = Field(..., description="分片列表")


class ShardReconstructRequest(BaseModel):
    """分片重构请求"""
    order_id: int = Field(..., description="订单ID")
    shard_indices: List[int] = Field(..., description="参与重构的分片索引")
    verification_code: Optional[str] = Field(None, description="验证码")
    reason: str = Field(..., min_length=5, max_length=500, description="重构原因")


class ShardReconstructResponse(BaseModel):
    """分片重构响应"""
    order_id: int = Field(..., description="订单ID")
    reconstructed_data: Dict[str, Any] = Field(..., description="重构的数据")
    used_shards: List[int] = Field(..., description="使用的分片索引")
    reconstruction_time: datetime = Field(..., description="重构时间")
    operator_id: str = Field(..., description="操作员ID")


class ShardStatsResponse(BaseModel):
    """分片统计响应"""
    total_shards: int = Field(..., description="总分片数")
    active_shards: int = Field(..., description="活跃分片数")
    corrupted_shards: int = Field(..., description="损坏分片数")
    total_orders_sharded: int = Field(..., description="已分片订单总数")
    storage_usage_bytes: int = Field(..., description="存储使用量（字节）")
    node_distribution: Dict[str, int] = Field(..., description="节点分布")
    status_distribution: Dict[str, int] = Field(..., description="状态分布")


class NodeInfoBase(BaseModel):
    """存储节点基础模型"""
    node_id: str = Field(..., description="节点ID")
    node_name: str = Field(..., description="节点名称")
    host: str = Field(..., description="主机地址")
    port: int = Field(..., ge=1, le=65535, description="端口")
    storage_path: str = Field(..., description="存储路径")
    max_capacity_bytes: int = Field(..., ge=0, description="最大容量（字节）")


class NodeInfoCreate(NodeInfoBase):
    """创建存储节点请求"""
    pass


class NodeInfoUpdate(BaseModel):
    """更新存储节点请求"""
    node_name: Optional[str] = Field(None, description="节点名称")
    host: Optional[str] = Field(None, description="主机地址")
    port: Optional[int] = Field(None, ge=1, le=65535, description="端口")
    storage_path: Optional[str] = Field(None, description="存储路径")
    max_capacity_bytes: Optional[int] = Field(None, ge=0, description="最大容量（字节）")
    status: Optional[NodeStatus] = Field(None, description="节点状态")


class NodeInfoResponse(NodeInfoBase):
    """存储节点响应"""
    id: int = Field(..., description="节点记录ID")
    status: NodeStatus = Field(..., description="节点状态")
    used_capacity_bytes: int = Field(..., description="已使用容量（字节）")
    shard_count: int = Field(..., description="存储的分片数量")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ShardDistributionRequest(BaseModel):
    """分片分发请求"""
    order_id: int = Field(..., description="订单ID")
    target_nodes: List[str] = Field(..., description="目标节点ID列表")
    distribution_strategy: str = Field(default="round_robin", description="分发策略")


class ShardMigrationRequest(BaseModel):
    """分片迁移请求"""
    shard_id: int = Field(..., description="分片ID")
    target_node_id: str = Field(..., description="目标节点ID")
    reason: str = Field(..., description="迁移原因")


class ShardMigrationResponse(BaseModel):
    """分片迁移响应"""
    shard_id: int = Field(..., description="分片ID")
    source_node_id: str = Field(..., description="源节点ID")
    target_node_id: str = Field(..., description="目标节点ID")
    migration_status: str = Field(..., description="迁移状态")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ShardVerificationRequest(BaseModel):
    """分片验证请求"""
    shard_id: int = Field(..., description="分片ID")
    deep_check: bool = Field(default=False, description="是否深度检查")


class ShardVerificationResponse(BaseModel):
    """分片验证响应"""
    shard_id: int = Field(..., description="分片ID")
    is_valid: bool = Field(..., description="是否有效")
    checksum_match: bool = Field(..., description="校验和是否匹配")
    accessibility: bool = Field(..., description="是否可访问")
    size_match: bool = Field(..., description="大小是否匹配")
    verification_time: datetime = Field(..., description="验证时间")
    error_details: Optional[str] = Field(None, description="错误详情")


class ShardBackupRequest(BaseModel):
    """分片备份请求"""
    shard_ids: List[int] = Field(..., description="分片ID列表")
    backup_location: str = Field(..., description="备份位置")
    compression_enabled: bool = Field(default=True, description="是否启用压缩")


class ShardBackupResponse(BaseModel):
    """分片备份响应"""
    backup_id: str = Field(..., description="备份ID")
    shard_count: int = Field(..., description="备份的分片数量")
    total_size_bytes: int = Field(..., description="总备份大小（字节）")
    backup_location: str = Field(..., description="备份位置")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    status: str = Field(..., description="备份状态")


class ShardRestoreRequest(BaseModel):
    """分片恢复请求"""
    backup_id: str = Field(..., description="备份ID")
    target_node_ids: List[str] = Field(..., description="目标节点ID列表")
    verify_after_restore: bool = Field(default=True, description="恢复后是否验证")


class ShardRestoreResponse(BaseModel):
    """分片恢复响应"""
    restore_id: str = Field(..., description="恢复ID")
    restored_shard_count: int = Field(..., description="恢复的分片数量")
    failed_shard_count: int = Field(..., description="失败的分片数量")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    status: str = Field(..., description="恢复状态")
    error_details: Optional[List[str]] = Field(None, description="错误详情")


class ShardSearchRequest(BaseModel):
    """分片搜索请求"""
    keyword: Optional[str] = Field(None, description="关键词")
    order_id: Optional[int] = Field(None, description="订单ID")
    node_id: Optional[str] = Field(None, description="节点ID")
    status: Optional[ShardStatus] = Field(None, description="分片状态")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    min_size: Optional[int] = Field(None, description="最小大小")
    max_size: Optional[int] = Field(None, description="最大大小")


class ShardBatchOperation(BaseModel):
    """分片批量操作"""
    shard_ids: List[int] = Field(..., description="分片ID列表")
    operation: str = Field(..., description="操作类型")
    params: Optional[Dict[str, Any]] = Field(None, description="操作参数")


class ShardMonitoringMetrics(BaseModel):
    """分片监控指标"""
    total_shards: int = Field(..., description="总分片数")
    healthy_shards: int = Field(..., description="健康分片数")
    corrupted_shards: int = Field(..., description="损坏分片数")
    missing_shards: int = Field(..., description="丢失分片数")
    average_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    storage_utilization_percent: float = Field(..., description="存储利用率（百分比）")
    recent_errors: List[Dict[str, Any]] = Field(..., description="最近错误")
    node_health: Dict[str, Dict[str, Any]] = Field(..., description="节点健康状态")
