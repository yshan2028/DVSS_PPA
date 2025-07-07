"""
Redis连接配置
Redis Configuration
"""

import json

from typing import Any, Optional

from redis import asyncio as aioredis
from redis.exceptions import AuthenticationError, RedisError, TimeoutError

from config.env import RedisConfig
from utils.log_util import LogUtil

logger = LogUtil.get_logger(__name__)


class RedisUtil:
    """
    Redis相关方法
    """

    @classmethod
    async def create_redis_pool(cls) -> aioredis.Redis:
        """
        创建Redis连接池
        """
        try:
            if RedisConfig.redis_password:
                redis = aioredis.from_url(
                    f'redis://:{RedisConfig.redis_password}@{RedisConfig.redis_host}:{RedisConfig.redis_port}/{RedisConfig.redis_db}',
                    encoding='utf-8',
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
            else:
                redis = aioredis.from_url(
                    f'redis://{RedisConfig.redis_host}:{RedisConfig.redis_port}/{RedisConfig.redis_db}',
                    encoding='utf-8',
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
            # 测试连接
            await redis.ping()
            logger.info('✅ Redis连接成功')
            return redis
        except (AuthenticationError, TimeoutError, RedisError) as e:
            logger.error(f'❌ Redis连接失败: {e}')
            return None

    @classmethod
    async def close_redis_pool(cls, app):
        """
        应用关闭时关闭redis连接

        :param app: fastapi对象
        :return:
        """
        if hasattr(app.state, 'redis') and app.state.redis:
            await app.state.redis.close()
            logger.info('🔌 Redis连接已关闭')

    @classmethod
    async def get_cache_prefix(cls):
        """
        获取缓存前缀
        """
        return 'dvss_admin:'


# Redis服务类，提供常用的Redis操作
class RedisService:
    """Redis 服务类，提供常用的Redis操作"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置键值对

        :param key: 键名
        :param value: 值
        :param expire: 过期时间（秒）
        :return: 是否成功
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            result = await self.redis.set(key, value, ex=expire)
            return bool(result)
        except RedisError as e:
            logger.error(f'Redis SET 操作失败: {e}')
            return False

    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取值

        :param key: 键名
        :param default: 默认值
        :return: 查询结果或默认值
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return default

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f'Redis GET 操作失败: {e}')
            return default

    async def delete(self, *keys: str) -> int:
        """
        删除键

        :param keys: 键名列表
        :return: 删除的键数量
        """
        try:
            return await self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f'Redis DELETE 操作失败: {e}')
            return 0

    async def exists(self, key: str) -> bool:
        """
        检查键是否存在

        :param key: 键名
        :return: 是否存在
        """
        try:
            return bool(await self.redis.exists(key))
        except RedisError as e:
            logger.error(f'Redis EXISTS 操作失败: {e}')
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        :param key: 键名
        :param seconds: 过期秒数
        :return: 是否成功
        """
        try:
            return bool(await self.redis.expire(key, seconds))
        except RedisError as e:
            logger.error(f'Redis EXPIRE 操作失败: {e}')
            return False

    async def ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间

        :param key: 键名
        :return: 剩余秒数
        """
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            logger.error(f'Redis TTL 操作失败: {e}')
            return -1

    async def incr(self, key: str, amount: int = 1) -> int:
        """
        递增计数器

        :param key: 键名
        :param amount: 增加量
        :return: 增加后的值
        """
        try:
            return await self.redis.incr(key, amount)
        except RedisError as e:
            logger.error(f'Redis INCR 操作失败: {e}')
            return 0

    async def hash_set(self, name: str, mapping: dict) -> int:
        """
        设置哈希表

        :param name: 哈希表名称
        :param mapping: 哈希表字段值映射
        :return: 新增字段数量
        """
        try:
            # 将字典值转换为字符串
            str_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    str_mapping[k] = json.dumps(v, ensure_ascii=False)
                else:
                    str_mapping[k] = str(v)

            return await self.redis.hset(name, mapping=str_mapping)
        except RedisError as e:
            logger.error(f'Redis HSET 操作失败: {e}')
            return 0

    async def hash_get(self, name: str, key: str) -> Any:
        """
        获取哈希表字段值

        :param name: 哈希表名称
        :param key: 字段名
        :return: 字段值
        """
        try:
            value = await self.redis.hget(name, key)
            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f'Redis HGET 操作失败: {e}')
            return None

    async def hash_get_all(self, name: str) -> dict:
        """
        获取整个哈希表

        :param name: 哈希表名称
        :return: 哈希表数据
        """
        try:
            data = await self.redis.hgetall(name)
            result = {}

            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v

            return result
        except RedisError as e:
            logger.error(f'Redis HGETALL 操作失败: {e}')
            return {}

    async def list_push(self, key: str, *values: Any) -> int:
        """
        向列表左侧推入元素

        :param key: 列表键名
        :param values: 值列表
        :return: 列表长度
        """
        try:
            str_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    str_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    str_values.append(str(value))

            return await self.redis.lpush(key, *str_values)
        except RedisError as e:
            logger.error(f'Redis LPUSH 操作失败: {e}')
            return 0

    async def list_pop(self, key: str) -> Any:
        """
        从列表右侧弹出元素

        :param key: 列表键名
        :return: 弹出的元素
        """
        try:
            value = await self.redis.rpop(key)
            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f'Redis RPOP 操作失败: {e}')
            return None

    async def list_range(self, key: str, start: int = 0, end: int = -1) -> list:
        """
        获取列表范围内的元素

        :param key: 列表键名
        :param start: 起始位置
        :param end: 结束位置
        :return: 元素列表
        """
        try:
            values = await self.redis.lrange(key, start, end)
            result = []

            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)

            return result
        except RedisError as e:
            logger.error(f'Redis LRANGE 操作失败: {e}')
            return []
