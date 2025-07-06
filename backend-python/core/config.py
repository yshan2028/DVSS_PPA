"""
应用配置模块
参考 Dash-FastAPI-Admin 的配置结构
"""

from pydantic_settings import BaseSettings
from typing import Optional, List, Union
import os
from pathlib import Path

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "DVSS-PPA"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://dvss:dvss123@localhost:5432/dvss_db"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "dvss_encrypted_data"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Neo4j配置 (权限管理)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123"
    
    # JWT配置
    SECRET_KEY: str = "dvss-ppa-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8081,http://127.0.0.1:3000,http://127.0.0.1:8080,http://127.0.0.1:8081"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # 加密配置
    ENCRYPTION_KEY: str = "dvss-encryption-key-32-bytes-long"
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/dvss-python.log"
    
    # Go后端配置 (用于Fabric通信)
    GO_BACKEND_URL: str = "http://localhost:8001"
    
    # ZKP配置
    ZKP_FIELD_SIZE: int = 2**256 - 2**32 * 351 + 1  # BN254 field size
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建全局配置实例
settings = Settings()
