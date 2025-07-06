"""
数据分片数据访问对象 (DAO)
Data Access Object - 处理分片相关的数据库操作
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta

from module_dvss.entity.do.shard_do import DataShard, ShardPermission, AccessLog
from module_dvss.entity.do.user_do import DvssUser
from exceptions.custom_exception import NotFoundError, ConflictError, DatabaseError, AuthorizationError
from utils.page_util import PageUtil
from utils.log_util import LogUtil

logger = LogUtil.get_logger("shard_dao")

class ShardDao:
    """数据分片数据访问对象"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_shard(self, shard_data: dict) -> DataShard:
        """
        创建数据分片
        
        Args:
            shard_data: 分片数据
            
        Returns:
            DataShard: 创建的分片对象
            
        Raises:
            ConflictError: 分片ID已存在
            DatabaseError: 数据库操作失败
        """
        try:
            # 检查分片ID是否已存在
            existing_shard = self.db.query(DataShard).filter(
                DataShard.shard_id == shard_data['shard_id']
            ).first()
            
            if existing_shard:
                raise ConflictError("分片ID已存在")
            
            # 创建分片对象
            shard = DataShard(**shard_data)
            
            # 添加到会话
            self.db.add(shard)
            self.db.commit()
            self.db.refresh(shard)
            
            logger.info(f"Shard created successfully: {shard.shard_id}")
            return shard
            
        except (ConflictError, DatabaseError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating shard: {e}")
            raise DatabaseError(f"创建分片失败: {str(e)}")
    
    def get_shard_by_id(self, shard_id: int) -> Optional[DataShard]:
        """
        根据ID获取分片
        
        Args:
            shard_id: 分片数据库ID
            
        Returns:
            Optional[DataShard]: 分片对象或None
        """
        try:
            return self.db.query(DataShard).options(
                joinedload(DataShard.permissions),
                joinedload(DataShard.owner)
            ).filter(DataShard.id == shard_id).first()
        except Exception as e:
            logger.error(f"Error getting shard by id {shard_id}: {e}")
            raise DatabaseError(f"获取分片失败: {str(e)}")
    
    def get_shard_by_shard_id(self, shard_id: str) -> Optional[DataShard]:
        """
        根据分片ID获取分片
        
        Args:
            shard_id: 分片唯一标识
            
        Returns:
            Optional[DataShard]: 分片对象或None
        """
        try:
            return self.db.query(DataShard).options(
                joinedload(DataShard.permissions),
                joinedload(DataShard.owner)
            ).filter(DataShard.shard_id == shard_id).first()
        except Exception as e:
            logger.error(f"Error getting shard by shard_id {shard_id}: {e}")
            raise DatabaseError(f"获取分片失败: {str(e)}")
    
    def get_shards_by_file_hash(self, file_hash: str) -> List[DataShard]:
        """
        根据文件哈希获取所有相关分片
        
        Args:
            file_hash: 原始文件哈希
            
        Returns:
            List[DataShard]: 分片列表
        """
        try:
            return self.db.query(DataShard).filter(
                DataShard.original_file_hash == file_hash
            ).order_by(DataShard.shard_index).all()
        except Exception as e:
            logger.error(f"Error getting shards by file hash {file_hash}: {e}")
            raise DatabaseError(f"获取分片失败: {str(e)}")
    
    def update_shard(self, shard_id: int, update_data: dict) -> DataShard:
        """
        更新分片信息
        
        Args:
            shard_id: 分片ID
            update_data: 更新数据
            
        Returns:
            DataShard: 更新后的分片对象
            
        Raises:
            NotFoundError: 分片不存在
            DatabaseError: 数据库操作失败
        """
        try:
            shard = self.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 更新字段
            for key, value in update_data.items():
                if hasattr(shard, key) and value is not None:
                    setattr(shard, key, value)
            
            shard.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(shard)
            
            logger.info(f"Shard updated successfully: {shard.shard_id}")
            return shard
            
        except (NotFoundError, DatabaseError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating shard {shard_id}: {e}")
            raise DatabaseError(f"更新分片失败: {str(e)}")
    
    def delete_shard(self, shard_id: int) -> bool:
        """
        删除分片 (物理删除)
        
        Args:
            shard_id: 分片ID
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            NotFoundError: 分片不存在
            DatabaseError: 数据库操作失败
        """
        try:
            shard = self.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 删除相关权限和访问日志 (级联删除)
            self.db.delete(shard)
            self.db.commit()
            
            logger.info(f"Shard deleted successfully: {shard.shard_id}")
            return True
            
        except (NotFoundError, DatabaseError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting shard {shard_id}: {e}")
            raise DatabaseError(f"删除分片失败: {str(e)}")
    
    def list_shards(self, page: int = 1, page_size: int = 20, 
                    filters: Optional[dict] = None, user_id: Optional[int] = None) -> Tuple[List[DataShard], int, int, int]:
        """
        分页获取分片列表
        
        Args:
            page: 页码
            page_size: 每页大小
            filters: 过滤条件
            user_id: 用户ID (只返回用户有权限的分片)
            
        Returns:
            Tuple[List[DataShard], int, int, int]: (分片列表, 总数, 页码, 每页大小)
        """
        try:
            query = self.db.query(DataShard)
            
            # 如果指定了用户ID，只返回用户有权限的分片
            if user_id:
                query = query.filter(
                    or_(
                        DataShard.owner_id == user_id,
                        DataShard.id.in_(
                            self.db.query(ShardPermission.shard_id).filter(
                                and_(
                                    ShardPermission.user_id == user_id,
                                    ShardPermission.is_active == True,
                                    or_(
                                        ShardPermission.valid_until.is_(None),
                                        ShardPermission.valid_until > datetime.now()
                                    )
                                )
                            )
                        )
                    )
                )
            
            # 应用过滤条件
            if filters:
                if filters.get('keyword'):
                    keyword = f"%{filters['keyword']}%"
                    query = query.filter(
                        or_(
                            DataShard.shard_id.ilike(keyword),
                            DataShard.original_file_name.ilike(keyword),
                            DataShard.storage_node.ilike(keyword)
                        )
                    )
                
                if filters.get('shard_type'):
                    query = query.filter(DataShard.shard_type == filters['shard_type'])
                
                if filters.get('status'):
                    query = query.filter(DataShard.status == filters['status'])
                
                if filters.get('owner_id'):
                    query = query.filter(DataShard.owner_id == filters['owner_id'])
                
                if filters.get('file_name'):
                    query = query.filter(DataShard.original_file_name.ilike(f"%{filters['file_name']}%"))
                
                if filters.get('created_from'):
                    query = query.filter(DataShard.created_at >= filters['created_from'])
                
                if filters.get('created_to'):
                    query = query.filter(DataShard.created_at <= filters['created_to'])
            
            # 排序
            query = query.order_by(desc(DataShard.created_at))
            
            # 分页
            return PageUtil.paginate(query, page, page_size)
            
        except Exception as e:
            logger.error(f"Error listing shards: {e}")
            raise DatabaseError(f"获取分片列表失败: {str(e)}")
    
    def update_access_time(self, shard_id: int) -> bool:
        """
        更新分片访问时间和计数
        
        Args:
            shard_id: 分片ID
            
        Returns:
            bool: 更新成功返回True
        """
        try:
            shard = self.get_shard_by_id(shard_id)
            if shard:
                shard.last_accessed = datetime.now()
                shard.access_count = (shard.access_count or 0) + 1
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating access time for shard {shard_id}: {e}")
            return False
    
    def get_shard_stats(self, user_id: Optional[int] = None) -> dict:
        """
        获取分片统计信息
        
        Args:
            user_id: 用户ID (如果指定，只统计用户相关的分片)
            
        Returns:
            dict: 统计信息
        """
        try:
            query = self.db.query(DataShard)
            
            if user_id:
                query = query.filter(
                    or_(
                        DataShard.owner_id == user_id,
                        DataShard.id.in_(
                            self.db.query(ShardPermission.shard_id).filter(
                                and_(
                                    ShardPermission.user_id == user_id,
                                    ShardPermission.is_active == True
                                )
                            )
                        )
                    )
                )
            
            total_shards = query.count()
            active_shards = query.filter(DataShard.status == "active").count()
            corrupted_shards = query.filter(DataShard.status == "corrupted").count()
            
            # 计算总存储大小
            total_storage_size = self.db.query(func.sum(DataShard.shard_size)).scalar() or 0
            
            # 计算文件数量
            total_files = self.db.query(func.count(func.distinct(DataShard.original_file_hash))).scalar() or 0
            
            # 平均分片大小
            average_shard_size = total_storage_size / total_shards if total_shards > 0 else 0
            
            # 最常访问的分片
            most_accessed_shards = query.order_by(desc(DataShard.access_count)).limit(5).all()
            
            return {
                "total_shards": total_shards,
                "active_shards": active_shards,
                "corrupted_shards": corrupted_shards,
                "total_storage_size": total_storage_size,
                "total_files": total_files,
                "average_shard_size": average_shard_size,
                "most_accessed_shards": [shard.to_dict() for shard in most_accessed_shards]
            }
            
        except Exception as e:
            logger.error(f"Error getting shard stats: {e}")
            raise DatabaseError(f"获取分片统计失败: {str(e)}")

class ShardPermissionDao:
    """分片权限数据访问对象"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def grant_permission(self, permission_data: dict) -> ShardPermission:
        """
        授予分片权限
        
        Args:
            permission_data: 权限数据
            
        Returns:
            ShardPermission: 权限对象
        """
        try:
            # 检查是否已存在权限
            existing_permission = self.db.query(ShardPermission).filter(
                and_(
                    ShardPermission.shard_id == permission_data['shard_id'],
                    ShardPermission.user_id == permission_data['user_id'],
                    ShardPermission.is_active == True
                )
            ).first()
            
            if existing_permission:
                # 更新现有权限
                for key, value in permission_data.items():
                    if hasattr(existing_permission, key) and value is not None:
                        setattr(existing_permission, key, value)
                existing_permission.updated_at = datetime.now()
                self.db.commit()
                self.db.refresh(existing_permission)
                return existing_permission
            else:
                # 创建新权限
                permission = ShardPermission(**permission_data)
                self.db.add(permission)
                self.db.commit()
                self.db.refresh(permission)
                return permission
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error granting permission: {e}")
            raise DatabaseError(f"授予权限失败: {str(e)}")
    
    def revoke_permission(self, shard_id: int, user_id: int) -> bool:
        """
        撤销分片权限
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            
        Returns:
            bool: 撤销成功返回True
        """
        try:
            permission = self.db.query(ShardPermission).filter(
                and_(
                    ShardPermission.shard_id == shard_id,
                    ShardPermission.user_id == user_id,
                    ShardPermission.is_active == True
                )
            ).first()
            
            if permission:
                permission.is_active = False
                permission.updated_at = datetime.now()
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error revoking permission: {e}")
            raise DatabaseError(f"撤销权限失败: {str(e)}")
    
    def check_permission(self, shard_id: int, user_id: int, permission_type: str) -> bool:
        """
        检查用户是否有指定权限
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            permission_type: 权限类型
            
        Returns:
            bool: 有权限返回True
        """
        try:
            # 检查是否是所有者
            shard = self.db.query(DataShard).filter(DataShard.id == shard_id).first()
            if shard and shard.owner_id == user_id:
                return True
            
            # 检查权限表
            permission = self.db.query(ShardPermission).filter(
                and_(
                    ShardPermission.shard_id == shard_id,
                    ShardPermission.user_id == user_id,
                    ShardPermission.is_active == True,
                    or_(
                        ShardPermission.valid_until.is_(None),
                        ShardPermission.valid_until > datetime.now()
                    )
                )
            ).first()
            
            if permission:
                permission_field = f"can_{permission_type}"
                return getattr(permission, permission_field, False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

class AccessLogDao:
    """访问日志数据访问对象"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_access_log(self, log_data: dict) -> AccessLog:
        """
        创建访问日志
        
        Args:
            log_data: 日志数据
            
        Returns:
            AccessLog: 日志对象
        """
        try:
            log = AccessLog(**log_data)
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating access log: {e}")
            raise DatabaseError(f"创建访问日志失败: {str(e)}")
    
    def get_access_logs(self, shard_id: Optional[int] = None, user_id: Optional[int] = None,
                       page: int = 1, page_size: int = 20) -> Tuple[List[AccessLog], int, int, int]:
        """
        获取访问日志
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[AccessLog], int, int, int]: (日志列表, 总数, 页码, 每页大小)
        """
        try:
            query = self.db.query(AccessLog)
            
            if shard_id:
                query = query.filter(AccessLog.shard_id == shard_id)
            
            if user_id:
                query = query.filter(AccessLog.user_id == user_id)
            
            query = query.order_by(desc(AccessLog.created_at))
            
            return PageUtil.paginate(query, page, page_size)
            
        except Exception as e:
            logger.error(f"Error getting access logs: {e}")
            raise DatabaseError(f"获取访问日志失败: {str(e)}")
