"""
日志配置模块
"""

import logging
import logging.config
from pathlib import Path
import sys

from core.config import settings

def setup_logging():
    """设置日志配置"""
    
    # 确保日志目录存在
    log_file = Path(settings.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 日志配置
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[{asctime}] [{levelname}] [{name}] {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "[{asctime}] [{levelname}] [{name}] [{filename}:{lineno}] {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "detailed",
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # 记录启动信息
    logger = logging.getLogger(__name__)
    logger.info(f"📝 日志系统初始化完成 - 级别: {settings.LOG_LEVEL}")
    logger.info(f"📁 日志文件: {log_file}")
