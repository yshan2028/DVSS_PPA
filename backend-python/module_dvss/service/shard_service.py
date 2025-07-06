"""
数据分片服务层
Service Layer - 处理分片相关的业务逻辑
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from module_dvss.dao.shard_dao import ShardDao
from module_dvss.dao.user_dao import UserDao
from module_dvss.schemas.shard_schema import (
    ShardCreateRequest, ShardUpdateRequest, ShardResponse,
    ShardListResponse, ShardStatsResponse, ShardDetailResponse
)
from module_dvss.schemas.common_schema import PageRequest, PageResponse
from module_dvss.entity.shard_info import ShardInfo
from exceptions.custom_exception import NotFoundError, ConflictError, ValidationError, AuthorizationError
from utils.log_util import LogUtil
from utils.crypto_util import CryptoUtil

logger = LogUtil.get_logger("shard_service")

class ShardService:
    """数据分片服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.shard_dao = ShardDao(db)
        self.user_dao = UserDao(db)
        self.crypto_util = CryptoUtil()
    
    async def create_shard(self, request: ShardCreateRequest, current_user_id: int) -> ShardResponse:
        """
        创建数据分片
        
        Args:
            request: 分片创建请求
            current_user_id: 当前用户ID
            
        Returns:
            ShardResponse: 分片响应数据
            
        Raises:
            ValidationError: 数据验证失败
            ConflictError: 分片已存在
        """
        try:
            logger.info(f"用户 {current_user_id} 开始创建分片")
            
            # 验证用户权限
            user = await self.user_dao.get_user_by_id(current_user_id)
            if not user:
                raise AuthorizationError("用户不存在")
            
            # 验证订单是否存在
            # TODO: 添加订单验证逻辑
            
            # 生成分片ID
            shard_id = self._generate_shard_id(request.order_id, request.shard_index)
            
            # 计算分片哈希值
            hash_value = self._calculate_shard_hash(request.data_content)
            
            # 创建分片数据
            shard_data = {
                "shard_id": shard_id,
                "order_id": request.order_id,
                "shard_index": request.shard_index,
                "total_shards": request.total_shards,
                "data_content": request.data_content,
                "encryption_algorithm": request.encryption_algorithm,
                "hash_value": hash_value,
                "size": len(request.data_content.encode('utf-8')) if request.data_content else 0,
                "status": "pending",
                "created_by": current_user_id,
                "created_at": datetime.utcnow()
            }
            
            # 创建分片
            shard = await self.shard_dao.create_shard(shard_data)
            
            logger.info(f"分片 {shard_id} 创建成功")
            
            return ShardResponse(
                id=shard.id,
                shard_id=shard.shard_id,
                order_id=shard.order_id,
                shard_index=shard.shard_index,
                total_shards=shard.total_shards,
                status=shard.status,
                encryption_algorithm=shard.encryption_algorithm,
                hash_value=shard.hash_value,
                size=shard.size,
                created_at=shard.created_at,
                updated_at=shard.updated_at
            )
            
        except Exception as e:
            logger.error(f"创建分片失败: {str(e)}")
            raise
    
    async def get_shard_by_id(self, shard_id: str, current_user_id: int) -> ShardDetailResponse:
        """
        根据ID获取分片详情
        
        Args:
            shard_id: 分片ID
            current_user_id: 当前用户ID
            
        Returns:
            ShardDetailResponse: 分片详情数据
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 无权限访问
        """
        try:
            # 获取分片信息
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 检查访问权限
            await self._check_shard_access_permission(shard, current_user_id)
            
            # 记录访问日志
            await self._log_shard_access(shard.id, current_user_id, "view")
            
            return ShardDetailResponse(
                id=shard.id,
                shard_id=shard.shard_id,
                order_id=shard.order_id,
                shard_index=shard.shard_index,
                total_shards=shard.total_shards,
                status=shard.status,
                encryption_algorithm=shard.encryption_algorithm,
                hash_value=shard.hash_value,
                size=shard.size,
                processing_node=shard.processing_node,
                error_message=shard.error_message,
                created_by=shard.created_by,
                created_at=shard.created_at,
                updated_at=shard.updated_at
            )
            
        except Exception as e:
            logger.error(f"获取分片详情失败: {str(e)}")
            raise
    
    async def get_shard_list(
        self, 
        page_request: PageRequest,
        order_id: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[int] = None,
        current_user_id: int = None
    ) -> ShardListResponse:
        """
        获取分片列表
        
        Args:
            page_request: 分页请求
            order_id: 订单ID筛选
            status: 状态筛选
            created_by: 创建者筛选
            current_user_id: 当前用户ID
            
        Returns:
            ShardListResponse: 分片列表响应
        """
        try:
            # 构建筛选条件
            filters = {}
            if order_id:
                filters['order_id'] = order_id
            if status:
                filters['status'] = status
            if created_by:
                filters['created_by'] = created_by
            
            # 获取分片列表
            shards, total = await self.shard_dao.get_shard_list(
                page=page_request.page,
                size=page_request.size,
                filters=filters
            )
            
            # 转换为响应格式
            shard_list = []
            for shard in shards:
                shard_list.append(ShardResponse(
                    id=shard.id,
                    shard_id=shard.shard_id,
                    order_id=shard.order_id,
                    shard_index=shard.shard_index,
                    total_shards=shard.total_shards,
                    status=shard.status,
                    encryption_algorithm=shard.encryption_algorithm,
                    hash_value=shard.hash_value,
                    size=shard.size,
                    created_at=shard.created_at,
                    updated_at=shard.updated_at
                ))
            
            return ShardListResponse(
                items=shard_list,
                total=total,
                page=page_request.page,
                size=page_request.size
            )
            
        except Exception as e:
            logger.error(f"获取分片列表失败: {str(e)}")
            raise
    
    async def update_shard(self, shard_id: str, request: ShardUpdateRequest, current_user_id: int) -> ShardResponse:
        """
        更新分片信息
        
        Args:
            shard_id: 分片ID
            request: 更新请求
            current_user_id: 当前用户ID
            
        Returns:
            ShardResponse: 更新后的分片数据
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 无权限修改
        """
        try:
            # 获取分片信息
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 检查修改权限
            await self._check_shard_modify_permission(shard, current_user_id)
            
            # 准备更新数据
            update_data = {}
            if request.status:
                update_data['status'] = request.status
            if request.processing_node:
                update_data['processing_node'] = request.processing_node
            if request.error_message is not None:
                update_data['error_message'] = request.error_message
            
            update_data['updated_at'] = datetime.utcnow()
            
            # 更新分片
            updated_shard = await self.shard_dao.update_shard(shard_id, update_data)
            
            # 记录操作日志
            await self._log_shard_access(shard.id, current_user_id, "update")
            
            logger.info(f"分片 {shard_id} 更新成功")
            
            return ShardResponse(
                id=updated_shard.id,
                shard_id=updated_shard.shard_id,
                order_id=updated_shard.order_id,
                shard_index=updated_shard.shard_index,
                total_shards=updated_shard.total_shards,
                status=updated_shard.status,
                encryption_algorithm=updated_shard.encryption_algorithm,
                hash_value=updated_shard.hash_value,
                size=updated_shard.size,
                created_at=updated_shard.created_at,
                updated_at=updated_shard.updated_at
            )
            
        except Exception as e:
            logger.error(f"更新分片失败: {str(e)}")
            raise
    
    async def delete_shard(self, shard_id: str, current_user_id: int) -> bool:
        """
        删除分片
        
        Args:
            shard_id: 分片ID
            current_user_id: 当前用户ID
            
        Returns:
            bool: 是否删除成功
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 无权限删除
        """
        try:
            # 获取分片信息
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 检查删除权限
            await self._check_shard_delete_permission(shard, current_user_id)
            
            # 检查分片状态
            if shard.status == "processing":
                raise ValidationError("处理中的分片不能删除")
            
            # 删除分片
            success = await self.shard_dao.delete_shard(shard_id)
            
            if success:
                # 记录操作日志
                await self._log_shard_access(shard.id, current_user_id, "delete")
                logger.info(f"分片 {shard_id} 删除成功")
            
            return success
            
        except Exception as e:
            logger.error(f"删除分片失败: {str(e)}")
            raise
    
    async def download_shard(self, shard_id: str, current_user_id: int) -> bytes:
        """
        下载分片数据
        
        Args:
            shard_id: 分片ID
            current_user_id: 当前用户ID
            
        Returns:
            bytes: 分片数据
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 无权限下载
        """
        try:
            # 获取分片信息
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 检查下载权限
            await self._check_shard_access_permission(shard, current_user_id)
            
            # 检查分片状态
            if shard.status != "completed":
                raise ValidationError("只有已完成的分片才能下载")
            
            # 获取分片数据
            shard_data = shard.data_content.encode('utf-8') if shard.data_content else b''
            
            # 记录下载日志
            await self._log_shard_access(shard.id, current_user_id, "download")
            
            logger.info(f"用户 {current_user_id} 下载分片 {shard_id}")
            
            return shard_data
            
        except Exception as e:
            logger.error(f"下载分片失败: {str(e)}")
            raise
    
    async def get_shard_stats(self, current_user_id: int) -> ShardStatsResponse:
        """
        获取分片统计信息
        
        Args:
            current_user_id: 当前用户ID
            
        Returns:
            ShardStatsResponse: 统计信息
        """
        try:
            stats = await self.shard_dao.get_shard_stats()
            
            return ShardStatsResponse(
                total_shards=stats.get('total_shards', 0),
                pending_shards=stats.get('pending_shards', 0),
                processing_shards=stats.get('processing_shards', 0),
                completed_shards=stats.get('completed_shards', 0),
                failed_shards=stats.get('failed_shards', 0),
                total_size=stats.get('total_size', 0)
            )
            
        except Exception as e:
            logger.error(f"获取分片统计失败: {str(e)}")
            raise
    
    async def validate_shard(self, shard_id: str, current_user_id: int) -> bool:
        """
        验证分片完整性
        
        Args:
            shard_id: 分片ID
            current_user_id: 当前用户ID
            
        Returns:
            bool: 验证结果
            
        Raises:
            NotFoundError: 分片不存在
        """
        try:
            # 获取分片信息
            shard = await self.shard_dao.get_shard_by_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 检查访问权限
            await self._check_shard_access_permission(shard, current_user_id)
            
            # 重新计算哈希值
            current_hash = self._calculate_shard_hash(shard.data_content)
            
            # 验证哈希值
            is_valid = current_hash == shard.hash_value
            
            # 记录验证日志
            await self._log_shard_access(shard.id, current_user_id, "validate")
            
            logger.info(f"分片 {shard_id} 验证结果: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"验证分片失败: {str(e)}")
            raise
    
    # 私有方法
    
    def _generate_shard_id(self, order_id: str, shard_index: int) -> str:
        """生成分片ID"""
        import uuid
        timestamp = int(datetime.utcnow().timestamp())
        return f"{order_id}_{shard_index}_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def _calculate_shard_hash(self, data_content: str) -> str:
        """计算分片哈希值"""
        if not data_content:
            return ""
        return self.crypto_util.calculate_hash(data_content.encode('utf-8'))
    
    async def _check_shard_access_permission(self, shard, user_id: int):
        """检查分片访问权限"""
        # TODO: 实现权限检查逻辑
        # 临时实现：只允许创建者或管理员访问
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthorizationError("用户不存在")
        
        if shard.created_by != user_id and user.role != 'admin':
            raise AuthorizationError("无权限访问该分片")
    
    async def _check_shard_modify_permission(self, shard, user_id: int):
        """检查分片修改权限"""
        # TODO: 实现权限检查逻辑
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthorizationError("用户不存在")
        
        if shard.created_by != user_id and user.role != 'admin':
            raise AuthorizationError("无权限修改该分片")
    
    async def _check_shard_delete_permission(self, shard, user_id: int):
        """检查分片删除权限"""
        # TODO: 实现权限检查逻辑
        user = await self.user_dao.get_user_by_id(user_id)
        if not user:
            raise AuthorizationError("用户不存在")
        
        if shard.created_by != user_id and user.role != 'admin':
            raise AuthorizationError("无权限删除该分片")
    
    async def _log_shard_access(self, shard_id: int, user_id: int, action: str):
        """记录分片访问日志"""
        try:
            # TODO: 实现访问日志记录
            logger.info(f"用户 {user_id} 对分片 {shard_id} 执行了 {action} 操作")
        except Exception as e:
            logger.error(f"记录分片访问日志失败: {str(e)}")
