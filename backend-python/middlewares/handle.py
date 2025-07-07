"""
中间件统一处理模块
"""

from fastapi import FastAPI

from .cors_middleware import setup_cors
from .gzip_middleware import add_gzip_middleware


def handle_middleware(app: FastAPI) -> None:
    """统一加载所有中间件"""
    # 添加CORS中间件
    setup_cors(app)
    
    # 添加Gzip压缩中间件
    add_gzip_middleware(app)
