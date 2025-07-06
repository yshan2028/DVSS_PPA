"""
数据库连接配置
Database Configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接
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
    
    logger = LogUtil.get_logger("database")
    logger.info('初始化数据库连接...')
    Base.metadata.create_all(bind=engine)
    logger.info('数据库表创建完成')
