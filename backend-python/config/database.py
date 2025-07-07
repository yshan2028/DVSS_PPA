"""
数据库连接配置
Database Configuration
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# 创建异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,  # 直接使用配置的URL
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO,
)

# 创建同步引擎（用于初始化表）
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO,
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

# 创建同步会话工厂（保持向后兼容）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


async def get_db():
    """
    获取异步数据库会话
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db():
    """
    获取同步数据库会话（用于向后兼容）
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_create_table():
    """
    应用启动时初始化数据库连接和创建表
    """
    from utils.log_util import LogUtil

    logger = LogUtil.get_logger('database')
    logger.info('初始化数据库连接...')
    Base.metadata.create_all(bind=engine)
    logger.info('数据库表创建完成')
