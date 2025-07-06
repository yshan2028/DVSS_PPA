"""
数据库模块
支持PostgreSQL和MongoDB
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL配置
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

# MongoDB配置
mongodb_client: AsyncIOMotorClient = None
mongodb_db = None

async def init_database():
    """初始化数据库连接"""
    global mongodb_client, mongodb_db
    
    try:
        # 初始化MongoDB
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client[settings.MONGODB_DB]
        
        # 测试连接
        await mongodb_client.admin.command('ping')
        logger.info("✅ MongoDB连接成功")
        
        # 创建PostgreSQL表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ PostgreSQL连接成功")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise

def get_db():
    """获取PostgreSQL数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mongodb():
    """获取MongoDB数据库实例"""
    return mongodb_db

async def close_database():
    """关闭数据库连接"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("🛑 数据库连接已关闭")
