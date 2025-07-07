"""
数据库依赖注入
Database Dependency Injection
"""

from config.database import AsyncSessionLocal, Base, engine
from utils.log_util import LogUtil

logger = LogUtil.get_logger('get_db')


async def get_db():
    """
    获取异步数据库会话
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
    """
    async with AsyncSessionLocal() as session:
        yield session


def init_create_table():
    """
    应用启动时初始化数据库连接
    """
    logger.info('初始化数据库连接...')
    Base.metadata.create_all(bind=engine)
    logger.info('数据库连接成功')
