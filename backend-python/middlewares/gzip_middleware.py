from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


def add_gzip_middleware(app: FastAPI):
    """添加GZIP压缩中间件"""
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
    )
