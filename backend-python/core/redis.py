"""
Redis模块
用于缓存和会话管理
"""

import aioredis
import logging
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[aioredis.Redis] = None

async def init_redis():
    """初始化Redis连接"""
    global redis_client
    
    try:
        redis_client = aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )
        
        # 测试连接
        await redis_client.ping()
        logger.info("✅ Redis连接成功")
        
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败: {e}")
        redis_client = None

def get_redis():
    """获取Redis客户端"""
    return redis_client

async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("🛑 Redis连接已关闭")
