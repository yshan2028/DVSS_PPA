"""
加密服务
处理秘密共享和数据加密
"""

import base64
import hashlib
import json
import random

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from module_dvss.dao.order_dao import OrderDAO
from module_dvss.dao.shard_dao import ShardDAO
from module_dvss.entity.encrypted_order import EncryptedOrder
from module_dvss.entity.shard_info import ShardInfo


class SimpleSecretSharing:
    """简单的秘密共享实现 (Shamir's Secret Sharing)"""

    @staticmethod
    def _generate_prime() -> int:
        """生成一个大质数"""
        return 2**31 - 1  # 使用梅森质数

    @staticmethod
    def _mod_inverse(a: int, m: int) -> int:
        """计算模逆"""

        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y

        gcd, x, _ = extended_gcd(a % m, m)
        if gcd != 1:
            raise ValueError('模逆不存在')
        return (x % m + m) % m

    @staticmethod
    def _evaluate_polynomial(coefficients: List[int], x: int, prime: int) -> int:
        """计算多项式在x处的值"""
        result = 0
        for i, coeff in enumerate(coefficients):
            result = (result + coeff * pow(x, i, prime)) % prime
        return result

    @classmethod
    def split_secret(cls, secret: str, k: int, n: int) -> List[str]:
        """分割秘密"""
        prime = cls._generate_prime()

        # 将秘密转换为整数
        secret_bytes = secret.encode('utf-8')
        secret_int = int.from_bytes(secret_bytes, byteorder='big')

        if secret_int >= prime:
            raise ValueError('秘密太大，无法处理')

        # 生成随机系数
        coefficients = [secret_int] + [random.randint(0, prime - 1) for _ in range(k - 1)]

        # 生成分片
        shares = []
        for i in range(1, n + 1):
            y = cls._evaluate_polynomial(coefficients, i, prime)
            share_data = {'x': i, 'y': y, 'prime': prime, 'k': k}
            shares.append(base64.b64encode(json.dumps(share_data).encode()).decode())

        return shares

    @classmethod
    def recover_secret(cls, shares: List[str]) -> str:
        """恢复秘密"""
        if not shares:
            raise ValueError('分片列表为空')

        # 解析分片
        parsed_shares = []
        for share in shares:
            share_data = json.loads(base64.b64decode(share).decode())
            parsed_shares.append((share_data['x'], share_data['y']))

        # 获取参数
        first_share_data = json.loads(base64.b64decode(shares[0]).decode())
        prime = first_share_data['prime']
        k = first_share_data['k']

        if len(parsed_shares) < k:
            raise ValueError(f'分片数量不足，需要至少{k}个分片')

        # 使用拉格朗日插值恢复秘密
        secret = 0
        for i in range(k):
            xi, yi = parsed_shares[i]
            li = 1

            for j in range(k):
                if i != j:
                    xj, _ = parsed_shares[j]
                    numerator = (0 - xj) % prime
                    denominator = (xi - xj) % prime
                    li = (li * numerator * cls._mod_inverse(denominator, prime)) % prime

            secret = (secret + yi * li) % prime

        # 将整数转换回字符串
        secret_bytes = secret.to_bytes((secret.bit_length() + 7) // 8, byteorder='big')
        return secret_bytes.decode('utf-8')


class EncryptionService:
    def __init__(self, db: Session):
        self.db = db
        self.order_dao = OrderDAO(db)
        self.shard_dao = ShardDAO(db)

    def create_shares(self, data: Dict[str, Any], k: int, n: int) -> List[str]:
        """创建秘密分片"""
        # 将数据转换为JSON字符串
        secret = json.dumps(data, ensure_ascii=False)

        # 使用简单秘密共享算法分片
        shares = SimpleSecretSharing.split_secret(secret, k, n)

        return shares

    def reconstruct_secret(self, shares: List[str]) -> Dict[str, Any]:
        """重构秘密"""
        # 恢复秘密
        secret = SimpleSecretSharing.recover_secret(shares)

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
            raise ValueError('订单不存在')

        # 构建订单数据
        order_data = {
            'order_id': order.order_id,
            'user_id': order.user_id,
            'name': order.name,
            'phone': order.phone,
            'email': order.email,
            'address': order.address,
            'payment_info': order.payment_info,
            'item_list': order.item_list,
            'total_amount': str(order.total_amount) if order.total_amount else None,
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
            encryption_algorithm='secretsharing',
            k_value=k,
            n_value=n,
            data_hash=data_hash,
            status='encrypted',
        )

        encrypted_order = self.order_dao.create_encrypted_order(encrypted_order)

        # 保存分片信息
        shard_hashes = []
        for i, share in enumerate(shares):
            shard_hash = hashlib.sha256(share.encode('utf-8')).hexdigest()
            shard_hashes.append(shard_hash)

            shard_info = ShardInfo(
                encrypted_order_id=encrypted_order.id,
                shard_id=f'{order.order_id}_shard_{i}',
                shard_index=i,
                shard_data=share,
                checksum=shard_hash,
                status='active',
            )

            self.shard_dao.create_shard(shard_info)

        return {
            'encrypted_order_id': encrypted_order.id,
            'k_value': k,
            'n_value': n,
            'data_hash': data_hash,
            'shard_hashes': shard_hashes,
        }

    async def decrypt_order(self, encrypted_order_id: int) -> Dict[str, Any]:
        """解密订单"""
        # 获取加密订单
        encrypted_order = self.order_dao.get_encrypted_by_id(encrypted_order_id)
        if not encrypted_order:
            raise ValueError('加密订单不存在')

        # 获取分片
        shards = self.shard_dao.get_by_encrypted_order_id(encrypted_order_id)
        if len(shards) < encrypted_order.k_value:
            raise ValueError('可用分片数量不足')

        # 取前k个分片进行重构
        share_data = [shard.shard_data for shard in shards[: encrypted_order.k_value]]

        # 重构数据
        reconstructed_data = self.reconstruct_secret(share_data)

        # 验证数据完整性
        reconstructed_hash = self.calculate_data_hash(reconstructed_data)
        if reconstructed_hash != encrypted_order.data_hash:
            raise ValueError('数据完整性验证失败')

        return reconstructed_data
