#!/usr/bin/env python3
"""
ETL数据处理服务
ETL Data Processing Service
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
import asyncio
import asyncpg
import pymongo
import redis

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ETL-Service')

class ETLProcessor:
    def __init__(self):
        self.pg_url = os.getenv('DATABASE_URL', 'postgresql://dvss:dvss123@postgres:5432/dvss_db')
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://mongo:27017')  # 移除认证信息
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        
        self.pg_pool = None
        self.mongo_client = None
        self.redis_client = None
        
    async def init_connections(self):
        """初始化数据库连接"""
        try:
            # PostgreSQL连接池
            self.pg_pool = await asyncpg.create_pool(self.pg_url)
            logger.info("PostgreSQL连接池初始化成功")
            
            # MongoDB连接
            self.mongo_client = pymongo.MongoClient(self.mongo_url)
            self.mongo_db = self.mongo_client['dvss_data']
            logger.info("MongoDB连接初始化成功")
            
            # Redis连接
            self.redis_client = redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            sys.exit(1)
    
    async def process_order_data(self):
        """处理订单数据ETL"""
        try:
            async with self.pg_pool.acquire() as conn:
                # 获取最近一小时的订单数据
                query = """
                SELECT id, order_id, customer_name, total_amount, 
                       sensitivity_score, sensitivity_level, created_at
                FROM orders 
                WHERE created_at > $1
                """
                one_hour_ago = datetime.now() - timedelta(hours=1)
                rows = await conn.fetch(query, one_hour_ago)
                
                if rows:
                    # 转换数据格式并存储到MongoDB
                    documents = []
                    for row in rows:
                        doc = {
                            'order_id': row['order_id'],
                            'customer_name': row['customer_name'],
                            'order_amount': float(row['total_amount']) if row['total_amount'] else 0,
                            'sensitivity_level': row['sensitivity_level'] or 'unknown',
                            'processed_at': datetime.now(),
                            'source': 'postgres_etl'
                        }
                        documents.append(doc)
                    
                    # 批量插入MongoDB
                    collection = self.mongo_db['processed_orders']
                    result = collection.insert_many(documents)
                    logger.info(f"处理了 {len(documents)} 条订单数据，插入到MongoDB")
                    
                    # 更新统计信息到Redis
                    stats_key = f"etl_stats:{datetime.now().strftime('%Y-%m-%d-%H')}"
                    self.redis_client.hincrby(stats_key, 'processed_orders', len(documents))
                    self.redis_client.expire(stats_key, 86400)  # 24小时过期
                    
        except Exception as e:
            logger.error(f"订单数据ETL处理失败: {e}")
    
    async def generate_analytics(self):
        """生成分析数据"""
        try:
            # 从MongoDB获取数据进行分析
            collection = self.mongo_db['processed_orders']
            
            # 敏感度统计
            pipeline = [
                {
                    '$group': {
                        '_id': '$sensitivity_level',
                        'count': {'$sum': 1},
                        'avg_amount': {'$avg': '$order_amount'}
                    }
                }
            ]
            
            sensitivity_stats = list(collection.aggregate(pipeline))
            
            # 存储分析结果到Redis
            analytics_key = f"analytics:{datetime.now().strftime('%Y-%m-%d')}"
            for stat in sensitivity_stats:
                self.redis_client.hset(
                    analytics_key,
                    f"sensitivity_{stat['_id']}_count",
                    stat['count']
                )
                self.redis_client.hset(
                    analytics_key,
                    f"sensitivity_{stat['_id']}_avg_amount",
                    round(stat['avg_amount'], 2)
                )
            
            self.redis_client.expire(analytics_key, 86400 * 7)  # 7天过期
            logger.info("分析数据生成完成")
            
        except Exception as e:
            logger.error(f"分析数据生成失败: {e}")
    
    async def cleanup_old_data(self):
        """清理过期数据"""
        try:
            # 清理MongoDB中7天前的数据
            seven_days_ago = datetime.now() - timedelta(days=7)
            collection = self.mongo_db['processed_orders']
            result = collection.delete_many({'processed_at': {'$lt': seven_days_ago}})
            
            if result.deleted_count > 0:
                logger.info(f"清理了 {result.deleted_count} 条过期数据")
                
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
    
    async def run_etl_cycle(self):
        """运行ETL循环"""
        logger.info("开始ETL数据处理循环")
        
        while True:
            try:
                await self.process_order_data()
                await self.generate_analytics()
                
                # 每小时执行一次清理
                current_minute = datetime.now().minute
                if current_minute == 0:
                    await self.cleanup_old_data()
                
                # 等待5分钟后再次执行
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"ETL循环执行失败: {e}")
                await asyncio.sleep(60)  # 发生错误时等待1分钟

async def main():
    """主函数"""
    logger.info("启动ETL数据处理服务")
    
    etl = ETLProcessor()
    await etl.init_connections()
    
    try:
        await etl.run_etl_cycle()
    except KeyboardInterrupt:
        logger.info("ETL服务停止")
    except Exception as e:
        logger.error(f"ETL服务异常停止: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
