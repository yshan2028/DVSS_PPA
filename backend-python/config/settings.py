from pydantic import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    APP_NAME: str = "DVSS-PPA Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/dvss_ppa"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "dvss_ppa"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".xlsx", ".xls"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/dvss-python.log"
    LOG_MAX_SIZE: int = 50 * 1024 * 1024  # 50MB
    LOG_BACKUP_COUNT: int = 5
    
    # Go后端配置
    GO_BACKEND_URL: str = "http://localhost:8001"
    GO_BACKEND_TIMEOUT: int = 30
    
    # Fabric配置
    FABRIC_NETWORK_PATH: str = "../fabric"
    FABRIC_CHANNEL_NAME: str = "mychannel"
    FABRIC_CHAINCODE_NAME: str = "dvss-chaincode"
    
    # 加密配置
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    KEY_DERIVATION_ITERATIONS: int = 100000
    
    # 分片配置
    DEFAULT_SHARD_SIZE: int = 1000
    MAX_SHARDS_PER_USER: int = 100
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # 监控配置
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # 缓存配置
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()


def get_settings() -> Settings:
    """获取设置实例"""
    return settings
    
    # Fabric配置
    FABRIC_GATEWAY_URL: str = "http://localhost:8001/api/v1/fabric"
    
    # 加密配置
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    SECRET_SHARING_THRESHOLD: int = 3
    SECRET_SHARING_TOTAL: int = 5
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局设置实例
settings = Settings()
