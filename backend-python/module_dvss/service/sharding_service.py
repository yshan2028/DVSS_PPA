"""
分片加密与重构服务
负责数据的分片加密、存储和重构
"""
import json
import hashlib
import secrets
import asyncio
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import secretsharing
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from core.models import Order, ShardIndex
import uuid

logger = logging.getLogger(__name__)

class ShardingService:
    """分片服务"""
    
    def __init__(self, mongodb_client, postgres_session, redis_client=None):
        self.mongodb_client = mongodb_client
        self.postgres_session = postgres_session
        self.redis_client = redis_client
        self.database = mongodb_client.dvss_shards
        self.collection = self.database.shards
        
    async def encrypt_and_shard_order(self, order_data: Dict[str, Any], 
                                    k: int, n: int = 5) -> List[Dict[str, Any]]:
        """
        加密并分片订单数据
        
        Args:
            order_data: 订单数据
            k: 重构阈值
            n: 总分片数
            
        Returns:
            分片信息列表
        """
        try:
            # 1. 序列化订单数据
            order_json = json.dumps(order_data, ensure_ascii=False, default=str)
            order_bytes = order_json.encode('utf-8')
            
            # 2. AES加密
            aes_key = get_random_bytes(32)  # 256-bit key
            cipher = AES.new(aes_key, AES.MODE_CBC)
            encrypted_data = cipher.encrypt(pad(order_bytes, AES.block_size))
            
            # 3. 计算数据哈希
            data_hash = hashlib.sha256(order_bytes).hexdigest()
            
            # 4. 使用Shamir秘密分享分片AES密钥
            key_hex = aes_key.hex()
            shares = secretsharing.SecretSharer.split_secret(key_hex, k, n)
            
            # 5. 创建分片
            shards = []
            order_id = order_data.get('id') or order_data.get('order_id')
            
            for i, share in enumerate(shares):
                shard_id = f"{order_id}_shard_{i+1}_{uuid.uuid4().hex[:8]}"
                
                # 分片数据结构
                shard_data = {
                    'shard_id': shard_id,
                    'order_id': order_id,
                    'shard_sequence': i + 1,
                    'total_shards': n,
                    'threshold_k': k,
                    'encrypted_data': encrypted_data.hex(),
                    'iv': cipher.iv.hex(),
                    'key_share': share,
                    'data_hash': data_hash,
                    'shard_hash': hashlib.sha256(f"{shard_id}{share}{encrypted_data.hex()}".encode()).hexdigest(),
                    'created_at': datetime.now(),
                    'metadata': {
                        'encryption_algorithm': 'AES-256-CBC',
                        'sharing_algorithm': 'Shamir',
                        'data_size': len(order_bytes),
                        'encrypted_size': len(encrypted_data)
                    }
                }
                
                shards.append(shard_data)
            
            # 6. 存储分片到MongoDB
            await self._store_shards_to_mongodb(shards)
            
            # 7. 更新PostgreSQL索引
            await self._update_shard_index(shards)
            
            logger.info(f"Successfully created {n} shards for order {order_id} with k={k}")
            
            return [self._create_shard_info(shard) for shard in shards]
            
        except Exception as e:
            logger.error(f"Error in encrypt_and_shard_order: {e}")
            raise
    
    async def _store_shards_to_mongodb(self, shards: List[Dict[str, Any]]):
        """将分片存储到MongoDB"""
        try:
            # 使用批量插入
            documents = []
            for shard in shards:
                doc = {
                    '_id': shard['shard_id'],
                    'order_id': shard['order_id'],
                    'shard_sequence': shard['shard_sequence'],
                    'total_shards': shard['total_shards'],
                    'threshold_k': shard['threshold_k'],
                    'encrypted_data': shard['encrypted_data'],
                    'iv': shard['iv'],
                    'key_share': shard['key_share'],
                    'data_hash': shard['data_hash'],
                    'shard_hash': shard['shard_hash'],
                    'created_at': shard['created_at'],
                    'metadata': shard['metadata'],
                    'status': 'active'
                }
                documents.append(doc)
            
            result = await self.collection.insert_many(documents)
            logger.info(f"Stored {len(result.inserted_ids)} shards to MongoDB")
            
        except Exception as e:
            logger.error(f"Error storing shards to MongoDB: {e}")
            raise
    
    async def _update_shard_index(self, shards: List[Dict[str, Any]]):
        """更新PostgreSQL分片索引"""
        try:
            async with self.postgres_session() as session:
                for shard in shards:
                    shard_index = ShardIndex(
                        shard_id=shard['shard_id'],
                        order_id=shard['order_id'],
                        shard_sequence=shard['shard_sequence'],
                        total_shards=shard['total_shards'],
                        threshold_k=shard['threshold_k'],
                        node_ip='mongodb_cluster',  # 可以是实际的MongoDB节点IP
                        storage_path=f"dvss_shards.shards.{shard['shard_id']}",
                        checksum=shard['shard_hash'],
                        status='active'
                    )
                    session.add(shard_index)
                
                await session.commit()
                logger.info(f"Updated shard index for {len(shards)} shards")
                
        except Exception as e:
            logger.error(f"Error updating shard index: {e}")
            raise
    
    def _create_shard_info(self, shard: Dict[str, Any]) -> Dict[str, Any]:
        """创建分片信息摘要（不包含敏感数据）"""
        return {
            'shard_id': shard['shard_id'],
            'shard_sequence': shard['shard_sequence'],
            'total_shards': shard['total_shards'],
            'threshold_k': shard['threshold_k'],
            'shard_hash': shard['shard_hash'],
            'data_hash': shard['data_hash'],
            'created_at': shard['created_at'],
            'metadata': shard['metadata']
        }
    
    async def reconstruct_order_data(self, order_id: str, 
                                   available_shards: List[str] = None) -> Dict[str, Any]:
        """
        重构订单数据
        
        Args:
            order_id: 订单ID
            available_shards: 可用分片ID列表（可选）
            
        Returns:
            重构的订单数据
        """
        try:
            # 1. 获取分片信息
            if available_shards:
                # 使用指定的分片
                shards = await self._get_shards_by_ids(available_shards)
            else:
                # 获取订单的所有分片
                shards = await self._get_shards_by_order_id(order_id)
            
            if not shards:
                raise ValueError(f"No shards found for order {order_id}")
            
            # 2. 检查分片数量是否足够
            k = shards[0].get('threshold_k', 3)
            if len(shards) < k:
                raise ValueError(f"Insufficient shards: need {k}, got {len(shards)}")
            
            # 3. 验证分片完整性
            valid_shards = []
            for shard in shards:
                if await self._verify_shard_integrity(shard):
                    valid_shards.append(shard)
            
            if len(valid_shards) < k:
                raise ValueError(f"Insufficient valid shards: need {k}, got {len(valid_shards)}")
            
            # 4. 使用前k个有效分片重构密钥
            key_shares = [shard['key_share'] for shard in valid_shards[:k]]
            reconstructed_key_hex = secretsharing.SecretSharer.recover_secret(key_shares)
            reconstructed_key = bytes.fromhex(reconstructed_key_hex)
            
            # 5. 解密数据
            encrypted_data = bytes.fromhex(valid_shards[0]['encrypted_data'])
            iv = bytes.fromhex(valid_shards[0]['iv'])
            
            cipher = AES.new(reconstructed_key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            
            # 6. 反序列化数据
            order_json = decrypted_data.decode('utf-8')
            order_data = json.loads(order_json)
            
            # 7. 验证数据完整性
            expected_hash = valid_shards[0]['data_hash']
            actual_hash = hashlib.sha256(decrypted_data).hexdigest()
            
            if expected_hash != actual_hash:
                raise ValueError("Data integrity check failed")
            
            logger.info(f"Successfully reconstructed order {order_id} using {len(key_shares)} shards")
            
            return {
                'order_data': order_data,
                'reconstruction_info': {
                    'shards_used': len(key_shares),
                    'shards_available': len(valid_shards),
                    'threshold_k': k,
                    'integrity_verified': True,
                    'reconstructed_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error reconstructing order {order_id}: {e}")
            raise
    
    async def _get_shards_by_order_id(self, order_id: str) -> List[Dict[str, Any]]:
        """根据订单ID获取分片"""
        try:
            cursor = self.collection.find({
                'order_id': order_id,
                'status': 'active'
            }).sort('shard_sequence', 1)
            
            shards = await cursor.to_list(length=None)
            return shards
            
        except Exception as e:
            logger.error(f"Error getting shards for order {order_id}: {e}")
            return []
    
    async def _get_shards_by_ids(self, shard_ids: List[str]) -> List[Dict[str, Any]]:
        """根据分片ID列表获取分片"""
        try:
            cursor = self.collection.find({
                '_id': {'$in': shard_ids},
                'status': 'active'
            }).sort('shard_sequence', 1)
            
            shards = await cursor.to_list(length=None)
            return shards
            
        except Exception as e:
            logger.error(f"Error getting shards by IDs: {e}")
            return []
    
    async def _verify_shard_integrity(self, shard: Dict[str, Any]) -> bool:
        """验证分片完整性"""
        try:
            # 重新计算分片哈希
            shard_content = f"{shard['_id']}{shard['key_share']}{shard['encrypted_data']}"
            calculated_hash = hashlib.sha256(shard_content.encode()).hexdigest()
            
            return calculated_hash == shard['shard_hash']
            
        except Exception as e:
            logger.error(f"Error verifying shard integrity: {e}")
            return False
    
    async def delete_shards(self, order_id: str, soft_delete: bool = True) -> bool:
        """
        删除订单分片
        
        Args:
            order_id: 订单ID
            soft_delete: 是否软删除
            
        Returns:
            删除是否成功
        """
        try:
            if soft_delete:
                # 软删除：更新状态
                mongo_result = await self.collection.update_many(
                    {'order_id': order_id},
                    {'$set': {'status': 'deleted', 'deleted_at': datetime.now()}}
                )
                
                # 更新PostgreSQL索引
                async with self.postgres_session() as session:
                    await session.execute(
                        update(ShardIndex)
                        .where(ShardIndex.order_id == order_id)
                        .values(status='deleted')
                    )
                    await session.commit()
            else:
                # 硬删除：物理删除
                mongo_result = await self.collection.delete_many({'order_id': order_id})
                
                # 删除PostgreSQL索引
                async with self.postgres_session() as session:
                    await session.execute(
                        ShardIndex.__table__.delete().where(ShardIndex.order_id == order_id)
                    )
                    await session.commit()
            
            logger.info(f"{'Soft' if soft_delete else 'Hard'} deleted {mongo_result.modified_count if soft_delete else mongo_result.deleted_count} shards for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting shards for order {order_id}: {e}")
            return False
    
    async def get_shard_statistics(self) -> Dict[str, Any]:
        """获取分片统计信息"""
        try:
            # MongoDB统计
            total_shards = await self.collection.count_documents({})
            active_shards = await self.collection.count_documents({'status': 'active'})
            deleted_shards = await self.collection.count_documents({'status': 'deleted'})
            
            # 按订单分组统计
            pipeline = [
                {'$match': {'status': 'active'}},
                {'$group': {
                    '_id': '$order_id',
                    'shard_count': {'$sum': 1},
                    'threshold_k': {'$first': '$threshold_k'},
                    'total_shards': {'$first': '$total_shards'}
                }},
                {'$group': {
                    '_id': None,
                    'total_orders': {'$sum': 1},
                    'avg_shards_per_order': {'$avg': '$shard_count'},
                    'avg_threshold_k': {'$avg': '$threshold_k'}
                }}
            ]
            
            agg_result = await self.collection.aggregate(pipeline).to_list(length=1)
            order_stats = agg_result[0] if agg_result else {}
            
            # 存储统计
            storage_stats = await self.collection.aggregate([
                {'$match': {'status': 'active'}},
                {'$group': {
                    '_id': None,
                    'total_encrypted_size': {'$sum': '$metadata.encrypted_size'},
                    'total_original_size': {'$sum': '$metadata.data_size'}
                }}
            ]).to_list(length=1)
            
            storage_info = storage_stats[0] if storage_stats else {}
            
            return {
                'shard_counts': {
                    'total': total_shards,
                    'active': active_shards,
                    'deleted': deleted_shards
                },
                'order_statistics': {
                    'total_orders_with_shards': order_stats.get('total_orders', 0),
                    'avg_shards_per_order': round(order_stats.get('avg_shards_per_order', 0), 2),
                    'avg_threshold_k': round(order_stats.get('avg_threshold_k', 0), 2)
                },
                'storage_statistics': {
                    'total_encrypted_size_bytes': storage_info.get('total_encrypted_size', 0),
                    'total_original_size_bytes': storage_info.get('total_original_size', 0),
                    'compression_ratio': round(
                        storage_info.get('total_encrypted_size', 1) / max(storage_info.get('total_original_size', 1), 1),
                        3
                    )
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting shard statistics: {e}")
            return {'error': str(e)}
    
    async def cleanup_expired_shards(self, days_old: int = 30) -> int:
        """
        清理过期的已删除分片
        
        Args:
            days_old: 删除多少天前的分片
            
        Returns:
            清理的分片数量
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # 删除MongoDB中的过期分片
            result = await self.collection.delete_many({
                'status': 'deleted',
                'deleted_at': {'$lt': cutoff_date}
            })
            
            # 删除PostgreSQL索引中的过期记录
            async with self.postgres_session() as session:
                deleted_shards = await session.execute(
                    select(ShardIndex.shard_id)
                    .where(ShardIndex.status == 'deleted')
                    .where(ShardIndex.created_at < cutoff_date)
                )
                
                shard_ids = [row.shard_id for row in deleted_shards]
                
                if shard_ids:
                    await session.execute(
                        ShardIndex.__table__.delete()
                        .where(ShardIndex.shard_id.in_(shard_ids))
                    )
                    await session.commit()
            
            logger.info(f"Cleaned up {result.deleted_count} expired shards")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired shards: {e}")
            return 0
