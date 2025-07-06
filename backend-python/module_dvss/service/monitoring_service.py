"""
系统监控服务层
Service Layer - 处理系统监控和性能指标相关的业务逻辑
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import psutil
import time

from module_dvss.dao.user_dao import UserDao
from module_dvss.dao.order_dao import OrderDao
from module_dvss.dao.shard_dao import ShardDao
from module_dvss.dao.log_dao import LogDao
from utils.log_util import LogUtil

logger = LogUtil.get_logger("monitoring_service")

class MonitoringService:
    """系统监控服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_dao = UserDao(db)
        self.order_dao = OrderDao(db)
        self.shard_dao = ShardDao(db)
        self.log_dao = LogDao(db)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            Dict: 系统状态信息
        """
        try:
            # 系统资源使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 数据库统计
            user_count = await self.user_dao.get_total_count()
            order_count = await self.order_dao.get_total_count()
            shard_count = await self.shard_dao.get_total_count()
            
            # 今日活动统计
            today = datetime.now().date()
            today_logs = await self.log_dao.get_logs_by_date(today)
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used": memory.used,
                    "memory_total": memory.total,
                    "disk_percent": disk.percent,
                    "disk_used": disk.used,
                    "disk_total": disk.total,
                    "uptime": self._get_uptime()
                },
                "database": {
                    "user_count": user_count,
                    "order_count": order_count,
                    "shard_count": shard_count
                },
                "activity": {
                    "today_operations": len(today_logs),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            raise
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取性能指标
        
        Args:
            hours: 统计时间范围（小时）
            
        Returns:
            Dict: 性能指标数据
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 获取时间范围内的操作日志
            logs = await self.log_dao.get_logs_by_time_range(start_time, end_time)
            
            # 统计各种操作的数量
            operation_stats = {}
            for log in logs:
                operation = log.operation
                if operation not in operation_stats:
                    operation_stats[operation] = 0
                operation_stats[operation] += 1
            
            # 统计每小时的活动量
            hourly_stats = {}
            for log in logs:
                hour = log.created_at.strftime('%Y-%m-%d %H:00')
                if hour not in hourly_stats:
                    hourly_stats[hour] = 0
                hourly_stats[hour] += 1
            
            return {
                "operation_stats": operation_stats,
                "hourly_stats": hourly_stats,
                "total_operations": len(logs),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                }
            }
            
        except Exception as e:
            logger.error(f"获取性能指标失败: {str(e)}")
            raise
    
    async def get_security_alerts(self) -> List[Dict[str, Any]]:
        """
        获取安全告警
        
        Returns:
            List: 安全告警列表
        """
        try:
            alerts = []
            
            # 检查异常登录活动
            recent_failed_logins = await self._check_failed_logins()
            if recent_failed_logins:
                alerts.append({
                    "type": "authentication",
                    "level": "warning",
                    "message": f"检测到 {recent_failed_logins} 次失败登录尝试",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 检查系统资源使用
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            if cpu_percent > 80:
                alerts.append({
                    "type": "resource",
                    "level": "warning",
                    "message": f"CPU使用率过高: {cpu_percent}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            if memory_percent > 80:
                alerts.append({
                    "type": "resource",
                    "level": "warning",
                    "message": f"内存使用率过高: {memory_percent}%",
                    "timestamp": datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"获取安全告警失败: {str(e)}")
            return []
    
    async def _check_failed_logins(self) -> int:
        """检查最近的失败登录次数"""
        try:
            # 获取最近1小时的失败登录日志
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            failed_logins = await self.log_dao.get_logs_by_operation_and_time(
                operation="login_failed",
                start_time=start_time,
                end_time=end_time
            )
            
            return len(failed_logins)
            
        except Exception as e:
            logger.error(f"检查失败登录失败: {str(e)}")
            return 0
    
    def _get_uptime(self) -> str:
        """获取系统运行时间"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = uptime_seconds / 3600
            
            if uptime_hours < 24:
                return f"{uptime_hours:.1f} 小时"
            else:
                uptime_days = uptime_hours / 24
                return f"{uptime_days:.1f} 天"
                
        except Exception:
            return "未知"
