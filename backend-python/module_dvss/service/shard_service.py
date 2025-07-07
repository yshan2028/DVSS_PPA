"""
数据分片服务层 - 异步版本
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.custom_exception import AuthorizationError, NotFoundError, ValidationError
from module_dvss.dao.shard_dao import ShardDAO
from module_dvss.entity.shard_info import ShardInfo
from module_dvss.schemas.shard_schema import (
    ShardInfoCreate,
    ShardInfoResponse,
    ShardInfoUpdate,
    ShardListResponse,
    ShardStatsResponse,
)
from utils.log_util import LogUtil

logger = LogUtil.get_logger('shard_service')


class ShardService:
    """数据分片服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.shard_dao = ShardDAO(db)

    async def create_shard(self, request: ShardInfoCreate, current_user_id: int) -> ShardInfoResponse:
        """创建数据分片"""
        try:
            # 创建分片数据
            shard_data = {
                'user_id': current_user_id,
                'shard_index': request.shard_index,
                'shard_data': request.shard_data,
                'storage_location': request.storage_location,
                'threshold': request.threshold,
                'total_shards': request.total_shards,
                'algorithm': request.algorithm,
                'metadata': request.metadata,
                'status': 'active',
                'created_at': datetime.utcnow(),
            }

            # 如果有原始订单ID，添加到数据中
            if hasattr(request, 'original_order_id') and request.original_order_id:
                shard_data['original_order_id'] = request.original_order_id

            shard = await self.shard_dao.create_shard(shard_data)

            return ShardInfoResponse(
                id=shard.id,
                user_id=shard.user_id,
                shard_index=shard.shard_index,
                storage_location=shard.storage_location,
                threshold=shard.threshold,
                total_shards=shard.total_shards,
                algorithm=shard.algorithm,
                status=shard.status,
                created_at=shard.created_at,
            )

        except Exception as e:
            logger.error(f'Error creating shard: {str(e)}')
            raise ValidationError(f'创建分片失败: {str(e)}')

    async def get_shard_by_id(self, shard_id: int, current_user_id: int) -> Optional[ShardInfoResponse]:
        """根据ID获取分片"""
        try:
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                return None

            # 权限检查 - 用户只能查看自己的分片
            if shard.user_id != current_user_id:
                # 这里可以添加管理员权限检查
                raise AuthorizationError('无权访问此分片')

            return ShardInfoResponse(
                id=shard.id,
                user_id=shard.user_id,
                shard_index=shard.shard_index,
                storage_location=shard.storage_location,
                threshold=shard.threshold,
                total_shards=shard.total_shards,
                algorithm=shard.algorithm,
                status=shard.status,
                created_at=shard.created_at,
            )

        except Exception as e:
            logger.error(f'Error getting shard {shard_id}: {str(e)}')
            raise

    async def get_shards_list(
        self,
        page: int = 1,
        size: int = 20,
        current_user_id: int = None,
        user_id: Optional[int] = None,
    ) -> ShardListResponse:
        """获取分片列表"""
        try:
            # 如果指定了user_id且不是当前用户，需要权限检查
            if user_id and user_id != current_user_id:
                # 这里可以添加管理员权限检查
                pass

            target_user_id = user_id or current_user_id
            shards, total = await self.shard_dao.get_shards_by_user(target_user_id, page, size)

            shard_list = []
            for shard in shards:
                shard_list.append(ShardInfoResponse(
                    id=shard.id,
                    user_id=shard.user_id,
                    shard_index=shard.shard_index,
                    storage_location=shard.storage_location,
                    threshold=shard.threshold,
                    total_shards=shard.total_shards,
                    algorithm=shard.algorithm,
                    status=shard.status,
                    created_at=shard.created_at,
                ))

            return ShardListResponse(
                shards=shard_list,
                total=total,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size,
            )

        except Exception as e:
            logger.error(f'Error getting shards list: {str(e)}')
            raise

    async def update_shard(
        self, shard_id: int, request: ShardInfoUpdate, current_user_id: int
    ) -> ShardInfoResponse:
        """更新分片"""
        try:
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError('分片不存在')

            # 权限检查
            if shard.user_id != current_user_id:
                raise AuthorizationError('无权修改此分片')

            # 更新字段
            update_data = request.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(shard, field):
                    setattr(shard, field, value)

            shard.updated_at = datetime.utcnow()
            updated_shard = await self.shard_dao.update_shard(shard)

            return ShardInfoResponse(
                id=updated_shard.id,
                user_id=updated_shard.user_id,
                shard_index=updated_shard.shard_index,
                storage_location=updated_shard.storage_location,
                threshold=updated_shard.threshold,
                total_shards=updated_shard.total_shards,
                algorithm=updated_shard.algorithm,
                status=updated_shard.status,
                created_at=updated_shard.created_at,
            )

        except Exception as e:
            logger.error(f'Error updating shard {shard_id}: {str(e)}')
            raise

    async def delete_shard(self, shard_id: int, current_user_id: int) -> bool:
        """删除分片"""
        try:
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError('分片不存在')

            # 权限检查
            if shard.user_id != current_user_id:
                raise AuthorizationError('无权删除此分片')

            return await self.shard_dao.delete_shard(shard_id)

        except Exception as e:
            logger.error(f'Error deleting shard {shard_id}: {str(e)}')
            raise

    async def get_shard_statistics(self) -> ShardStatsResponse:
        """获取分片统计信息"""
        try:
            stats = await self.shard_dao.get_statistics()

            return ShardStatsResponse(
                total_shards=stats['total_shards'],
                active_shards=stats['active_shards'],
                storage_distribution=stats['storage_distribution'],
            )

        except Exception as e:
            logger.error(f'Error getting shard statistics: {str(e)}')
            raise

    async def get_shards_by_order(self, order_id: int, current_user_id: int) -> List[ShardInfoResponse]:
        """根据订单ID获取相关分片"""
        try:
            shards = await self.shard_dao.get_shards_by_order(order_id)

            shard_list = []
            for shard in shards:
                # 权限检查
                if shard.user_id != current_user_id:
                    continue

                shard_list.append(ShardInfoResponse(
                    id=shard.id,
                    user_id=shard.user_id,
                    shard_index=shard.shard_index,
                    storage_location=shard.storage_location,
                    threshold=shard.threshold,
                    total_shards=shard.total_shards,
                    algorithm=shard.algorithm,
                    status=shard.status,
                    created_at=shard.created_at,
                ))

            return shard_list

        except Exception as e:
            logger.error(f'Error getting shards by order {order_id}: {str(e)}')
            raise
