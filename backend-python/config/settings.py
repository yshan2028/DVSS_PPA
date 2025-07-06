from pydantic import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用设置"""
    
    # 应用基本信息
    APP_NAME: str = "DVSS-PPA Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/dvss_ppa"
    DATABASE_ECHO: bool = False
    
    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "dvss_ppa"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/dvss-python.log"
    
    # Go后端配置
    GO_BACKEND_URL: str = "http://localhost:8001"
    
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
