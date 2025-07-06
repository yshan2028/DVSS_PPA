"""
加密服务
处理秘密共享和数据加密
"""

import json
import hashlib
from typing import List, Dict, Any
from secretsharing import SecretSharer
from sqlalchemy.orm import Session
from module_dvss.dao.order_dao import OrderDAO
from module_dvss.dao.shard_dao import ShardDAO
from module_dvss.entity.encrypted_order import EncryptedOrder
from module_dvss.entity.shard_info import ShardInfo

class EncryptionService:
    def __init__(self, db: Session):
        self.db = db
        self.order_dao = OrderDAO(db)
        self.shard_dao = ShardDAO(db)
    
    def create_shares(self, data: Dict[str, Any], k: int, n: int) -> List[str]:
        """创建秘密分片"""
        # 将数据转换为JSON字符串
        secret = json.dumps(data, ensure_ascii=False)
        
        # 使用秘密共享算法分片
        shares = SecretSharer.split_secret(secret, k, n)
        
        return shares
    
    def reconstruct_secret(self, shares: List[str]) -> Dict[str, Any]:
        """重构秘密"""
        # 恢复秘密
        secret = SecretSharer.recover_secret(shares)
        
        # 解析JSON
        return json.loads(secret)
    
    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """计算数据哈希值"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    async def encrypt_order(self, order_id: int, k: int, n: int) -> Dict[str, Any]:
        """加密订单"""
        # 获取原始订单
        order = self.order_dao.get_by_id(order_id)
        if not order:
            raise ValueError("订单不存在")
        
        # 构建订单数据
        order_data = {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "name": order.name,
            "phone": order.phone,
            "email": order.email,
            "address": order.address,
            "payment_info": order.payment_info,
            "item_list": order.item_list,
            "total_amount": str(order.total_amount) if order.total_amount else None
        }
        
        # 创建分片
        shares = self.create_shares(order_data, k, n)
        
        # 计算数据哈希
        data_hash = self.calculate_data_hash(order_data)
        
        # 保存加密订单记录
        encrypted_order = EncryptedOrder(
            original_order_id=order.id,
            order_id=order.order_id,
            encrypted_data=json.dumps(order_data),
            encryption_algorithm="secretsharing",
            k_value=k,
            n_value=n,
            data_hash=data_hash,
            status="encrypted"
        )
        
        encrypted_order = self.order_dao.create_encrypted_order(encrypted_order)
        
        # 保存分片信息
        shard_hashes = []
        for i, share in enumerate(shares):
            shard_hash = hashlib.sha256(share.encode('utf-8')).hexdigest()
            shard_hashes.append(shard_hash)
            
            shard_info = ShardInfo(
                encrypted_order_id=encrypted_order.id,
                shard_id=f"{order.order_id}_shard_{i}",
                shard_index=i,
                shard_data=share,
                checksum=shard_hash,
                status="active"
            )
            
            self.shard_dao.create_shard(shard_info)
        
        return {
            "encrypted_order_id": encrypted_order.id,
            "k_value": k,
            "n_value": n,
            "data_hash": data_hash,
            "shard_hashes": shard_hashes
        }
    
    async def decrypt_order(self, encrypted_order_id: int) -> Dict[str, Any]:
        """解密订单"""
        # 获取加密订单
        encrypted_order = self.order_dao.get_encrypted_by_id(encrypted_order_id)
        if not encrypted_order:
            raise ValueError("加密订单不存在")
        
        # 获取分片
        shards = self.shard_dao.get_by_encrypted_order_id(encrypted_order_id)
        if len(shards) < encrypted_order.k_value:
            raise ValueError("可用分片数量不足")
        
        # 取前k个分片进行重构
        share_data = [shard.shard_data for shard in shards[:encrypted_order.k_value]]
        
        # 重构数据
        reconstructed_data = self.reconstruct_secret(share_data)
        
        # 验证数据完整性
        reconstructed_hash = self.calculate_data_hash(reconstructed_data)
        if reconstructed_hash != encrypted_order.data_hash:
            raise ValueError("数据完整性验证失败")
        
        return reconstructed_data
