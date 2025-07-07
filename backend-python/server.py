"""
DVSS-PPA FastAPI 应用入口
"""

from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI

# 本地模块导入
from config.database import init_create_table
from exceptions.handle import register_exception_handlers
from middlewares.handle import handle_middleware
from module_dvss.controller.auth_controller import router as auth_router
from module_dvss.controller.dvss_controller import router as dvss_router
from module_dvss.controller.field_controller import router as field_router
from module_dvss.controller.log_controller import router as log_router
from module_dvss.controller.metrics_controller import router as metrics_router
from module_dvss.controller.order_controller import router as order_router
from module_dvss.controller.role_controller import router as role_router
from module_dvss.controller.shard_controller import router as shard_router
from module_dvss.controller.user_controller import router as user_router
from module_dvss.entity import Base  # 导入所有实体模型
from utils.log_util import LogUtil

# 初始化日志
logger = LogUtil.get_logger(__name__)


async def init_database():
    """异步初始化数据库"""
    try:
        # 异步创建数据库表
        await init_create_table()
        logger.info('✅ 数据库表已就绪')
        
        # 异步初始化数据（创建默认角色和用户）
        from scripts.init_db import init_database as init_data
        await init_data()
        logger.info('✅ 数据库数据初始化完成')
        
    except Exception as exc:
        logger.exception('❌ 数据库初始化失败', exc_info=exc)
        raise


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动阶段
    logger.info('🚀 启动 DVSS-PPA 应用...')

    # 异步初始化数据库
    await init_database()

    logger.info('✅ DVSS-PPA启动成功')
    yield

    # 关闭阶段
    logger.info('👋 应用关闭完成')


# 初始化FastAPI对象
app = FastAPI(
    title='DVSS-PPA System',
    description='Dynamic Verifiable Secret Sharing with Privacy-Preserving Authentication',
    version='1.0.0',
    openapi_url='/api/v1/openapi.json',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)

# 加载中间件处理方法
handle_middleware(app)

# 加载全局异常处理方法
register_exception_handlers(app)

# 加载路由列表
controller_list = [
    {'router': auth_router, 'prefix': '/api/v1/auth', 'tags': ['认证管理']},
    {'router': user_router, 'prefix': '/api/v1', 'tags': ['用户管理']},
    {'router': role_router, 'prefix': '/api/v1', 'tags': ['角色管理']},
    {'router': field_router, 'prefix': '/api/v1', 'tags': ['字段管理']},
    {'router': dvss_router, 'prefix': '/api/v1/dvss', 'tags': ['DVSS核心']},
    {'router': order_router, 'prefix': '/api/v1/orders', 'tags': ['订单管理']},
    {'router': shard_router, 'prefix': '/api/v1/shards', 'tags': ['分片管理']},
    {'router': log_router, 'prefix': '/api/v1/logs', 'tags': ['日志管理']},
    {'router': metrics_router, 'tags': ['监控指标']},
]

for controller in controller_list:
    app.include_router(
        router=controller.get('router'), prefix=controller.get('prefix', ''), tags=controller.get('tags')
    )


# 健康检查
@app.get('/health', tags=['Meta'])
async def health_check():
    return {
        'status': 'healthy',
        'service': 'DVSS-PPA System',
        'version': app.version,
    }


@app.get('/', tags=['Meta'])
async def root():
    return {
        'message': '欢迎使用 DVSS-PPA System API',
        'version': app.version,
        'docs': app.docs_url,
    }


if __name__ == '__main__':
    uvicorn.run(
        'server:app',
        host='0.0.0.0',
        port=8005,
        reload=True,
        log_level='info',
    )
