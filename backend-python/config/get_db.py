"""
数据库依赖注入
Database Dependency Injection
"""

from config.database import AsyncSessionLocal, Base, async_engine
from utils.log_util import LogUtil

logger = LogUtil.get_logger('get_db')


async def get_db():
    """
    获取异步数据库会话
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
    """
    async with AsyncSessionLocal() as session:
        yield session


async def init_create_table():
    """
    应用启动时异步初始化数据库连接和创建表
    """
    logger.info('异步初始化数据库连接...')

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info('数据库表创建完成')
