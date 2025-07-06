"""
配置参数模块
Configuration Parameters Module
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 根据环境变量加载不同的.env文件
env = os.getenv("ENV", "dev")
env_file = f".env.{env}"
load_dotenv(env_file)


class AppSettings(BaseSettings):
    """应用程序配置"""
    app_name: str = "DVSS-PPA System"
    app_version: str = "1.0.0"
    app_description: str = "Dynamic Verifiable Secret Sharing with Privacy‑Preserving Authentication"
    debug: bool = os.getenv("DEBUG", "True") == "True"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    openapi_url: str = "/api/v1/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # CORS配置
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]


class JwtSettings(BaseSettings):
    """JWT配置"""
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24小时
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7天


class DataBaseSettings(BaseSettings):
    """数据库配置"""
    db_type: str = os.getenv("DB_TYPE", "mysql")  # 支持mysql, postgresql
    db_host: str = os.getenv("DB_HOST", "localhost") 
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_username: str = os.getenv("DB_USERNAME", "root")
    db_password: str = os.getenv("DB_PASSWORD", "admin123")
    db_database: str = os.getenv("DB_DATABASE", "dvss")
    db_echo: str = os.getenv("DB_ECHO", "flase")
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))  # 最大溢出连接数
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))  # 连接池大小
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 连接池回收时间（秒）
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # 连接池超时时间（秒）
    # SQLAlchemy配置
    sqlalchemy_database_url: Optional[str] = None
    
    @field_validator("sqlalchemy_database_url", mode="before")
    def assemble_db_url(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        """组装数据库URL"""
        if v:
            return v
        db_type = info.data.get("db_type")
        db_host = info.data.get("db_host")
        db_port = info.data.get("db_port")
        db_username = info.data.get("db_username")
        db_password = info.data.get("db_password")
        db_database = info.data.get("db_database")
        
        if db_type == "postgresql":
            return f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
        elif db_type == "mysql":
            return f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
        elif db_type == "sqlite":
            return f"sqlite:///{db_database}.db"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")


class RedisSettings(BaseSettings):
    """Redis配置"""
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    redis_url: Optional[str] = None
    
    @field_validator("redis_url", mode="before")
    def assemble_redis_url(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        """组装Redis URL"""
        if v:
            return v
        redis_host = info.data.get("redis_host")
        redis_port = info.data.get("redis_port")
        redis_db = info.data.get("redis_db")
        redis_password = info.data.get("redis_password")
        
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            return f"redis://{redis_host}:{redis_port}/{redis_db}"


class UploadSettings(BaseSettings):
    """上传配置"""
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "pdf", "doc", "docx", "xls", "xlsx"]


class SensitivitySettings(BaseSettings):
    """敏感度配置"""
    sensitivity_config_path: str = os.getenv("SENSITIVITY_CONFIG_PATH", "/app/config/sensitivity.yaml")
    thresholds_config_path: str = os.getenv("THRESHOLDS_CONFIG_PATH", "/app/config/thresholds.yaml")


class MonitoringSettings(BaseSettings):
    """监控配置"""
    monitoring_interval: int = int(os.getenv("MONITORING_INTERVAL", "30"))
    metrics_history_size: int = int(os.getenv("METRICS_HISTORY_SIZE", "100"))


class LogSettings(BaseSettings):
    """日志配置"""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_path: str = os.getenv("LOG_PATH", "logs")
    log_filename: str = os.getenv("LOG_FILENAME", "dvss-python.log")
    log_rotation: str = os.getenv("LOG_ROTATION", "10 MB")
    log_retention: int = int(os.getenv("LOG_RETENTION", "30"))


# 配置实例
AppConfig = AppSettings()
JwtConfig = JwtSettings()
DataBaseConfig = DataBaseSettings()
RedisConfig = RedisSettings()
UploadConfig = UploadSettings()
SensitivityConfig = SensitivitySettings()
MonitoringConfig = MonitoringSettings()
LogConfig = LogSettings()

# 导出所有配置
__all__ = [
    "AppConfig",
    "JwtConfig", 
    "DataBaseConfig", 
    "RedisConfig", 
    "UploadConfig", 
    "SensitivityConfig",
    "MonitoringConfig",
    "LogConfig"
]
