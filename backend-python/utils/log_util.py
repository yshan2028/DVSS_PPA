"""
日志工具类
统一日志配置和记录
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from core.config import settings

class LogUtil:
    """日志工具类"""
    
    _logger_cache = {}
    
    @classmethod
    def get_logger(cls, name: str = "dvss") -> logging.Logger:
        """
        获取日志器
        
        Args:
            name: 日志器名称
            
        Returns:
            logging.Logger: 日志器实例
        """
        if name in cls._logger_cache:
            return cls._logger_cache[name]
        
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            cls._setup_logger(logger)
        
        cls._logger_cache[name] = logger
        return logger
    
    @classmethod
    def _setup_logger(cls, logger: logging.Logger):
        """
        设置日志器
        
        Args:
            logger: 日志器实例
        """
        # 设置日志级别
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # 创建格式器
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if settings.DEBUG:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 文件处理器
        if settings.LOG_FILE:
            try:
                # 确保日志目录存在
                log_path = Path(settings.LOG_FILE)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 创建轮转文件处理器
                file_handler = logging.handlers.RotatingFileHandler(
                    filename=settings.LOG_FILE,
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                
            except Exception as e:
                # 如果文件日志设置失败，至少保证控制台日志可用
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(log_level)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
                logger.error(f"Failed to setup file logging: {e}")
    
    @classmethod
    def log_request(cls, method: str, url: str, user_id: Optional[int] = None, 
                   ip: Optional[str] = None, user_agent: Optional[str] = None):
        """
        记录请求日志
        
        Args:
            method: HTTP方法
            url: 请求URL
            user_id: 用户ID
            ip: 客户端IP
            user_agent: 用户代理
        """
        logger = cls.get_logger("request")
        logger.info(f"REQUEST - {method} {url} - User:{user_id} - IP:{ip} - UA:{user_agent}")
    
    @classmethod
    def log_response(cls, method: str, url: str, status_code: int, 
                    execution_time: float, user_id: Optional[int] = None):
        """
        记录响应日志
        
        Args:
            method: HTTP方法
            url: 请求URL
            status_code: 状态码
            execution_time: 执行时间(秒)
            user_id: 用户ID
        """
        logger = cls.get_logger("response")
        logger.info(f"RESPONSE - {method} {url} - {status_code} - {execution_time:.3f}s - User:{user_id}")
    
    @classmethod
    def log_security(cls, event: str, user_id: Optional[int] = None, 
                    ip: Optional[str] = None, details: Optional[str] = None):
        """
        记录安全日志
        
        Args:
            event: 安全事件
            user_id: 用户ID
            ip: 客户端IP
            details: 详细信息
        """
        logger = cls.get_logger("security")
        logger.warning(f"SECURITY - {event} - User:{user_id} - IP:{ip} - Details:{details}")
    
    @classmethod
    def log_error(cls, error: Exception, context: Optional[str] = None, 
                 user_id: Optional[int] = None):
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 上下文信息
            user_id: 用户ID
        """
        logger = cls.get_logger("error")
        logger.error(f"ERROR - {type(error).__name__}: {str(error)} - Context:{context} - User:{user_id}", 
                    exc_info=True)
    
    @classmethod
    def log_business(cls, action: str, user_id: Optional[int] = None, 
                    resource_id: Optional[str] = None, details: Optional[str] = None):
        """
        记录业务日志
        
        Args:
            action: 业务操作
            user_id: 用户ID
            resource_id: 资源ID
            details: 详细信息
        """
        logger = cls.get_logger("business")
        logger.info(f"BUSINESS - {action} - User:{user_id} - Resource:{resource_id} - Details:{details}")

class AuditLogger:
    """审计日志类"""
    
    def __init__(self):
        self.logger = LogUtil.get_logger("audit")
    
    def log_user_action(self, action: str, user_id: int, target_user_id: Optional[int] = None,
                       details: Optional[dict] = None):
        """
        记录用户操作审计日志
        
        Args:
            action: 操作类型
            user_id: 操作用户ID
            target_user_id: 目标用户ID
            details: 详细信息
        """
        self.logger.info(f"USER_ACTION - {action} - Operator:{user_id} - Target:{target_user_id} - Details:{details}")
    
    def log_data_access(self, action: str, user_id: int, shard_id: str, 
                       result: str, details: Optional[dict] = None):
        """
        记录数据访问审计日志
        
        Args:
            action: 访问类型
            user_id: 用户ID
            shard_id: 分片ID
            result: 访问结果
            details: 详细信息
        """
        self.logger.info(f"DATA_ACCESS - {action} - User:{user_id} - Shard:{shard_id} - Result:{result} - Details:{details}")
    
    def log_permission_change(self, action: str, grantor_id: int, user_id: int, 
                             resource_id: str, permissions: dict):
        """
        记录权限变更审计日志
        
        Args:
            action: 操作类型
            grantor_id: 授权者ID
            user_id: 用户ID
            resource_id: 资源ID
            permissions: 权限信息
        """
        self.logger.info(f"PERMISSION_CHANGE - {action} - Grantor:{grantor_id} - User:{user_id} - Resource:{resource_id} - Permissions:{permissions}")
    
    def log_system_event(self, event: str, details: Optional[dict] = None):
        """
        记录系统事件审计日志
        
        Args:
            event: 系统事件
            details: 详细信息
        """
        self.logger.info(f"SYSTEM_EVENT - {event} - Details:{details}")

# 创建全局审计日志实例
audit_logger = AuditLogger()
