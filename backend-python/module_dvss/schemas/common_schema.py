"""
通用响应模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class CommonResponse(BaseModel, Generic[T]):
    """通用响应模型"""
    code: int = Field(..., description="响应码")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    success: bool = Field(..., description="是否成功")


class PaginationInfo(BaseModel):
    """分页信息"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    code: int = Field(..., description="响应码")
    message: str = Field(..., description="响应消息")
    data: List[T] = Field(..., description="数据列表")
    pagination: PaginationInfo = Field(..., description="分页信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    success: bool = Field(..., description="是否成功")


class BaseRequest(BaseModel):
    """基础请求模型"""
    pass


class PaginationRequest(BaseModel):
    """分页请求模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    search: Optional[str] = Field(None, description="搜索关键词")


class SortRequest(BaseModel):
    """排序请求模型"""
    sort_field: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="排序方向")


class FilterRequest(BaseModel):
    """过滤请求模型"""
    filters: Optional[dict] = Field(None, description="过滤条件")


class BulkOperationRequest(BaseModel):
    """批量操作请求模型"""
    ids: List[int] = Field(..., description="ID列表")
    operation: str = Field(..., description="操作类型")


class StatusToggleRequest(BaseModel):
    """状态切换请求模型"""
    is_active: bool = Field(..., description="是否激活")


class ImportRequest(BaseModel):
    """导入请求模型"""
    file_type: str = Field(..., regex="^(csv|json|xlsx)$", description="文件类型")
    data: List[dict] = Field(..., description="导入数据")
    validate_only: bool = Field(False, description="仅验证不导入")


class ExportRequest(BaseModel):
    """导出请求模型"""
    file_type: str = Field(..., regex="^(csv|json|xlsx)$", description="导出文件类型")
    filters: Optional[dict] = Field(None, description="过滤条件")
    fields: Optional[List[str]] = Field(None, description="导出字段")


class ApiResponse(BaseModel):
    """API响应包装器"""
    version: str = Field("1.0.0", description="API版本")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    
class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field("healthy", description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    dependencies: Optional[dict] = Field(None, description="依赖服务状态")


class ErrorDetail(BaseModel):
    """错误详情"""
    field: Optional[str] = Field(None, description="错误字段")
    message: str = Field(..., description="错误消息")
    code: Optional[str] = Field(None, description="错误代码")


class ValidationErrorResponse(BaseModel):
    """验证错误响应"""
    code: int = Field(422, description="错误码")
    message: str = Field("验证失败", description="错误消息")
    errors: List[ErrorDetail] = Field(..., description="错误详情列表")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    success: bool = Field(False, description="是否成功")
