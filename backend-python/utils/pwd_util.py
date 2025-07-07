"""
密码工具类
处理密码加密、验证等
"""

import base64
import hashlib
import secrets

from typing import Tuple

import bcrypt

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PwdUtil:
    """密码工具类"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        使用bcrypt对密码进行哈希

        Args:
            password: 明文密码

        Returns:
            str: 哈希后的密码
        """
        # 生成salt并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            hashed_password: 哈希后的密码

        Returns:
            bool: 验证结果
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度

        Returns:
            str: 随机密码
        """
        # 定义字符集
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def generate_salt() -> str:
        """
        生成随机盐值

        Returns:
            str: Base64编码的盐值
        """
        salt = secrets.token_bytes(32)
        return base64.b64encode(salt).decode('utf-8')

    @staticmethod
    def hash_with_salt(password: str, salt: str) -> str:
        """
        使用指定盐值对密码进行哈希

        Args:
            password: 明文密码
            salt: 盐值

        Returns:
            str: 哈希后的密码
        """
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_bytes, 100000)
        return base64.b64encode(password_hash).decode('utf-8')

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            Tuple[bool, str]: (是否符合要求, 错误信息)
        """
        if len(password) < 8:
            return False, '密码长度至少8个字符'

        if len(password) > 128:
            return False, '密码长度不能超过128个字符'

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if not has_upper:
            return False, '密码必须包含至少一个大写字母'

        if not has_lower:
            return False, '密码必须包含至少一个小写字母'

        if not has_digit:
            return False, '密码必须包含至少一个数字'

        if not has_special:
            return False, '密码必须包含至少一个特殊字符'

        return True, '密码强度符合要求'


class CryptoUtil:
    """加密工具类"""

    @staticmethod
    def generate_key() -> str:
        """
        生成加密密钥

        Returns:
            str: Base64编码的密钥
        """
        key = Fernet.generate_key()
        return base64.b64encode(key).decode('utf-8')

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        从密码派生加密密钥

        Args:
            password: 密码
            salt: 盐值

        Returns:
            Tuple[bytes, bytes]: (密钥, 盐值)
        """
        if salt is None:
            salt = secrets.token_bytes(32)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode('utf-8'))
        return key, salt

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """
        加密数据

        Args:
            data: 要加密的数据
            key: Base64编码的密钥

        Returns:
            str: Base64编码的加密数据
        """
        key_bytes = base64.b64decode(key.encode('utf-8'))
        f = Fernet(key_bytes)
        encrypted = f.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """
        解密数据

        Args:
            encrypted_data: Base64编码的加密数据
            key: Base64编码的密钥

        Returns:
            str: 解密后的数据
        """
        key_bytes = base64.b64decode(key.encode('utf-8'))
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        f = Fernet(key_bytes)
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')

    @staticmethod
    def generate_hash(data: str, algorithm: str = 'sha256') -> str:
        """
        生成数据哈希

        Args:
            data: 要哈希的数据
            algorithm: 哈希算法

        Returns:
            str: 十六进制哈希值
        """
        if algorithm == 'sha256':
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode('utf-8')).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        else:
            raise ValueError(f'不支持的哈希算法: {algorithm}')
