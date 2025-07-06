"""
Redis连接配置
"""
import redis
from typing import Optional
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class RedisUtil:
    """
    Redis工具类
    """
    redis_client: Optional[redis.Redis] = None

    @classmethod
    def create_redis_pool(cls) -> redis.Redis:
        """
        创建Redis连接池
        """
        try:
            cls.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )
            # 测试连接
            cls.redis_client.ping()
            logger.info("Redis connection pool created successfully")
            return cls.redis_client
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {e}")
            raise

    @classmethod
    def get_redis(cls) -> redis.Redis:
        """
        获取Redis客户端
        """
        if cls.redis_client is None:
            cls.create_redis_pool()
        return cls.redis_client

    @classmethod
    def close_redis_pool(cls):
        """
        关闭Redis连接池
        """
        if cls.redis_client:
            cls.redis_client.close()
            cls.redis_client = None
            logger.info("Redis connection pool closed")

    @classmethod
    def check_redis_connection(cls) -> bool:
        """
        检查Redis连接
        """
        try:
            redis_client = cls.get_redis()
            redis_client.ping()
            logger.info("Redis connection successful")
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False

# 全局Redis实例
def get_redis_client() -> redis.Redis:
    """
    获取Redis客户端实例
    """
    return RedisUtil.get_redis()

# 兼容性函数别名
def get_redis_pool() -> redis.Redis:
    """
    获取Redis连接池（兼容性函数）
    """
    return get_redis_client()