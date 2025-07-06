"""
CORS中间件配置
CORS Middleware Configuration
"""
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


def setup_cors(app):
    """设置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
