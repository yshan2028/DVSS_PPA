"""
数据库初始化脚本
异步版本
"""

import asyncio

from config.database import async_engine, Base
from module_dvss.entity import *  # 导入所有实体模型
from utils.log_util import LogUtil

logger = LogUtil.get_logger(__name__)


async def init_database():
    """异步初始化数据库"""
    try:
        logger.info('开始创建数据库表...')
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info('✅ 数据库表创建完成')
    except Exception as e:
        logger.error(f'❌ 数据库初始化失败: {e}')
        raise


def main():
    """主函数"""
    asyncio.run(init_database())


if __name__ == '__main__':
    main()
