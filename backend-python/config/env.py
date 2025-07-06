"""
环境配置文件
Environment Configuration
"""
import os
from typing import Optional

class Config:
    """基础配置类"""
    
    # 应用配置
    APP_NAME = "DVSS-PPA Backend"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # 数据库配置
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://dvss:admin123@postgres:5432/dvss_db"
    )
    
    # MongoDB 配置
    MONGODB_URL = os.getenv(
        "MONGODB_URL", 
        "mongodb://dvss:admin123@mongo:27017/dvss_data"
    )
    
    # Redis 配置
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "admin123")
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Neo4j 配置
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "admin123")
    
    # JWT 配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dvss-ppa-secret-key-2024")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    
    # Go 后端配置
    GO_BACKEND_URL = os.getenv("GO_BACKEND_URL", "http://backend-go:8001")
    
    # Fabric 配置
    FABRIC_NETWORK = os.getenv("FABRIC_NETWORK", "dvss-ppa")
    FABRIC_CHANNEL = os.getenv("FABRIC_CHANNEL", "dvss-channel")
    FABRIC_CHAINCODE = os.getenv("FABRIC_CHAINCODE", "dvss-chaincode")
    
    # 默认用户配置
    DEFAULT_USERS = [
        {
            "username": "seller",
            "password": "admin",
            "role": "seller",
            "email": "seller@dvss-ppa.com"
        },
        {
            "username": "payment_provider", 
            "password": "admin",
            "role": "payment_provider",
            "email": "payment@dvss-ppa.com"
        },
        {
            "username": "logistics",
            "password": "admin", 
            "role": "logistics",
            "email": "logistics@dvss-ppa.com"
        },
        {
            "username": "auditor",
            "password": "admin",
            "role": "auditor", 
            "email": "auditor@dvss-ppa.com"
        },
        {
            "username": "platform",
            "password": "admin",
            "role": "platform",
            "email": "platform@dvss-ppa.com"
        }
    ]
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS 配置
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://frontend",
        "http://dvss-frontend"
    ]
    
    # 文件上传配置
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/app/uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 安全配置
    BCRYPT_LOG_ROUNDS = 12
    
    @classmethod
    def get_database_url(cls) -> str:
        """获取数据库连接URL"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_mongodb_url(cls) -> str:
        """获取MongoDB连接URL"""
        return cls.MONGODB_URL
    
    @classmethod
    def get_redis_url(cls) -> str:
        """获取Redis连接URL"""
        return cls.REDIS_URL


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    DATABASE_URL = "postgresql://dvss:admin123@postgres:5432/dvss_test_db"
    MONGODB_URL = "mongodb://dvss:admin123@mongo:27017/dvss_test_data"


# 根据环境变量选择配置
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config() -> Config:
    """获取当前环境配置"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    return config_mapping.get(env, DevelopmentConfig)


# 全局配置实例
config = get_config()
