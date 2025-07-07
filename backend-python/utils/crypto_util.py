"""
密码学工具类
"""

import base64
import hashlib
import json
import os
import secrets

from typing import Any, Dict, List, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoUtil:
    """密码学工具类"""

    @staticmethod
    def generate_random_key(length: int = 32) -> str:
        """生成随机密钥"""
        return base64.b64encode(os.urandom(length)).decode('utf-8')

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """生成随机盐值"""
        return base64.b64encode(os.urandom(length)).decode('utf-8')

    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """哈希密码"""
        if salt is None:
            salt = CryptoUtil.generate_salt()

        # 使用PBKDF2进行密码哈希
        password_bytes = password.encode('utf-8')
        salt_bytes = base64.b64decode(salt.encode('utf-8'))

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )

        hashed = kdf.derive(password_bytes)
        hashed_b64 = base64.b64encode(hashed).decode('utf-8')

        return hashed_b64, salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        try:
            new_hash, _ = CryptoUtil.hash_password(password, salt)
            return new_hash == hashed_password
        except Exception:
            return False

    @staticmethod
    def calculate_hash(data: str, algorithm: str = 'sha256') -> str:
        """计算数据哈希值"""
        data_bytes = data.encode('utf-8')

        if algorithm.lower() == 'sha256':
            return hashlib.sha256(data_bytes).hexdigest()
        elif algorithm.lower() == 'sha512':
            return hashlib.sha512(data_bytes).hexdigest()
        elif algorithm.lower() == 'md5':
            return hashlib.md5(data_bytes).hexdigest()
        else:
            raise ValueError(f'不支持的哈希算法: {algorithm}')

    @staticmethod
    def encrypt_fernet(data: str, key: str = None) -> Tuple[str, str]:
        """使用Fernet对称加密"""
        if key is None:
            key = Fernet.generate_key()
        else:
            key = key.encode('utf-8')

        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))

        return base64.b64encode(encrypted_data).decode('utf-8'), key.decode('utf-8')

    @staticmethod
    def decrypt_fernet(encrypted_data: str, key: str) -> str:
        """使用Fernet对称解密"""
        fernet = Fernet(key.encode('utf-8'))
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')

    @staticmethod
    def generate_rsa_keypair(key_size: int = 2048) -> Tuple[str, str]:
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return base64.b64encode(private_pem).decode('utf-8'), base64.b64encode(public_pem).decode('utf-8')

    @staticmethod
    def rsa_encrypt(data: str, public_key_b64: str) -> str:
        """RSA加密"""
        public_key_bytes = base64.b64decode(public_key_b64.encode('utf-8'))
        public_key = serialization.load_pem_public_key(public_key_bytes)

        encrypted = public_key.encrypt(
            data.encode('utf-8'),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )

        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def rsa_decrypt(encrypted_data: str, private_key_b64: str) -> str:
        """RSA解密"""
        private_key_bytes = base64.b64decode(private_key_b64.encode('utf-8'))
        private_key = serialization.load_pem_private_key(private_key_bytes, password=None)

        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )

        return decrypted.decode('utf-8')


class SecretSharingUtil:
    """秘密分享工具类（简化版实现）"""

    def __init__(self):
        self.prime = 2**127 - 1  # 梅森素数

    def split_secret(self, secret: str, k: int, n: int) -> List[str]:
        """
        将秘密分割为n个分片，需要k个分片才能重构

        Args:
            secret: 要分割的秘密
            k: 阈值（最少需要的分片数）
            n: 总分片数

        Returns:
            分片列表
        """
        if k > n:
            raise ValueError('阈值不能大于总分片数')

        # 将秘密转换为整数
        secret_bytes = secret.encode('utf-8')
        secret_int = int.from_bytes(secret_bytes, byteorder='big')

        # 生成随机系数
        coefficients = [secret_int]
        for i in range(k - 1):
            coefficients.append(secrets.randbelow(self.prime))

        # 计算分片
        shares = []
        for x in range(1, n + 1):
            y = self._evaluate_polynomial(coefficients, x)
            share_data = {'x': x, 'y': y, 'k': k, 'n': n}
            share_json = json.dumps(share_data)
            share_b64 = base64.b64encode(share_json.encode('utf-8')).decode('utf-8')
            shares.append(share_b64)

        return shares

    def reconstruct_secret(self, shares: List[str]) -> str:
        """
        从分片重构秘密

        Args:
            shares: 分片列表

        Returns:
            重构的秘密
        """
        if len(shares) < 2:
            raise ValueError('至少需要2个分片')

        # 解析分片
        points = []
        k = None

        for share in shares:
            share_json = base64.b64decode(share.encode('utf-8')).decode('utf-8')
            share_data = json.loads(share_json)

            if k is None:
                k = share_data['k']
            elif k != share_data['k']:
                raise ValueError('分片的k值不一致')

            points.append((share_data['x'], share_data['y']))

        if len(points) < k:
            raise ValueError(f'分片数量不足，需要至少{k}个分片')

        # 使用拉格朗日插值重构秘密
        secret_int = self._lagrange_interpolation(points[:k], 0)

        # 将整数转换回字符串
        try:
            # 计算需要的字节数
            byte_length = (secret_int.bit_length() + 7) // 8
            secret_bytes = secret_int.to_bytes(byte_length, byteorder='big')
            return secret_bytes.decode('utf-8')
        except Exception:
            raise ValueError('无法重构秘密，分片可能已损坏')

    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """计算多项式在x处的值"""
        result = 0
        for i, coeff in enumerate(coefficients):
            result = (result + coeff * pow(x, i, self.prime)) % self.prime
        return result

    def _lagrange_interpolation(self, points: List[Tuple[int, int]], x: int) -> int:
        """拉格朗日插值"""
        result = 0

        for i, (xi, yi) in enumerate(points):
            # 计算拉格朗日基函数
            li = 1
            for j, (xj, _) in enumerate(points):
                if i != j:
                    # 计算 (x - xj) / (xi - xj)
                    numerator = (x - xj) % self.prime
                    denominator = (xi - xj) % self.prime

                    # 计算模逆
                    denominator_inv = self._mod_inverse(denominator, self.prime)
                    li = (li * numerator * denominator_inv) % self.prime

            result = (result + yi * li) % self.prime

        return result

    def _mod_inverse(self, a: int, m: int) -> int:
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

    def verify_share(self, share: str) -> bool:
        """验证分片格式是否正确"""
        try:
            share_json = base64.b64decode(share.encode('utf-8')).decode('utf-8')
            share_data = json.loads(share_json)

            required_fields = ['x', 'y', 'k', 'n']
            return all(field in share_data for field in required_fields)
        except Exception:
            return False

    def get_share_info(self, share: str) -> Dict[str, Any]:
        """获取分片信息"""
        try:
            share_json = base64.b64decode(share.encode('utf-8')).decode('utf-8')
            share_data = json.loads(share_json)

            return {
                'index': share_data['x'],
                'threshold': share_data['k'],
                'total_shares': share_data['n'],
                'is_valid': True,
            }
        except Exception:
            return {'is_valid': False, 'error': '分片格式无效'}


class HashUtil:
    """哈希工具类"""

    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """计算文件哈希值"""
        hash_func = getattr(hashlib, algorithm.lower())()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    @staticmethod
    def calculate_data_hash(data: bytes, algorithm: str = 'sha256') -> str:
        """计算数据哈希值"""
        hash_func = getattr(hashlib, algorithm.lower())()
        hash_func.update(data)
        return hash_func.hexdigest()

    @staticmethod
    def verify_hash(data: bytes, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """验证哈希值"""
        actual_hash = HashUtil.calculate_data_hash(data, algorithm)
        return actual_hash.lower() == expected_hash.lower()


class EncryptionKeyManager:
    """加密密钥管理器"""

    def __init__(self):
        self.keys = {}

    def generate_key(self, key_id: str, algorithm: str = 'fernet') -> str:
        """生成并存储密钥"""
        if algorithm.lower() == 'fernet':
            key = Fernet.generate_key().decode('utf-8')
        elif algorithm.lower() == 'aes':
            key = CryptoUtil.generate_random_key(32)
        else:
            raise ValueError(f'不支持的算法: {algorithm}')

        self.keys[key_id] = {
            'key': key,
            'algorithm': algorithm,
            'created_at': CryptoUtil.calculate_hash(str(secrets.randbelow(2**32))),
        }

        return key

    def get_key(self, key_id: str) -> str:
        """获取密钥"""
        if key_id not in self.keys:
            raise ValueError(f'密钥不存在: {key_id}')
        return self.keys[key_id]['key']

    def rotate_key(self, key_id: str) -> str:
        """轮换密钥"""
        if key_id not in self.keys:
            raise ValueError(f'密钥不存在: {key_id}')

        algorithm = self.keys[key_id]['algorithm']
        return self.generate_key(key_id, algorithm)

    def delete_key(self, key_id: str) -> bool:
        """删除密钥"""
        if key_id in self.keys:
            del self.keys[key_id]
            return True
        return False
