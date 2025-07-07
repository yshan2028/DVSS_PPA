"""
订单服务层
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.custom_exception import ServiceException
from module_dvss.dao.order_dao import OrderDAO
from module_dvss.entity.original_order import OriginalOrder
from module_dvss.schemas.common_schema import CrudResponseModel
from module_dvss.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderStatistics,
    OrderUpdate,
)
from utils.log_util import LogUtil

logger = LogUtil.get_logger('order_service')


class OrderService:
    """
    订单管理模块服务层
    """

    @classmethod
    async def create_order_services(
        cls, query_db: AsyncSession, order_data: OrderCreate, user_id: int
    ) -> CrudResponseModel:
        """
        创建订单服务

        :param query_db: orm对象
        :param order_data: 订单创建数据
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            # 暂时使用固定的敏感度分值，后续实现敏感度计算服务
            sensitivity_score = 0.5

            # 创建订单实体
            order_entity = OriginalOrder(
                order_id=order_data.order_id,
                user_id=order_data.user_id,
                name=getattr(order_data, 'name', None),
                phone=getattr(order_data, 'phone', None),
                email=getattr(order_data, 'email', None),
                address=getattr(order_data, 'address', None),
                shipping_address=getattr(order_data, 'shipping_address', None),
                billing_address=getattr(order_data, 'billing_address', None),
                zip_code=getattr(order_data, 'zip_code', None),
                city=getattr(order_data, 'city', None),
                state=getattr(order_data, 'state', None),
                country=getattr(order_data, 'country', None),
                payment_info=getattr(order_data, 'payment_info', None),
                credit_card=getattr(order_data, 'credit_card', None),
                bank_account=getattr(order_data, 'bank_account', None),
                payment_method=getattr(order_data, 'payment_method', None).value
                if getattr(order_data, 'payment_method', None)
                else None,
                item_list=getattr(order_data, 'item_list', None),
                item_name=getattr(order_data, 'item_name', None),
                item_price=getattr(order_data, 'item_price', None),
                quantity=getattr(order_data, 'quantity', None),
                total_amount=getattr(order_data, 'total_amount', None),
                tax_amount=getattr(order_data, 'tax_amount', None),
                shipping_cost=getattr(order_data, 'shipping_cost', None),
                discount=getattr(order_data, 'discount', None),
                sensitivity_score=sensitivity_score,
                status='active',
            )

            # 保存订单
            await OrderDAO.create(query_db, order_entity)
            await query_db.commit()

            return CrudResponseModel(is_success=True, message='新增成功')

        except Exception as e:
            await query_db.rollback()
            logger.error(f'Error creating order: {str(e)}')
            raise ServiceException(message=f'创建订单失败: {str(e)}')

    @classmethod
    async def get_order_by_id_services(
        cls, query_db: AsyncSession, order_id: int, user_id: int
    ) -> Optional[OrderResponse]:
        """
        根据ID获取订单服务

        :param query_db: orm对象
        :param order_id: 订单ID
        :param user_id: 用户ID
        :return: 订单响应对象
        """
        try:
            order = await OrderDAO.get_by_id(query_db, order_id)
            if not order:
                return None

            # 检查权限 - 用户只能查看自己的订单或管理员可以查看所有
            # 这里暂时简化处理

            return OrderResponse(
                id=order.id,
                order_id=order.order_id,
                user_id=order.user_id,
                name=order.name,
                phone=order.phone,
                email=order.email,
                total_amount=order.total_amount,
                status=order.status,
                sensitivity_score=order.sensitivity_score,
                created_at=order.created_at,
            )

        except Exception as e:
            logger.error(f'Error getting order by id {order_id}: {str(e)}')
            raise

    @classmethod
    async def get_order_list_services(
        cls,
        query_db: AsyncSession,
        page: int = 1,
        size: int = 20,
        user_id: Optional[int] = None,
        filters: Optional[Dict] = None,
    ) -> Tuple[List[OrderResponse], int]:
        """
        获取订单列表服务

        :param query_db: orm对象
        :param page: 页码
        :param size: 每页数量
        :param user_id: 用户ID
        :param filters: 过滤条件
        :return: 订单列表和总数
        """
        try:
            orders, total = await OrderDAO.get_list(
                query_db,
                page=page,
                size=size,
                filters=filters or {},
            )

            order_responses = []
            for order in orders:
                order_responses.append(
                    OrderResponse(
                        id=order.id,
                        order_id=order.order_id,
                        user_id=order.user_id,
                        name=order.name,
                        phone=order.phone,
                        email=order.email,
                        total_amount=order.total_amount,
                        status=order.status,
                        sensitivity_score=order.sensitivity_score,
                        created_at=order.created_at,
                    )
                )

            return order_responses, total

        except Exception as e:
            logger.error(f'Error getting orders list: {str(e)}')
            raise

    @classmethod
    async def update_order_services(
        cls, query_db: AsyncSession, order_id: int, order_data: OrderUpdate, user_id: int
    ) -> CrudResponseModel:
        """
        更新订单服务

        :param query_db: orm对象
        :param order_id: 订单ID
        :param order_data: 订单更新数据
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            order = await OrderDAO.get_by_id(query_db, order_id)
            if not order:
                raise ServiceException(message='订单不存在')

            # 更新字段
            update_data = order_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(order, field):
                    setattr(order, field, value)

            # 更新时间
            order.updated_at = datetime.now(timezone.utc)

            # 保存更新
            await OrderDAO.update(query_db, order)
            await query_db.commit()

            return CrudResponseModel(is_success=True, message='更新成功')

        except Exception as e:
            await query_db.rollback()
            logger.error(f'Error updating order {order_id}: {str(e)}')
            raise

    @classmethod
    async def delete_order_services(cls, query_db: AsyncSession, order_id: int, user_id: int) -> CrudResponseModel:
        """
        删除订单服务（软删除）

        :param query_db: orm对象
        :param order_id: 订单ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            result = await OrderDAO.soft_delete(query_db, order_id)
            if not result:
                raise ServiceException(message='订单不存在')
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            logger.error(f'Error deleting order {order_id}: {str(e)}')
            raise

    @classmethod
    async def get_order_statistics_services(cls, query_db: AsyncSession) -> OrderStatistics:
        """
        获取订单统计信息服务

        :param query_db: orm对象
        :return: 订单统计对象
        """
        try:
            stats = await OrderDAO.get_statistics(query_db)
            return OrderStatistics(
                total_orders=stats['total_orders'],
                active_orders=stats['active_orders'],
                encrypted_orders=stats['encrypted_orders'],
                average_sensitivity=stats['average_sensitivity'],
                high_risk_orders=stats['high_risk_orders'],
                sensitivity_distribution=stats['sensitivity_distribution'],
            )
        except Exception as e:
            logger.error(f'Error getting order statistics: {str(e)}')
            raise

    @classmethod
    async def search_orders_services(
        cls, query_db: AsyncSession, keyword: str, page: int = 1, size: int = 20
    ) -> Tuple[List[OrderResponse], int]:
        """
        搜索订单服务

        :param query_db: orm对象
        :param keyword: 搜索关键词
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        try:
            orders, total = await OrderDAO.search_orders(query_db, keyword, page, size)

            order_responses = []
            for order in orders:
                order_responses.append(
                    OrderResponse(
                        id=order.id,
                        order_id=order.order_id,
                        user_id=order.user_id,
                        name=order.name,
                        phone=order.phone,
                        email=order.email,
                        total_amount=order.total_amount,
                        status=order.status,
                        sensitivity_score=order.sensitivity_score,
                        created_at=order.created_at,
                    )
                )

            return order_responses, total

        except Exception as e:
            logger.error(f'Error searching orders: {str(e)}')
            raise
