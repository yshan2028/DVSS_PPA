"""
响应工具类
统一API响应格式
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class ResponseUtil:
    """响应工具类"""

    @staticmethod
    def success(data: Any = None, message: str = '操作成功', code: int = 200) -> Dict[str, Any]:
        """
        成功响应
        """
        return {
            'code': code,
            'success': True,
            'message': message,
            'data': data,
            'timestamp': None,  # 将在中间件中设置
        }

    @staticmethod
    def error(message: str = '操作失败', code: int = 400, data: Any = None) -> Dict[str, Any]:
        """
        错误响应
        """
        return {
            'code': code,
            'success': False,
            'message': message,
            'data': data,
            'timestamp': None,  # 将在中间件中设置
        }

    @staticmethod
    def page_success(items: list, total: int, page: int, page_size: int, message: str = '查询成功') -> Dict[str, Any]:
        """
        分页成功响应
        """
        return {
            'code': 200,
            'success': True,
            'message': message,
            'data': {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size,
            },
            'timestamp': None,  # 将在中间件中设置
        }

    @staticmethod
    def paginated_success(items: list, total: int, page: int, size: int, message: str = '查询成功') -> Dict[str, Any]:
        """
        分页成功响应（兼容方法）
        """
        return ResponseUtil.page_success(items, total, page, size, message)


class ApiResponse(BaseModel, Generic[T]):
    """API响应模型"""

    code: int
    success: bool
    message: str
    data: Optional[T] = None
    timestamp: Optional[str] = None

    model_config = {'arbitrary_types_allowed': True}


class PageResponse(BaseModel, Generic[T]):
    """分页响应模型"""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = {'arbitrary_types_allowed': True}
