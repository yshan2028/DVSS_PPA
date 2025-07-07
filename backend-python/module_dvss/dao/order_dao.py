"""
订单数据访问层 (DAO) - 异步版本
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvss.entity.encrypted_order import EncryptedOrder
from module_dvss.entity.original_order import OriginalOrder
from utils.log_util import LogUtil

logger = LogUtil.get_logger('order_dao')


class OrderDAO:
    """
    订单管理模块数据库操作层
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    @classmethod
    async def create(cls, db: AsyncSession, order: OriginalOrder) -> OriginalOrder:
        """
        创建订单

        :param db: orm对象
        :param order: 订单对象
        :return: 创建的订单对象
        """
        try:
            db.add(order)
            await db.flush()
            await db.refresh(order)
            return order
        except Exception as e:
            logger.error(f'Error creating order: {str(e)}')
            raise

    @classmethod
    async def get_by_id(cls, db: AsyncSession, order_id: int) -> Optional[OriginalOrder]:
        """
        根据ID获取订单

        :param db: orm对象
        :param order_id: 订单ID
        :return: 订单对象
        """
        try:
            stmt = select(OriginalOrder).where(and_(OriginalOrder.id == order_id, OriginalOrder.status != 'deleted'))
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting order by id {order_id}: {str(e)}')
            raise

    @classmethod
    async def get_by_order_id(cls, db: AsyncSession, order_id: str) -> Optional[OriginalOrder]:
        """
        根据订单号获取订单

        :param db: orm对象
        :param order_id: 订单号
        :return: 订单对象
        """
        try:
            stmt = select(OriginalOrder).where(
                and_(OriginalOrder.order_id == order_id, OriginalOrder.status != 'deleted')
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting order by order_id {order_id}: {str(e)}')
            raise

    @classmethod
    async def get_list(
        cls,
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = 'created_at',
        order_direction: str = 'desc',
    ) -> Tuple[List[OriginalOrder], int]:
        """
        获取订单列表

        :param db: orm对象
        :param page: 页码
        :param size: 每页数量
        :param filters: 过滤条件
        :param order_by: 排序字段
        :param order_direction: 排序方向
        :return: 订单列表和总数
        """
        try:
            stmt = select(OriginalOrder).where(OriginalOrder.status != 'deleted')

            # 应用过滤条件
            if filters:
                for key, value in filters.items():
                    if hasattr(OriginalOrder, key) and value is not None:
                        if key == 'user_id':
                            stmt = stmt.where(OriginalOrder.user_id == value)
                        elif key == 'status':
                            stmt = stmt.where(OriginalOrder.status == value)
                        elif key == 'start_date':
                            stmt = stmt.where(OriginalOrder.created_at >= value)
                        elif key == 'end_date':
                            stmt = stmt.where(OriginalOrder.created_at <= value)
                        elif key == 'keyword':
                            # 模糊搜索
                            stmt = stmt.where(
                                or_(
                                    OriginalOrder.order_id.like(f'%{value}%'),
                                    OriginalOrder.name.like(f'%{value}%'),
                                    OriginalOrder.phone.like(f'%{value}%'),
                                    OriginalOrder.email.like(f'%{value}%'),
                                )
                            )
                        elif key == 'min_amount':
                            stmt = stmt.where(OriginalOrder.total_amount >= value)
                        elif key == 'max_amount':
                            stmt = stmt.where(OriginalOrder.total_amount <= value)
                        elif key == 'sensitivity_level':
                            # 根据敏感度级别过滤
                            if value == 'low':
                                stmt = stmt.where(OriginalOrder.sensitivity_score < 0.3)
                            elif value == 'medium':
                                stmt = stmt.where(
                                    and_(OriginalOrder.sensitivity_score >= 0.3, OriginalOrder.sensitivity_score < 0.7)
                                )
                            elif value == 'high':
                                stmt = stmt.where(OriginalOrder.sensitivity_score >= 0.7)

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await db.execute(count_stmt)
            total = total_result.scalar()

            # 排序
            if hasattr(OriginalOrder, order_by):
                if order_direction.lower() == 'desc':
                    stmt = stmt.order_by(desc(getattr(OriginalOrder, order_by)))
                else:
                    stmt = stmt.order_by(asc(getattr(OriginalOrder, order_by)))

            # 分页
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await db.execute(stmt)
            orders = result.scalars().all()

            return list(orders), total

        except Exception as e:
            logger.error(f'Error getting order list: {str(e)}')
            raise

    @classmethod
    async def update(cls, db: AsyncSession, order: OriginalOrder) -> OriginalOrder:
        """
        更新订单

        :param db: orm对象
        :param order: 订单对象
        :return: 更新后的订单对象
        """
        try:
            order.updated_at = datetime.now(timezone.utc)
            await db.flush()
            await db.refresh(order)
            return order
        except Exception as e:
            logger.error(f'Error updating order {order.id}: {str(e)}')
            raise

    @classmethod
    async def delete(cls, db: AsyncSession, order_id: int) -> bool:
        """
        删除订单（物理删除）

        :param db: orm对象
        :param order_id: 订单ID
        :return: 删除结果
        """
        try:
            stmt = select(OriginalOrder).where(OriginalOrder.id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                return False

            await db.delete(order)
            return True
        except Exception as e:
            logger.error(f'Error deleting order {order_id}: {str(e)}')
            raise

    @classmethod
    async def soft_delete(cls, db: AsyncSession, order_id: int) -> bool:
        """
        软删除订单

        :param db: orm对象
        :param order_id: 订单ID
        :return: 删除结果
        """
        try:
            stmt = select(OriginalOrder).where(OriginalOrder.id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()

            if not order:
                return False

            order.status = 'deleted'
            order.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f'Error soft deleting order {order_id}: {str(e)}')
            raise

    @classmethod
    async def get_orders_by_user(
        cls, db: AsyncSession, user_id: str, page: int = 1, size: int = 10
    ) -> Tuple[List[OriginalOrder], int]:
        """
        获取用户的订单列表

        :param db: orm对象
        :param user_id: 用户ID
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        return await cls.get_list(db, page=page, size=size, filters={'user_id': user_id})

    @classmethod
    async def get_orders_by_status(
        cls, db: AsyncSession, status: str, page: int = 1, size: int = 10
    ) -> Tuple[List[OriginalOrder], int]:
        """
        根据状态获取订单列表

        :param db: orm对象
        :param status: 订单状态
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        return await cls.get_list(db, page=page, size=size, filters={'status': status})

    @classmethod
    async def get_sensitive_orders(
        cls, db: AsyncSession, threshold: float = 0.7, page: int = 1, size: int = 10
    ) -> Tuple[List[OriginalOrder], int]:
        """
        获取高敏感度订单

        :param db: orm对象
        :param threshold: 敏感度阈值
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        try:
            stmt = (
                select(OriginalOrder)
                .where(and_(OriginalOrder.sensitivity_score >= threshold, OriginalOrder.status != 'deleted'))
                .order_by(desc(OriginalOrder.sensitivity_score))
            )

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await db.execute(count_stmt)
            total = total_result.scalar()

            # 分页
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await db.execute(stmt)
            orders = result.scalars().all()

            return list(orders), total

        except Exception as e:
            logger.error(f'Error getting sensitive orders: {str(e)}')
            raise

    @classmethod
    async def get_statistics(cls, db: AsyncSession) -> Dict[str, Any]:
        """
        获取订单统计信息

        :param db: orm对象
        :return: 统计信息字典
        """
        try:
            # 基础统计
            total_stmt = select(func.count(OriginalOrder.id)).where(OriginalOrder.status != 'deleted')
            total_result = await db.execute(total_stmt)
            total_orders = total_result.scalar()

            active_stmt = select(func.count(OriginalOrder.id)).where(OriginalOrder.status == 'active')
            active_result = await db.execute(active_stmt)
            active_orders = active_result.scalar()

            encrypted_stmt = select(func.count(OriginalOrder.id)).where(OriginalOrder.status == 'encrypted')
            encrypted_result = await db.execute(encrypted_stmt)
            encrypted_orders = encrypted_result.scalar()

            # 平均敏感度
            avg_stmt = select(func.avg(OriginalOrder.sensitivity_score)).where(OriginalOrder.status != 'deleted')
            avg_result = await db.execute(avg_stmt)
            avg_sensitivity = avg_result.scalar() or 0.0

            # 高风险订单数（敏感度 >= 0.7）
            high_risk_stmt = select(func.count(OriginalOrder.id)).where(
                and_(OriginalOrder.sensitivity_score >= 0.7, OriginalOrder.status != 'deleted')
            )
            high_risk_result = await db.execute(high_risk_stmt)
            high_risk_orders = high_risk_result.scalar()

            # 敏感度分布
            low_stmt = select(func.count(OriginalOrder.id)).where(
                and_(OriginalOrder.sensitivity_score < 0.3, OriginalOrder.status != 'deleted')
            )
            low_result = await db.execute(low_stmt)

            medium_stmt = select(func.count(OriginalOrder.id)).where(
                and_(
                    OriginalOrder.sensitivity_score >= 0.3,
                    OriginalOrder.sensitivity_score < 0.7,
                    OriginalOrder.status != 'deleted',
                )
            )
            medium_result = await db.execute(medium_stmt)

            high_stmt = select(func.count(OriginalOrder.id)).where(
                and_(OriginalOrder.sensitivity_score >= 0.7, OriginalOrder.status != 'deleted')
            )
            high_result = await db.execute(high_stmt)

            sensitivity_distribution = {
                'low': low_result.scalar(),
                'medium': medium_result.scalar(),
                'high': high_result.scalar(),
            }

            return {
                'total_orders': total_orders,
                'active_orders': active_orders,
                'encrypted_orders': encrypted_orders,
                'average_sensitivity': round(avg_sensitivity, 2),
                'high_risk_orders': high_risk_orders,
                'sensitivity_distribution': sensitivity_distribution,
            }

        except Exception as e:
            logger.error(f'Error getting order statistics: {str(e)}')
            raise

    @classmethod
    async def search_orders(
        cls, db: AsyncSession, keyword: str, page: int = 1, size: int = 10
    ) -> Tuple[List[OriginalOrder], int]:
        """
        搜索订单

        :param db: orm对象
        :param keyword: 搜索关键词
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        return await cls.get_list(db, page=page, size=size, filters={'keyword': keyword})

    @classmethod
    async def get_orders_by_date_range(
        cls, db: AsyncSession, start_date: datetime, end_date: datetime, page: int = 1, size: int = 10
    ) -> Tuple[List[OriginalOrder], int]:
        """
        根据日期范围获取订单

        :param db: orm对象
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param page: 页码
        :param size: 每页数量
        :return: 订单列表和总数
        """
        return await cls.get_list(db, page=page, size=size, filters={'start_date': start_date, 'end_date': end_date})

    @classmethod
    async def get_total_count(cls, db: AsyncSession) -> int:
        """
        获取订单总数

        :param db: orm对象
        :return: 订单总数
        """
        try:
            stmt = select(func.count(OriginalOrder.id)).where(OriginalOrder.status != 'deleted')
            result = await db.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f'Error getting total count: {str(e)}')
            raise

    # 加密订单相关方法
    @classmethod
    async def create_encrypted_order(cls, db: AsyncSession, encrypted_order: EncryptedOrder) -> EncryptedOrder:
        """
        创建加密订单

        :param db: orm对象
        :param encrypted_order: 加密订单对象
        :return: 创建的加密订单对象
        """
        try:
            db.add(encrypted_order)
            await db.flush()
            await db.refresh(encrypted_order)
            return encrypted_order
        except Exception as e:
            logger.error(f'Error creating encrypted order: {str(e)}')
            raise

    @classmethod
    async def get_encrypted_order_by_id(cls, db: AsyncSession, encrypted_order_id: int) -> Optional[EncryptedOrder]:
        """
        根据ID获取加密订单

        :param db: orm对象
        :param encrypted_order_id: 加密订单ID
        :return: 加密订单对象
        """
        try:
            stmt = select(EncryptedOrder).where(EncryptedOrder.id == encrypted_order_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting encrypted order by id {encrypted_order_id}: {str(e)}')
            raise

    @classmethod
    async def get_encrypted_order_by_original_id(
        cls, db: AsyncSession, original_order_id: int
    ) -> Optional[EncryptedOrder]:
        """
        根据原始订单ID获取加密订单

        :param db: orm对象
        :param original_order_id: 原始订单ID
        :return: 加密订单对象
        """
        try:
            stmt = select(EncryptedOrder).where(EncryptedOrder.original_order_id == original_order_id)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting encrypted order by original_id {original_order_id}: {str(e)}')
            raise

    @classmethod
    async def get_by_condition(
        cls,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        order_by: str = 'created_at',
        order_direction: str = 'desc',
    ) -> Tuple[List[OriginalOrder], int]:
        """
        根据条件获取订单列表（别名方法）
        """
        return await cls.get_list(db, page, size, filters, order_by, order_direction)

    async def query_orders(
        self, filters: Dict[str, Any] = None, page: int = 1, size: int = 20
    ) -> Tuple[List[OriginalOrder], int]:
        """查询订单（实例方法版本）"""
        return await self.get_by_condition(self.db, filters, page, size)

    async def get_orders_by_ids(self, order_ids: List[int]) -> List[OriginalOrder]:
        """根据ID列表获取订单"""
        try:
            stmt = select(OriginalOrder).where(OriginalOrder.id.in_(order_ids))
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f'Error getting orders by ids: {str(e)}')
            raise

    async def delete_orders(self, order_ids: List[int]) -> int:
        """批量删除订单（软删除）"""
        try:
            stmt = select(OriginalOrder).where(OriginalOrder.id.in_(order_ids))
            result = await self.db.execute(stmt)
            orders = result.scalars().all()

            count = 0
            for order in orders:
                order.status = 'deleted'
                count += 1

            await self.db.commit()
            return count
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error deleting orders: {str(e)}')
            raise

    async def get_order_statistics(self) -> Dict[str, Any]:
        """获取订单统计信息"""
        try:
            # 总订单数
            total_stmt = select(func.count(OriginalOrder.id)).where(OriginalOrder.status != 'deleted')
            total_result = await self.db.execute(total_stmt)
            total_orders = total_result.scalar()

            # 按状态统计
            status_stmt = (
                select(OriginalOrder.status, func.count(OriginalOrder.id).label('count'))
                .where(OriginalOrder.status != 'deleted')
                .group_by(OriginalOrder.status)
            )
            status_result = await self.db.execute(status_stmt)
            status_stats = {row[0]: row[1] for row in status_result.fetchall()}

            return {
                'total_orders': total_orders,
                'status_distribution': status_stats,
                'encrypted_orders': 0,  # 需要从加密订单表获取
            }
        except Exception as e:
            logger.error(f'Error getting order statistics: {str(e)}')
            raise

    async def create_order(self, order_data: Dict[str, Any]) -> OriginalOrder:
        """创建订单（实例方法版本）"""
        try:
            order = OriginalOrder(**order_data)
            return await self.create(self.db, order)
        except Exception as e:
            logger.error(f'Error creating order: {str(e)}')
            raise

    async def get_encrypted_by_id(self, encrypted_order_id: int) -> Optional[EncryptedOrder]:
        """获取加密订单（实例方法版本）"""
        return await self.get_encrypted_order_by_id(self.db, encrypted_order_id)

    async def create_encrypted_order_instance(self, encrypted_order: EncryptedOrder) -> EncryptedOrder:
        """创建加密订单（实例方法版本）"""
        return await self.create_encrypted_order(self.db, encrypted_order)
