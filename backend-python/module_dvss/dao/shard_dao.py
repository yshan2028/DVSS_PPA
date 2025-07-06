"""
分片数据访问对象
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from module_dvss.entity.shard_info import ShardInfo, StorageNode
from module_dvss.entity.user import User
from exceptions.custom_exception import NotFoundError, ConflictError, DatabaseError
from utils.log_util import LogUtil

logger = LogUtil.get_logger("shard_dao")

class ShardDAO:
    """数据分片数据访问对象"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_shard(self, shard_data: dict) -> ShardInfo:
        """创建新的数据分片"""
        try:
            shard = ShardInfo(**shard_data)
            self.db.add(shard)
            self.db.commit()
            self.db.refresh(shard)
            return shard
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建分片失败: {e}")
            raise DatabaseError(f"创建分片失败: {str(e)}")
    
    def get_shard_by_id(self, shard_id: int) -> Optional[ShardInfo]:
        """根据ID获取分片信息"""
        try:
            return self.db.query(ShardInfo).filter(ShardInfo.id == shard_id).first()
        except Exception as e:
            logger.error(f"获取分片失败: {e}")
            raise DatabaseError(f"获取分片失败: {str(e)}")
    
    def get_shards_by_user(self, user_id: int, page: int = 1, size: int = 20) -> Tuple[List[ShardInfo], int]:
        """分页获取用户的分片列表"""
        try:
            query = self.db.query(ShardInfo).filter(ShardInfo.user_id == user_id)
            total = query.count()
            shards = query.order_by(desc(ShardInfo.created_at)).offset(
                (page - 1) * size
            ).limit(size).all()
            return shards, total
        except Exception as e:
            logger.error(f"获取用户分片列表失败: {e}")
            raise DatabaseError(f"获取用户分片列表失败: {str(e)}")
