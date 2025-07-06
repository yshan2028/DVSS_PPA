"""
异常处理器
统一处理应用中的异常
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from datetime import datetime

from exceptions.custom_exception import DVSSException
from utils.response_util import ResponseUtil
from utils.log_util import LogUtil

logger = LogUtil.get_logger("exception_handler")

async def dvss_exception_handler(request: Request, exc: DVSSException) -> JSONResponse:
    """
    处理DVSS自定义异常
    """
    logger.error(f"DVSS Exception: {exc.message}", exc_info=True)
    
    response_data = ResponseUtil.error(
        message=exc.message,
        code=exc.code,
        data=exc.details
    )
    response_data["timestamp"] = datetime.now().isoformat()
    
    return JSONResponse(
        status_code=exc.code,
        content=response_data
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    处理HTTP异常
    """
    logger.warning(f"HTTP Exception: {exc.detail}")
    
    response_data = ResponseUtil.error(
        message=exc.detail,
        code=exc.status_code
    )
    response_data["timestamp"] = datetime.now().isoformat()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求验证异常
    """
    logger.warning(f"Validation Exception: {exc.errors()}")
    
    # 格式化验证错误信息
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_details.append(f"{field}: {message}")
    
    response_data = ResponseUtil.error(
        message="请求参数验证失败",
        code=422,
        data={
            "validation_errors": error_details,
            "details": exc.errors()
        }
    )
    response_data["timestamp"] = datetime.now().isoformat()
    
    return JSONResponse(
        status_code=422,
        content=response_data
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理通用异常
    """
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    
    # 在生产环境中不暴露详细的错误信息
    from core.config import settings
    
    if settings.DEBUG:
        error_detail = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc()
        }
    else:
        error_detail = None
    
    response_data = ResponseUtil.error(
        message="服务器内部错误",
        code=500,
        data=error_detail
    )
    response_data["timestamp"] = datetime.now().isoformat()
    
    return JSONResponse(
        status_code=500,
        content=response_data
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    处理Starlette HTTP异常
    """
    logger.warning(f"Starlette HTTP Exception: {exc.detail}")
    
    response_data = ResponseUtil.error(
        message=exc.detail,
        code=exc.status_code
    )
    response_data["timestamp"] = datetime.now().isoformat()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

def register_exception_handlers(app):
    """
    注册异常处理器
    """
    app.add_exception_handler(DVSSException, dvss_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
