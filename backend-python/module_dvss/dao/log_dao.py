"""
日志数据访问层 (DAO) - 异步版本
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvss.entity.operation_log import OperationLog
from module_dvss.schemas.log_schema import LogSearchRequest, SecurityLogCreate, SystemLogCreate
from utils.log_util import LogUtil

logger = LogUtil.get_logger('log_dao')


class LogDAO:
    """日志数据访问对象"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_operation_log(self, log: OperationLog) -> OperationLog:
        """创建操作日志"""
        try:
            self.db.add(log)
            await self.db.commit()
            await self.db.refresh(log)
            return log
        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error creating operation log: {str(e)}')
            raise

    async def get_operation_log_by_id(self, log_id: int) -> Optional[OperationLog]:
        """根据ID获取操作日志"""
        try:
            stmt = select(OperationLog).where(OperationLog.id == log_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'Error getting operation log by id {log_id}: {str(e)}')
            raise

    async def get_operation_logs_list(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = 'created_at',
        order_direction: str = 'desc',
    ) -> Tuple[List[OperationLog], int]:
        """获取操作日志列表"""
        try:
            stmt = select(OperationLog)

            # 应用过滤条件
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        if key == 'user_id':
                            stmt = stmt.where(OperationLog.user_id == value)
                        elif key == 'operation_type':
                            stmt = stmt.where(OperationLog.operation_type == value)
                        elif key == 'resource_type':
                            stmt = stmt.where(OperationLog.resource_type == value)
                        elif key == 'resource_id':
                            stmt = stmt.where(OperationLog.resource_id == value)
                        elif key == 'ip_address':
                            stmt = stmt.where(OperationLog.ip_address == value)
                        elif key == 'start_date':
                            stmt = stmt.where(OperationLog.created_at >= value)
                        elif key == 'end_date':
                            stmt = stmt.where(OperationLog.created_at <= value)
                        elif key == 'is_success':
                            stmt = stmt.where(OperationLog.status == ('success' if value else 'failure'))

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 排序
            if hasattr(OperationLog, order_by):
                if order_direction.lower() == 'desc':
                    stmt = stmt.order_by(desc(getattr(OperationLog, order_by)))
                else:
                    stmt = stmt.order_by(asc(getattr(OperationLog, order_by)))

            # 分页
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await self.db.execute(stmt)
            logs = result.scalars().all()

            return list(logs), total

        except Exception as e:
            logger.error(f'Error getting operation logs list: {str(e)}')
            raise

    async def search_logs(self, search_request: LogSearchRequest, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """搜索日志"""
        try:
            stmt = select(OperationLog)

            # 应用搜索条件
            if search_request.user_id:
                stmt = stmt.where(OperationLog.user_id == search_request.user_id)

            if search_request.operation_type:
                stmt = stmt.where(OperationLog.operation_type == search_request.operation_type)

            if search_request.resource_type:
                stmt = stmt.where(OperationLog.resource_type == search_request.resource_type)

            if search_request.resource_id:
                stmt = stmt.where(OperationLog.resource_id == search_request.resource_id)

            if search_request.ip_address:
                stmt = stmt.where(OperationLog.ip_address == search_request.ip_address)

            if search_request.start_date:
                stmt = stmt.where(OperationLog.created_at >= search_request.start_date)

            if search_request.end_date:
                stmt = stmt.where(OperationLog.created_at <= search_request.end_date)

            if search_request.is_success is not None:
                status = 'success' if search_request.is_success else 'failure'
                stmt = stmt.where(OperationLog.status == status)

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 分页和排序
            stmt = stmt.order_by(desc(OperationLog.created_at))
            stmt = stmt.offset((page - 1) * size).limit(size)
            result = await self.db.execute(stmt)
            logs = result.scalars().all()

            return {
                'logs': list(logs),
                'total': total,
                'page': page,
                'size': size,
                'total_pages': (total + size - 1) // size,
            }

        except Exception as e:
            logger.error(f'Error searching logs: {str(e)}')
            raise

    async def get_logs_by_user(self, user_id: int, page: int = 1, size: int = 20) -> Tuple[List[OperationLog], int]:
        """获取用户操作日志"""
        return await self.get_operation_logs_list(page=page, size=size, filters={'user_id': user_id})

    async def get_logs_by_type(
        self, operation_type: str, page: int = 1, size: int = 20
    ) -> Tuple[List[OperationLog], int]:
        """根据操作类型获取日志"""
        return await self.get_operation_logs_list(page=page, size=size, filters={'operation_type': operation_type})

    async def get_logs_by_date(self, date: datetime, page: int = 1, size: int = 20) -> Tuple[List[OperationLog], int]:
        """根据日期获取日志"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        return await self.get_operation_logs_list(
            page=page, size=size, filters={'start_date': start_date, 'end_date': end_date}
        )

    async def get_logs_by_time_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, size: int = 20
    ) -> Tuple[List[OperationLog], int]:
        """根据时间范围获取日志"""
        return await self.get_operation_logs_list(
            page=page, size=size, filters={'start_date': start_date, 'end_date': end_date}
        )

    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取日志统计信息"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            # 总操作数
            total_stmt = select(func.count(OperationLog.id)).where(OperationLog.created_at >= start_date)
            total_result = await self.db.execute(total_stmt)
            total_operations = total_result.scalar()

            # 成功操作数
            success_stmt = select(func.count(OperationLog.id)).where(
                and_(OperationLog.created_at >= start_date, OperationLog.status == 'success')
            )
            success_result = await self.db.execute(success_stmt)
            success_operations = success_result.scalar()

            # 失败操作数
            failure_operations = total_operations - success_operations

            # 操作类型分布
            type_stmt = (
                select(OperationLog.operation_type, func.count(OperationLog.id).label('count'))
                .where(OperationLog.created_at >= start_date)
                .group_by(OperationLog.operation_type)
            )
            type_result = await self.db.execute(type_stmt)
            operation_types = {row[0]: row[1] for row in type_result.fetchall()}

            # 资源类型分布
            resource_stmt = (
                select(OperationLog.resource_type, func.count(OperationLog.id).label('count'))
                .where(OperationLog.created_at >= start_date)
                .group_by(OperationLog.resource_type)
            )
            resource_result = await self.db.execute(resource_stmt)
            resource_types = {row[0]: row[1] for row in resource_result.fetchall()}

            return {
                'total_operations': total_operations,
                'success_operations': success_operations,
                'failure_operations': failure_operations,
                'success_rate': round(success_operations / total_operations * 100, 2) if total_operations > 0 else 0,
                'operation_types': operation_types,
                'resource_types': resource_types,
                'period_days': days,
            }

        except Exception as e:
            logger.error(f'Error getting log statistics: {str(e)}')
            raise

    async def delete_old_logs(self, days: int = 90) -> int:
        """删除旧日志"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = select(OperationLog).where(OperationLog.created_at < cutoff_date)
            result = await self.db.execute(stmt)
            logs_to_delete = result.scalars().all()

            count = len(logs_to_delete)
            for log in logs_to_delete:
                await self.db.delete(log)

            await self.db.commit()
            return count

        except Exception as e:
            await self.db.rollback()
            logger.error(f'Error deleting old logs: {str(e)}')
            raise

    async def get_total_count(self) -> int:
        """获取日志总数"""
        try:
            stmt = select(func.count(OperationLog.id))
            result = await self.db.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f'Error getting total count: {str(e)}')
            raise

    async def create_system_log(self, log_data: SystemLogCreate) -> Any:
        """创建系统日志"""
        # 这里可以实现系统日志的创建逻辑
        # 暂时返回模拟对象
        logger.info(f'Creating system log: {log_data}')
        return {'id': 1, 'message': 'System log created'}

    async def create_security_log(self, log_data: SecurityLogCreate) -> Any:
        """创建安全日志"""
        # 这里可以实现安全日志的创建逻辑
        # 暂时返回模拟对象
        logger.info(f'Creating security log: {log_data}')
        return {'id': 1, 'message': 'Security log created'}
