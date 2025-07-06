"""
DVSS-PPA FastAPI 应用入口
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

# 本地模块导入  
from config.database import engine
from module_dvss.entity import Base
from exceptions.handle import register_exception_handlers
from middlewares.cors_middleware import setup_cors
from module_dvss.controller.auth_controller import router as auth_router
from module_dvss.controller.dvss_controller import router as dvss_router
from utils.log_util import LogUtil

# 初始化日志
logger = LogUtil.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动阶段
    logger.info("🚀 启动 DVSS-PPA 应用...")
    
    try:
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表已就绪")
    except Exception as exc:
        logger.exception("❌ 数据库初始化失败", exc_info=exc)
    
    yield
    
    # 关闭阶段
    logger.info("👋 应用关闭完成")

def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title="DVSS-PPA System",
        description="Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # 中间件
    setup_cors(app)
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    
    # 异常处理器
    register_exception_handlers(app)
    
    # 路由注册
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(dvss_router, prefix="/api/v1/dvss", tags=["DVSS"])
    
    # 健康检查
    @app.get("/health", tags=["Meta"])
    async def health_check():
        return {
            "status": "healthy",
            "service": "DVSS-PPA System",
            "version": app.version,
        }
    
    @app.get("/", tags=["Meta"])
    async def root():
        return {
            "message": "欢迎使用 DVSS-PPA System API",
            "version": app.version,
            "docs": app.docs_url,
        }
    
    logger.info("✅ FastAPI 应用创建完毕")
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
