"""
数据库连接配置
Database Configuration
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config.settings import settings

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,  # 直接使用配置的URL
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# 创建基础模型类
Base = declarative_base()


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
    from utils.log_util import LogUtil

    logger = LogUtil.get_logger('database')
    logger.info('异步初始化数据库连接...')
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info('数据库表创建完成')
