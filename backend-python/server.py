"""
DVSS-PPA FastAPI 应用入口
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

# 本地模块导入
from config.database import engine
from module_dvss.entity import Base  # 导入所有实体模型
from exceptions.handle import register_exception_handlers
from middlewares.cors_middleware import setup_cors
from module_dvss.controller.auth_controller import router as auth_router
from module_dvss.controller.user_controller import router as user_router
from module_dvss.controller.role_controller import router as role_router
from module_dvss.controller.field_controller import router as field_router
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
    app.include_router(user_router, prefix="/api/v1", tags=["用户管理"])
    app.include_router(role_router, prefix="/api/v1", tags=["角色管理"])
    app.include_router(field_router, prefix="/api/v1", tags=["字段管理"])
    app.include_router(dvss_router, prefix="/api/v1/dvss", tags=["DVSS"])
    
    # 导入并注册订单管理路由
    try:
        from module_dvss.controller.order_controller import router as order_router
        app.include_router(order_router, tags=["订单管理"])
        logger.info("✅ 订单管理路由已注册")
    except ImportError as e:
        logger.warning(f"⚠️ 无法导入订单管理路由: {e}")
    
    # 导入并注册分片管理路由
    try:
        from module_dvss.controller.shard_controller import router as shard_router
        app.include_router(shard_router, tags=["分片管理"])
        logger.info("✅ 分片管理路由已注册")
    except ImportError as e:
        logger.warning(f"⚠️ 无法导入分片管理路由: {e}")
    
    # 导入并注册日志管理路由
    try:
        from module_dvss.controller.log_controller import router as log_router
        app.include_router(log_router, tags=["日志管理"])
        logger.info("✅ 日志管理路由已注册")
    except ImportError as e:
        logger.warning(f"⚠️ 无法导入日志管理路由: {e}")
    
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
