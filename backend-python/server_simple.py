"""
DVSS-PPA FastAPI 应用入口 (简化版本)
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

# 本地模块导入
from middlewares.cors_middleware import setup_cors

def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    
    app = FastAPI(
        title="DVSS-PPA System",
        description="Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 中间件
    setup_cors(app)
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    
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
    
    return app

# 创建应用实例
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "server_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
