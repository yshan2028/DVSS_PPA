"""
分片数据访问对象 (DAO) - 异步版本
"""

from typing import List, Optional, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.custom_exception import DatabaseError
from module_dvss.entity.shard_info import ShardInfo
from utils.log_util import LogUtil

logger = LogUtil.get_logger('shard_dao')


class ShardDAO:
    """数据分片数据访问对象"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_shard(self, shard_data: dict) -> ShardInfo:
        """创建新的数据分片"""
        try:
            shard = ShardInfo(**shard_data)
            self.db.add(shard)
            await self.db.commit()
            await self.db.refresh(shard)
            return shard
        except Exception as e:
            await self.db.rollback()
            logger.error(f'创建分片失败: {e}')
            raise DatabaseError(f'创建分片失败: {str(e)}')

    async def get_shard_by_id(self, shard_id: int) -> Optional[ShardInfo]:
        """根据ID获取分片信息"""
        try:
            stmt = select(ShardInfo).where(ShardInfo.id == shard_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f'获取分片失败: {e}')
            raise DatabaseError(f'获取分片失败: {str(e)}')

    async def get_shards_by_user(self, user_id: int, page: int = 1, size: int = 20) -> Tuple[List[ShardInfo], int]:
        """分页获取用户的分片列表"""
        try:
            stmt = select(ShardInfo).where(ShardInfo.user_id == user_id)

            # 获取总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 分页查询
            stmt = stmt.order_by(desc(ShardInfo.created_at)).offset((page - 1) * size).limit(size)
            result = await self.db.execute(stmt)
            shards = result.scalars().all()

            return list(shards), total
        except Exception as e:
            logger.error(f'获取用户分片列表失败: {e}')
            raise DatabaseError(f'获取用户分片列表失败: {str(e)}')

    async def get_all_shards(self, page: int = 1, size: int = 20) -> Tuple[List[ShardInfo], int]:
        """分页获取所有分片"""
        try:
            stmt = select(ShardInfo)

            # 获取总数
            count_stmt = select(func.count(ShardInfo.id))
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 分页查询
            stmt = stmt.order_by(desc(ShardInfo.created_at)).offset((page - 1) * size).limit(size)
            result = await self.db.execute(stmt)
            shards = result.scalars().all()

            return list(shards), total
        except Exception as e:
            logger.error(f'获取分片列表失败: {e}')
            raise DatabaseError(f'获取分片列表失败: {str(e)}')

    async def update_shard(self, shard: ShardInfo) -> ShardInfo:
        """更新分片信息"""
        try:
            await self.db.commit()
            await self.db.refresh(shard)
            return shard
        except Exception as e:
            await self.db.rollback()
            logger.error(f'更新分片失败: {e}')
            raise DatabaseError(f'更新分片失败: {str(e)}')

    async def delete_shard(self, shard_id: int) -> bool:
        """删除分片"""
        try:
            stmt = select(ShardInfo).where(ShardInfo.id == shard_id)
            result = await self.db.execute(stmt)
            shard = result.scalar_one_or_none()

            if not shard:
                return False

            await self.db.delete(shard)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f'删除分片失败: {e}')
            raise DatabaseError(f'删除分片失败: {str(e)}')

    async def get_shards_by_order(self, order_id: int) -> List[ShardInfo]:
        """根据订单ID获取相关分片"""
        try:
            stmt = select(ShardInfo).where(ShardInfo.original_order_id == order_id)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f'根据订单获取分片失败: {e}')
            raise DatabaseError(f'根据订单获取分片失败: {str(e)}')

    async def get_statistics(self) -> dict:
        """获取分片统计信息"""
        try:
            # 总分片数
            total_stmt = select(func.count(ShardInfo.id))
            total_result = await self.db.execute(total_stmt)
            total_shards = total_result.scalar()

            # 活跃分片数
            active_stmt = select(func.count(ShardInfo.id)).where(ShardInfo.status == 'active')
            active_result = await self.db.execute(active_stmt)
            active_shards = active_result.scalar()

            # 存储分布统计
            storage_stmt = select(ShardInfo.storage_location, func.count(ShardInfo.id).label('count')).group_by(
                ShardInfo.storage_location
            )
            storage_result = await self.db.execute(storage_stmt)
            storage_distribution = {row[0]: row[1] for row in storage_result.fetchall()}

            return {
                'total_shards': total_shards,
                'active_shards': active_shards,
                'storage_distribution': storage_distribution,
            }
        except Exception as e:
            logger.error(f'获取分片统计失败: {e}')
            raise DatabaseError(f'获取分片统计失败: {str(e)}')

    async def get_total_count(self) -> int:
        """获取分片总数"""
        try:
            stmt = select(func.count(ShardInfo.id))
            result = await self.db.execute(stmt)
            return result.scalar()
        except Exception as e:
            logger.error(f'获取分片总数失败: {e}')
            raise DatabaseError(f'获取分片总数失败: {str(e)}')
