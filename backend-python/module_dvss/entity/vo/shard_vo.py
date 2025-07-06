"""
数据分片视图对象 (VO)
View Object - 用于API响应的数据传输对象
"""

from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ShardTypeEnum(str, Enum):
    """分片类型枚举"""
    ORIGINAL = "original"
    ENCRYPTED = "encrypted"
    THRESHOLD = "threshold"
    BACKUP = "backup"

class ShardStatusEnum(str, Enum):
    """分片状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CORRUPTED = "corrupted"
    LOST = "lost"
    ARCHIVED = "archived"

class PermissionTypeEnum(str, Enum):
    """权限类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    AUDIT = "audit"

class ShardCreateRequest(BaseModel):
    """分片创建请求"""
    original_file_name: str
    original_file_hash: str
    total_shards: int
    threshold: int
    shard_type: ShardTypeEnum = ShardTypeEnum.THRESHOLD
    encryption_algorithm: Optional[str] = "AES-256-GCM"
    access_policy: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('threshold')
    def threshold_validator(cls, v, values):
        if 'total_shards' in values and v > values['total_shards']:
            raise ValueError('门限值不能大于总分片数')
        if v < 1:
            raise ValueError('门限值至少为1')
        return v

    @validator('total_shards')
    def total_shards_validator(cls, v):
        if v < 1 or v > 100:
            raise ValueError('总分片数必须在1-100之间')
        return v

class ShardUploadRequest(BaseModel):
    """分片上传请求"""
    shard_id: str
    shard_index: int
    shard_data: str  # Base64编码的分片数据
    shard_hash: str
    shard_size: int
    storage_node: Optional[str] = None
    zkp_proof: Optional[str] = None

class ShardUpdateRequest(BaseModel):
    """分片更新请求"""
    status: Optional[ShardStatusEnum] = None
    storage_path: Optional[str] = None
    storage_node: Optional[str] = None
    access_policy: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ShardReconstructRequest(BaseModel):
    """分片重构请求"""
    shard_ids: List[str]
    reconstruction_key: Optional[str] = None

class ShardPermissionRequest(BaseModel):
    """分片权限请求"""
    user_id: int
    permission_type: PermissionTypeEnum
    can_read: bool = False
    can_write: bool = False
    can_delete: bool = False
    can_share: bool = False
    can_audit: bool = False
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class ShardBaseResponse(BaseModel):
    """分片基础响应"""
    id: int
    shard_id: str
    original_file_name: str
    original_file_hash: str
    shard_index: int
    total_shards: int
    threshold: int
    shard_type: ShardTypeEnum
    shard_size: int
    shard_hash: str
    storage_node: Optional[str] = None
    owner_id: int
    status: ShardStatusEnum
    version: int
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int

    class Config:
        from_attributes = True

class ShardDetailResponse(ShardBaseResponse):
    """分片详细响应"""
    storage_path: Optional[str] = None
    encryption_algorithm: Optional[str] = None
    access_policy: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    permissions: Optional[List['ShardPermissionResponse']] = None

class ShardListResponse(BaseModel):
    """分片列表响应"""
    total: int
    page: int
    page_size: int
    items: List[ShardBaseResponse]

class ShardPermissionResponse(BaseModel):
    """分片权限响应"""
    id: int
    shard_id: int
    user_id: int
    permission_type: PermissionTypeEnum
    can_read: bool
    can_write: bool
    can_delete: bool
    can_share: bool
    can_audit: bool
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    granted_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class ShardReconstructResponse(BaseModel):
    """分片重构响应"""
    success: bool
    reconstructed_file_hash: str
    reconstructed_file_size: int
    used_shards: List[str]
    reconstruction_time: float

class ShardSearchRequest(BaseModel):
    """分片搜索请求"""
    keyword: Optional[str] = None
    shard_type: Optional[ShardTypeEnum] = None
    status: Optional[ShardStatusEnum] = None
    owner_id: Optional[int] = None
    file_name: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    page: int = 1
    page_size: int = 20

class AccessLogRequest(BaseModel):
    """访问日志请求"""
    shard_id: int
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None

class AccessLogResponse(BaseModel):
    """访问日志响应"""
    id: int
    shard_id: int
    user_id: int
    action: str
    result: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ShardStatsResponse(BaseModel):
    """分片统计响应"""
    total_shards: int
    active_shards: int
    corrupted_shards: int
    total_storage_size: int
    total_files: int
    average_shard_size: float
    most_accessed_shards: List[ShardBaseResponse]

class ShardIntegrityCheckResponse(BaseModel):
    """分片完整性检查响应"""
    shard_id: str
    is_valid: bool
    hash_match: bool
    storage_accessible: bool
    last_check_time: datetime
    error_details: Optional[str] = None

# 更新前向引用
ShardDetailResponse.model_rebuild()
