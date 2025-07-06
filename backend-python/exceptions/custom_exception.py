"""
自定义异常类
"""

from typing import Optional, Any, Dict

class DVSSException(Exception):
    """DVSS基础异常类"""
    
    def __init__(self, message: str, code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(DVSSException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)

class AuthorizationError(DVSSException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)

class ValidationError(DVSSException):
    """数据验证错误"""
    
    def __init__(self, message: str = "数据验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

class NotFoundError(DVSSException):
    """资源不存在错误"""
    
    def __init__(self, message: str = "资源不存在", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)

class ConflictError(DVSSException):
    """冲突错误"""
    
    def __init__(self, message: str = "资源冲突", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, details)

class BusinessError(DVSSException):
    """业务逻辑错误"""
    
    def __init__(self, message: str = "业务处理失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

class DatabaseError(DVSSException):
    """数据库错误"""
    
    def __init__(self, message: str = "数据库操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ExternalServiceError(DVSSException):
    """外部服务错误"""
    
    def __init__(self, message: str = "外部服务调用失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 502, details)

class RateLimitError(DVSSException):
    """限流错误"""
    
    def __init__(self, message: str = "请求频率过高", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 429, details)

class CryptoError(DVSSException):
    """加密/解密错误"""
    
    def __init__(self, message: str = "加密操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ShardError(DVSSException):
    """分片操作错误"""
    
    def __init__(self, message: str = "分片操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ReconstructionError(DVSSException):
    """重构错误"""
    
    def __init__(self, message: str = "数据重构失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ZKPError(DVSSException):
    """零知识证明错误"""
    
    def __init__(self, message: str = "零知识证明验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, details)

class FabricError(DVSSException):
    """Fabric区块链错误"""
    
    def __init__(self, message: str = "区块链操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class ConfigError(DVSSException):
    """配置错误"""
    
    def __init__(self, message: str = "配置错误", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)

class RedisError(DVSSException):
    """Redis错误"""
    
    def __init__(self, message: str = "Redis操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)
