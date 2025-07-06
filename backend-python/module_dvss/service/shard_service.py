"""
数据分片服务层 (Service)
处理分片相关的业务逻辑
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import requests
import base64

from module_dvss.dao.shard_dao import ShardDao, ShardPermissionDao, AccessLogDao
from module_dvss.entity.do.shard_do import DataShard, ShardPermission, AccessLog
from module_dvss.entity.vo.shard_vo import (
    ShardCreateRequest, ShardUploadRequest, ShardUpdateRequest,
    ShardReconstructRequest, ShardPermissionRequest, ShardDetailResponse,
    ShardBaseResponse, ShardListResponse, ShardStatsResponse,
    ShardReconstructResponse, AccessLogResponse, ShardIntegrityCheckResponse
)
from exceptions.custom_exception import (
    NotFoundError, ConflictError, BusinessError, AuthorizationError,
    ValidationError, ShardError, ReconstructionError, ZKPError
)
from utils.log_util import LogUtil, audit_logger
from core.config import settings

logger = LogUtil.get_logger("shard_service")

class ShardService:
    """数据分片服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.shard_dao = ShardDao(db)
        self.permission_dao = ShardPermissionDao(db)
        self.access_log_dao = AccessLogDao(db)
    
    def create_shard(self, shard_request: ShardCreateRequest, owner_id: int) -> ShardDetailResponse:
        """
        创建数据分片
        
        Args:
            shard_request: 分片创建请求
            owner_id: 所有者ID
            
        Returns:
            ShardDetailResponse: 分片详细信息
            
        Raises:
            ValidationError: 数据验证失败
            ConflictError: 分片已存在
        """
        try:
            # 准备分片数据
            shard_data = shard_request.dict()
            shard_data['owner_id'] = owner_id
            shard_data['status'] = 'active'
            shard_data['version'] = 1
            shard_data['access_count'] = 0
            
            # 生成唯一的分片ID (如果没有提供)
            if 'shard_id' not in shard_data or not shard_data['shard_id']:
                shard_data['shard_id'] = self._generate_shard_id(
                    shard_request.original_file_hash, 
                    owner_id
                )
            
            # 创建分片
            shard = self.shard_dao.create_shard(shard_data)
            
            # 记录审计日志
            audit_logger.log_data_access("CREATE_SHARD", owner_id, shard.shard_id, "success", {
                "file_name": shard.original_file_name,
                "total_shards": shard.total_shards,
                "threshold": shard.threshold
            })
            
            logger.info(f"Shard created successfully: {shard.shard_id}")
            
            return ShardDetailResponse.from_orm(shard)
            
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error creating shard: {e}")
            raise BusinessError(f"创建分片失败: {str(e)}")
    
    def upload_shard_data(self, upload_request: ShardUploadRequest, user_id: int) -> bool:
        """
        上传分片数据
        
        Args:
            upload_request: 分片上传请求
            user_id: 用户ID
            
        Returns:
            bool: 上传成功返回True
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 权限不足
            ShardError: 分片操作失败
        """
        try:
            # 获取分片信息
            shard = self.shard_dao.get_shard_by_shard_id(upload_request.shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 权限检查
            if not self._check_shard_permission(shard.id, user_id, 'write'):
                raise AuthorizationError("权限不足")
            
            # 验证分片哈希
            decoded_data = base64.b64decode(upload_request.shard_data)
            calculated_hash = hashlib.sha256(decoded_data).hexdigest()
            
            if calculated_hash != upload_request.shard_hash:
                raise ValidationError("分片数据哈希验证失败")
            
            # 更新分片信息
            update_data = {
                'shard_hash': upload_request.shard_hash,
                'shard_size': upload_request.shard_size,
                'storage_node': upload_request.storage_node,
                'zkp_proof': upload_request.zkp_proof,
                'status': 'active'
            }
            
            # 如果有ZKP证明，验证它
            if upload_request.zkp_proof:
                if not self._verify_zkp_proof(upload_request.zkp_proof, decoded_data):
                    raise ZKPError("零知识证明验证失败")
            
            self.shard_dao.update_shard(shard.id, update_data)
            
            # 记录访问日志
            self._log_access(shard.id, user_id, "UPLOAD_DATA", "success", {
                "shard_size": upload_request.shard_size,
                "storage_node": upload_request.storage_node
            })
            
            logger.info(f"Shard data uploaded successfully: {shard.shard_id}")
            
            return True
            
        except (NotFoundError, AuthorizationError, ValidationError, ZKPError):
            raise
        except Exception as e:
            logger.error(f"Error uploading shard data: {e}")
            raise ShardError(f"上传分片数据失败: {str(e)}")
    
    def get_shard_by_id(self, shard_id: str, user_id: int) -> ShardDetailResponse:
        """
        根据分片ID获取分片信息
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            
        Returns:
            ShardDetailResponse: 分片详细信息
            
        Raises:
            NotFoundError: 分片不存在
            AuthorizationError: 权限不足
        """
        try:
            shard = self.shard_dao.get_shard_by_shard_id(shard_id)
            if not shard:
                raise NotFoundError("分片不存在")
            
            # 权限检查
            if not self._check_shard_permission(shard.id, user_id, 'read'):
                raise AuthorizationError("权限不足")
            
            # 更新访问时间和计数
            self.shard_dao.update_access_time(shard.id)
            
            # 记录访问日志
            self._log_access(shard.id, user_id, "GET_SHARD", "success")
            
            return ShardDetailResponse.from_orm(shard)
            
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Error getting shard {shard_id}: {e}")
            raise BusinessError(f"获取分片失败: {str(e)}")
    
    def list_shards(self, page: int = 1, page_size: int = 20, 
                   filters: Optional[Dict[str, Any]] = None, 
                   user_id: int = None) -> ShardListResponse:
        """
        获取分片列表
        
        Args:
            page: 页码
            page_size: 每页大小
            filters: 过滤条件
            user_id: 用户ID
            
        Returns:
            ShardListResponse: 分片列表响应
        """
        try:
            # 获取分片列表 (只返回用户有权限的分片)
            shards, total, page, page_size = self.shard_dao.list_shards(
                page, page_size, filters, user_id
            )
            
            # 转换为响应对象
            shard_responses = [ShardBaseResponse.from_orm(shard) for shard in shards]
            
            return ShardListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=shard_responses
            )
            
        except Exception as e:
            logger.error(f"Error listing shards: {e}")
            raise BusinessError(f"获取分片列表失败: {str(e)}")
    
    def _check_shard_permission(self, shard_id: int, user_id: int, permission_type: str) -> bool:
        """
        检查分片权限
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            permission_type: 权限类型
            
        Returns:
            bool: 有权限返回True
        """
        return self.permission_dao.check_permission(shard_id, user_id, permission_type)
    
    def _log_access(self, shard_id: int, user_id: int, action: str, result: str, 
                   details: Optional[Dict[str, Any]] = None):
        """
        记录访问日志
        
        Args:
            shard_id: 分片ID
            user_id: 用户ID
            action: 操作类型
            result: 操作结果
            details: 详细信息
        """
        try:
            log_data = {
                'shard_id': shard_id,
                'user_id': user_id,
                'action': action,
                'result': result,
                'request_data': details
            }
            self.access_log_dao.create_access_log(log_data)
        except Exception as e:
            logger.error(f"Error logging access: {e}")
    
    def _generate_shard_id(self, file_hash: str, owner_id: int) -> str:
        """
        生成分片ID
        
        Args:
            file_hash: 文件哈希
            owner_id: 所有者ID
            
        Returns:
            str: 分片ID
        """
        data = f"{file_hash}_{owner_id}_{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def _verify_zkp_proof(self, proof: str, data: bytes) -> bool:
        """
        验证零知识证明
        
        Args:
            proof: ZKP证明
            data: 数据
            
        Returns:
            bool: 验证结果
        """
        try:
            # 调用Go后端的ZKP验证服务
            response = requests.post(
                f"{settings.GO_BACKEND_URL}/api/zkp/verify",
                json={"proof": proof, "data": base64.b64encode(data).decode()},
                timeout=30
            )
            return response.status_code == 200 and response.json().get('valid', False)
        except Exception as e:
            logger.error(f"Error verifying ZKP proof: {e}")
            return False
from module_dvss.entity.vo.shard_vo import (
    ShardModel, 
    ShardPageQueryModel, 
    AddShardModel, 
    EditShardModel, 
    DeleteShardModel,
    PermissionModel
)
from exceptions.custom_exception import ServiceException


class CrudResponseModel:
    """CRUD操作响应模型"""
    def __init__(self, is_success: bool, message: str, result=None):
        self.is_success = is_success
        self.message = message
        self.result = result


class ShardService:
    """
    数据分片管理模块服务层
    """

    @classmethod
    def _generate_shard_hash(cls, file_path: str, size: int, owner_id: int) -> str:
        """
        生成分片哈希
        
        :param file_path: 文件路径
        :param size: 文件大小
        :param owner_id: 所有者ID
        :return: 分片哈希
        """
        content = f"{file_path}_{size}_{owner_id}_{datetime.now().timestamp()}"
        return hashlib.sha256(content.encode()).hexdigest()

    @classmethod
    def _generate_checksum(cls, file_path: str) -> str:
