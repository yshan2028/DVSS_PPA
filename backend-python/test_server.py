"""
DVSS-PPA FastAPI 简化测试版
"""
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.config import settings
from middlewares.cors_middleware import setup_cors
from config.get_db import engine, Base
from utils.log_util import LogUtil

logger = LogUtil.get_logger("test_server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting DVSS-PPA application...")
    
    # 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        logger.warning("Application will continue without database")
    
    logger.info("DVSS-PPA application started successfully")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down DVSS-PPA application...")


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="DVSS-PPA - Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # 设置CORS中间件
    setup_cors(app)
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    @app.get("/")
    async def root():
        """根端点"""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    """直接运行应用"""
    uvicorn.run(
        "test_server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
