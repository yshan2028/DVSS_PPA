"""
分页工具类
处理分页逻辑
"""

import math

from typing import Any, List, Tuple

from sqlalchemy.orm import Query


class PageUtil:
    """分页工具类"""

    @staticmethod
    def paginate(query: Query, page: int = 1, page_size: int = 20) -> Tuple[List[Any], int, int, int]:
        """
        分页查询

        Args:
            query: SQLAlchemy查询对象
            page: 页码 (从1开始)
            page_size: 每页大小

        Returns:
            Tuple[List[Any], int, int, int]: (数据列表, 总记录数, 页码, 每页大小)
        """
        # 确保页码至少为1
        page = max(1, page)
        page_size = max(1, min(100, page_size))  # 限制每页最大100条

        # 计算总记录数
        total = query.count()

        # 计算偏移量
        offset = (page - 1) * page_size

        # 执行分页查询
        items = query.offset(offset).limit(page_size).all()

        return items, total, page, page_size

    @staticmethod
    def get_page_info(total: int, page: int, page_size: int) -> dict:
        """
        获取分页信息

        Args:
            total: 总记录数
            page: 当前页码
            page_size: 每页大小

        Returns:
            dict: 分页信息
        """
        total_pages = math.ceil(total / page_size) if page_size > 0 else 0
        has_prev = page > 1
        has_next = page < total_pages

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_page': page - 1 if has_prev else None,
            'next_page': page + 1 if has_next else None,
        }

    @staticmethod
    def validate_page_params(page: int, page_size: int) -> Tuple[int, int]:
        """
        验证和标准化分页参数

        Args:
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[int, int]: (标准化后的页码, 标准化后的每页大小)
        """
        # 页码至少为1
        page = max(1, page)

        # 每页大小在1-100之间
        page_size = max(1, min(100, page_size))

        return page, page_size

    @staticmethod
    def create_page_response(items: List[Any], total: int, page: int, page_size: int) -> dict:
        """
        创建标准分页响应

        Args:
            items: 数据列表
            total: 总记录数
            page: 页码
            page_size: 每页大小

        Returns:
            dict: 标准分页响应
        """
        page_info = PageUtil.get_page_info(total, page, page_size)

        return {'items': items, **page_info}


class OffsetLimitUtil:
    """偏移量分页工具类"""

    @staticmethod
    def calculate_offset(page: int, page_size: int) -> int:
        """
        计算偏移量

        Args:
            page: 页码 (从1开始)
            page_size: 每页大小

        Returns:
            int: 偏移量
        """
        return (max(1, page) - 1) * max(1, page_size)

    @staticmethod
    def calculate_page_from_offset(offset: int, page_size: int) -> int:
        """
        从偏移量计算页码

        Args:
            offset: 偏移量
            page_size: 每页大小

        Returns:
            int: 页码
        """
        return (offset // max(1, page_size)) + 1
