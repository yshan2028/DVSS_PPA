"""
DVSS-PPA FastAPI 主应用入口
Main FastAPI Application Entry Point
"""
import uvicorn
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from core.database import engine, Base
from core.redis_client import get_redis
from middlewares.cors_middleware import setup_cors
from exceptions.handle import register_exception_handlers
from module_dvss.controller.dvss_controller import router as dvss_router
from module_dvss.controller.auth_controller import router as auth_router
from module_dvss.service.monitoring_service import MonitoringService
from utils.log_util import LogUtil

logger = LogUtil.get_logger("server")

# 全局监控服务实例
monitoring_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global monitoring_service
    
    # 启动时执行
    logger.info("Starting DVSS-PPA application...")
    
    # 创建数据库表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        logger.warning("Application will continue without database")
    
    # 测试Redis连接
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
        # 启动监控服务
        monitoring_service = MonitoringService(redis_client=redis_client)
        asyncio.create_task(monitoring_service.start_monitoring(interval=30))
        logger.info("System monitoring service started")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        logger.warning("Application will continue without Redis and monitoring")
    
    logger.info("DVSS-PPA application started successfully")
    yield
    
    # 关闭时执行
    logger.info("Shutting down DVSS-PPA application...")
    if monitoring_service:
        monitoring_service.stop_monitoring()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title="DVSS-PPA System",
        version="1.0.0",
        description="Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # 设置CORS中间件
    setup_cors(app)
    
    # 添加Gzip压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 设置异常处理器
    register_exception_handlers(app)
    
    # 注册路由
    register_routers(app)
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {
            "status": "healthy",
            "service": "DVSS-PPA System",
            "version": "1.0.0",
            "environment": "development"
        }
    
    @app.get("/")
    async def root():
        """根端点"""
        return {
            "message": "Welcome to DVSS-PPA System API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    return app


def register_routers(app: FastAPI):
    """注册所有路由"""
    
    # 认证模块路由
    app.include_router(auth_router)
    
    # DVSS核心模块路由
    app.include_router(dvss_router)
    
    logger.info("All routers registered successfully")


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    """直接运行应用"""
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
