"""
Redis 客户端管理
"""

import asyncio
import json
import logging
from typing import Any, Optional, Union
import aioredis
from core.config import settings


logger = logging.getLogger(__name__)


class RedisClient:
    """Redis 异步客户端封装"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.connection_pool: Optional[aioredis.ConnectionPool] = None
    
    async def connect(self):
        """连接到 Redis"""
        try:
            self.connection_pool = aioredis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                retry_on_timeout=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0
            )
            
            self.redis = aioredis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=True
            )
            
            # 测试连接
            await self.redis.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """断开 Redis 连接"""
        try:
            if self.redis:
                await self.redis.close()
            if self.connection_pool:
                await self.connection_pool.disconnect()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    async def get(self, key: str) -> Optional[str]:
        """获取键值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Union[str, int, float], 
        ex: Optional[int] = None
    ) -> bool:
        """设置键值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def setex(self, key: str, seconds: int, value: Any) -> bool:
        """设置键值并指定过期时间"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.setex(key, seconds, value)
        except Exception as e:
            logger.error(f"Redis SETEX error for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            if not self.redis:
                await self.connect()
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def lpush(self, key: str, *values: Any) -> int:
        """向列表左侧推入值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis LPUSH error for key {key}: {e}")
            return 0
    
    async def rpush(self, key: str, *values: Any) -> int:
        """向列表右侧推入值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.rpush(key, *values)
        except Exception as e:
            logger.error(f"Redis RPUSH error for key {key}: {e}")
            return 0
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """获取列表范围内的元素"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis LRANGE error for key {key}: {e}")
            return []
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """修剪列表"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.ltrim(key, start, end)
        except Exception as e:
            logger.error(f"Redis LTRIM error for key {key}: {e}")
            return False
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """获取哈希字段值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.hget(key, field)
        except Exception as e:
            logger.error(f"Redis HGET error for key {key}, field {field}: {e}")
            return None
    
    async def hset(self, key: str, field: str, value: Any) -> bool:
        """设置哈希字段值"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.hset(key, field, value)
        except Exception as e:
            logger.error(f"Redis HSET error for key {key}, field {field}: {e}")
            return False
    
    async def hgetall(self, key: str) -> dict:
        """获取哈希所有字段"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.hgetall(key)
        except Exception as e:
            logger.error(f"Redis HGETALL error for key {key}: {e}")
            return {}
    
    async def sadd(self, key: str, *values: Any) -> int:
        """向集合添加元素"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.sadd(key, *values)
        except Exception as e:
            logger.error(f"Redis SADD error for key {key}: {e}")
            return 0
    
    async def smembers(self, key: str) -> set:
        """获取集合所有成员"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.smembers(key)
        except Exception as e:
            logger.error(f"Redis SMEMBERS error for key {key}: {e}")
            return set()
    
    async def sismember(self, key: str, value: Any) -> bool:
        """检查是否为集合成员"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.sismember(key, value)
        except Exception as e:
            logger.error(f"Redis SISMEMBER error for key {key}: {e}")
            return False
    
    async def incr(self, key: str) -> int:
        """递增计数器"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return 0
    
    async def decr(self, key: str) -> int:
        """递减计数器"""
        try:
            if not self.redis:
                await self.connect()
            return await self.redis.decr(key)
        except Exception as e:
            logger.error(f"Redis DECR error for key {key}: {e}")
            return 0
    
    async def set_json(self, key: str, data: dict, ex: Optional[int] = None) -> bool:
        """存储 JSON 数据"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return await self.set(key, json_str, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET_JSON error for key {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[dict]:
        """获取 JSON 数据"""
        try:
            json_str = await self.get(key)
            if json_str:
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Redis GET_JSON error for key {key}: {e}")
            return None
    
    async def ping(self) -> bool:
        """检查连接状态"""
        try:
            if not self.redis:
                await self.connect()
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False


# 全局 Redis 客户端实例
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """获取 Redis 客户端实例"""
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client


async def init_redis():
    """初始化 Redis 连接"""
    await redis_client.connect()


async def close_redis():
    """关闭 Redis 连接"""
    await redis_client.disconnect()
