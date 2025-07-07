"""
通用响应模式
与Dash-FastAPI-Admin风格保持一致
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API响应模型"""

    code: int = Field(default=200, description='状态码')
    message: str = Field(default='操作成功', description='响应消息')
    data: Optional[T] = Field(default=None, description='响应数据')
    success: bool = Field(default=True, description='是否成功')


class PageInfo(BaseModel):
    """分页信息"""

    total: int = Field(..., description='总记录数')
    page: int = Field(..., description='当前页码')
    size: int = Field(..., description='每页大小')
    pages: int = Field(..., description='总页数')


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""

    items: List[T] = Field(default_factory=list, description='数据列表')
    page_info: PageInfo = Field(..., description='分页信息')


class CrudResponseModel(BaseModel):
    """CRUD操作响应模型"""

    is_success: bool = Field(..., description='操作是否成功')
    message: str = Field(..., description='操作结果消息')


class BaseRequest(BaseModel):
    """基础请求模型"""

    pass


class PageRequest(BaseModel):
    """分页请求模型"""

    page: int = Field(default=1, ge=1, description='页码')
    size: int = Field(default=10, ge=1, le=100, description='每页大小')
    keyword: Optional[str] = Field(default=None, description='搜索关键词')


class SortRequest(BaseModel):
    """排序请求模型"""

    sort_field: Optional[str] = Field(default=None, description='排序字段')
    sort_order: Optional[str] = Field(default='desc', description='排序方向')


class SearchRequest(BaseRequest):
    """搜索请求模型"""

    keyword: Optional[str] = Field(default=None, description='搜索关键词')
    start_date: Optional[datetime] = Field(default=None, description='开始日期')
    end_date: Optional[datetime] = Field(default=None, description='结束日期')
