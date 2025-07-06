"""
日志数据访问层
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..entity.operation_log import OperationLog
from ..schemas.log_schema import LogSearchRequest, SystemLogCreate, SecurityLogCreate
from core.deps import get_db_session


class LogDAO:
    """日志数据访问对象"""
    
    def __init__(self):
        self.session = None
    
    async def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.session:
            self.session = next(get_db_session())
        return self.session
    
    async def create_operation_log(self, log: OperationLog) -> OperationLog:
        """创建操作日志"""
        session = await self.get_session()
        try:
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        except Exception as e:
            session.rollback()
            raise e
    
    async def create_system_log(self, log_data: SystemLogCreate) -> Any:
        """创建系统日志"""
        # 这里应该创建SystemLog实体并保存
        # 暂时返回模拟对象
        class MockSystemLog:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
                self.id = 1
                self.created_at = datetime.now()
        
        return MockSystemLog(**log_data.dict())
    
    async def create_security_log(self, log_data: SecurityLogCreate) -> Any:
        """创建安全日志"""
        # 这里应该创建SecurityLog实体并保存
        # 暂时返回模拟对象
        class MockSecurityLog:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
                self.id = 1
                self.created_at = datetime.now()
        
        return MockSecurityLog(**log_data.dict())
    
    async def get_operation_log_by_id(self, log_id: int) -> Optional[OperationLog]:
        """根据ID获取操作日志"""
        session = await self.get_session()
        return session.query(OperationLog).filter(OperationLog.id == log_id).first()
    
    async def get_operation_logs_list(self, page: int = 1, size: int = 20, 
                                    filters: Optional[Dict[str, Any]] = None,
                                    order_by: str = 'created_at',
                                    order_direction: str = 'desc') -> Tuple[List[OperationLog], int]:
        """获取操作日志列表"""
        session = await self.get_session()
        
        query = session.query(OperationLog)
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(OperationLog, key) and value is not None:
                    if key == 'user_id':
                        query = query.filter(OperationLog.user_id == value)
                    elif key == 'operation_type':
                        query = query.filter(OperationLog.operation_type == value)
                    elif key == 'resource_type':
                        query = query.filter(OperationLog.resource_type == value)
                    elif key == 'is_success':
                        query = query.filter(OperationLog.is_success == value)
                    elif key == 'start_date':
                        query = query.filter(OperationLog.created_at >= value)
                    elif key == 'end_date':
                        query = query.filter(OperationLog.created_at <= value)
                    elif key == 'keyword':
                        # 模糊搜索
                        query = query.filter(
                            or_(
                                OperationLog.username.like(f'%{value}%'),
                                OperationLog.operation_details.like(f'%{value}%'),
                                OperationLog.resource_id.like(f'%{value}%')
                            )
                        )
                    elif key == 'ip_address':
                        query = query.filter(OperationLog.ip_address == value)
        
        # 获取总数
        total = query.count()
        
        # 排序
        if hasattr(OperationLog, order_by):
            if order_direction.lower() == 'desc':
                query = query.order_by(desc(getattr(OperationLog, order_by)))
            else:
                query = query.order_by(asc(getattr(OperationLog, order_by)))
        
        # 分页
        logs = query.offset((page - 1) * size).limit(size).all()
        
        return logs, total
    
    async def search_logs(self, search_request: LogSearchRequest, 
                         page: int = 1, size: int = 20) -> Dict[str, Any]:
        """搜索日志"""
        session = await self.get_session()
        
        # 构建基础查询
        query = session.query(OperationLog)
        
        # 应用搜索条件
        if search_request.keyword:
            query = query.filter(
                or_(
                    OperationLog.username.like(f'%{search_request.keyword}%'),
                    OperationLog.operation_details.like(f'%{search_request.keyword}%'),
                    OperationLog.resource_id.like(f'%{search_request.keyword}%')
                )
            )
        
        if search_request.operation_type:
            query = query.filter(OperationLog.operation_type == search_request.operation_type)
        
        if search_request.user_id:
            query = query.filter(OperationLog.user_id == search_request.user_id)
        
        if search_request.username:
            query = query.filter(OperationLog.username.like(f'%{search_request.username}%'))
        
        if search_request.resource_type:
            query = query.filter(OperationLog.resource_type == search_request.resource_type)
        
        if search_request.resource_id:
            query = query.filter(OperationLog.resource_id == search_request.resource_id)
        
        if search_request.ip_address:
            query = query.filter(OperationLog.ip_address == search_request.ip_address)
        
        if search_request.start_date:
            query = query.filter(OperationLog.created_at >= search_request.start_date)
        
        if search_request.end_date:
            query = query.filter(OperationLog.created_at <= search_request.end_date)
        
        if search_request.is_success is not None:
            query = query.filter(OperationLog.is_success == search_request.is_success)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        logs = query.order_by(desc(OperationLog.created_at)).offset(
            (page - 1) * size
        ).limit(size).all()
        
        return {
            'logs': logs,
            'total': total,
            'page': page,
            'size': size,
            'pages': (total + size - 1) // size
        }
    
    async def get_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取日志统计信息"""
        session = await self.get_session()
        
        # 基础统计
        total_logs = session.query(func.count(OperationLog.id)).filter(
            and_(
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).scalar()
        
        success_count = session.query(func.count(OperationLog.id)).filter(
            and_(
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date,
                OperationLog.is_success == True
            )
        ).scalar()
        
        error_count = total_logs - success_count
        success_rate = (success_count / total_logs * 100) if total_logs > 0 else 0
        
        # 热门操作
        top_operations = session.query(
            OperationLog.operation_type,
            func.count(OperationLog.id).label('count')
        ).filter(
            and_(
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).group_by(OperationLog.operation_type).order_by(
            desc('count')
        ).limit(10).all()
        
        top_operations_list = [
            {'operation': op.operation_type, 'count': op.count}
            for op in top_operations
        ]
        
        # 活跃用户
        top_users = session.query(
            OperationLog.username,
            func.count(OperationLog.id).label('count')
        ).filter(
            and_(
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).group_by(OperationLog.username).order_by(
            desc('count')
        ).limit(10).all()
        
        top_users_list = [
            {'username': user.username, 'count': user.count}
            for user in top_users
        ]
        
        # 错误分布
        error_distribution = {}
        if error_count > 0:
            error_ops = session.query(
                OperationLog.operation_type,
                func.count(OperationLog.id).label('count')
            ).filter(
                and_(
                    OperationLog.created_at >= start_date,
                    OperationLog.created_at <= end_date,
                    OperationLog.is_success == False
                )
            ).group_by(OperationLog.operation_type).all()
            
            error_distribution = {
                op.operation_type: op.count for op in error_ops
            }
        
        # 小时分布
        hourly_distribution = []
        for hour in range(24):
            count = session.query(func.count(OperationLog.id)).filter(
                and_(
                    OperationLog.created_at >= start_date,
                    OperationLog.created_at <= end_date,
                    func.extract('hour', OperationLog.created_at) == hour
                )
            ).scalar()
            
            hourly_distribution.append({
                'hour': hour,
                'count': count
            })
        
        # 日趋势
        daily_trends = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            count = session.query(func.count(OperationLog.id)).filter(
                and_(
                    func.date(OperationLog.created_at) == current_date
                )
            ).scalar()
            
            daily_trends.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': count
            })
            
            current_date += timedelta(days=1)
        
        return {
            'total_logs': total_logs,
            'operation_logs': total_logs,  # 目前只有操作日志
            'system_logs': 0,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': round(success_rate, 2),
            'top_operations': top_operations_list,
            'top_users': top_users_list,
            'error_distribution': error_distribution,
            'hourly_distribution': hourly_distribution,
            'daily_trends': daily_trends
        }
    
    async def get_user_activities(self, user_id: int, start_date: datetime, 
                                 end_date: datetime) -> List[OperationLog]:
        """获取用户活动记录"""
        session = await self.get_session()
        
        return session.query(OperationLog).filter(
            and_(
                OperationLog.user_id == user_id,
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).order_by(desc(OperationLog.created_at)).all()
    
    async def get_user_recent_activities(self, user_id: int, hours: int = 24) -> List[OperationLog]:
        """获取用户最近的活动记录"""
        session = await self.get_session()
        since_time = datetime.now() - timedelta(hours=hours)
        
        return session.query(OperationLog).filter(
            and_(
                OperationLog.user_id == user_id,
                OperationLog.created_at >= since_time
            )
        ).order_by(desc(OperationLog.created_at)).all()
    
    async def get_failed_login_attempts(self, user_id: int = None, ip_address: str = None,
                                       hours: int = 24) -> List[OperationLog]:
        """获取失败的登录尝试"""
        session = await self.get_session()
        since_time = datetime.now() - timedelta(hours=hours)
        
        query = session.query(OperationLog).filter(
            and_(
                OperationLog.operation_type == 'LOGIN',
                OperationLog.is_success == False,
                OperationLog.created_at >= since_time
            )
        )
        
        if user_id:
            query = query.filter(OperationLog.user_id == user_id)
        
        if ip_address:
            query = query.filter(OperationLog.ip_address == ip_address)
        
        return query.order_by(desc(OperationLog.created_at)).all()
    
    async def get_sensitive_operations(self, start_date: datetime, 
                                     end_date: datetime) -> List[OperationLog]:
        """获取敏感操作记录"""
        session = await self.get_session()
        
        sensitive_operations = [
            'DECRYPT_ORDER', 'VIEW_SENSITIVE_DATA', 'EXPORT_DATA',
            'DELETE_USER', 'DELETE_ORDER', 'SYSTEM_CONFIG'
        ]
        
        return session.query(OperationLog).filter(
            and_(
                OperationLog.operation_type.in_(sensitive_operations),
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).order_by(desc(OperationLog.created_at)).all()
    
    async def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """清理旧日志"""
        session = await self.get_session()
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            deleted_count = session.query(OperationLog).filter(
                OperationLog.created_at < cutoff_date
            ).delete()
            
            session.commit()
            return deleted_count
        except Exception as e:
            session.rollback()
            raise e
    
    async def get_operation_counts_by_user(self, start_date: datetime, 
                                         end_date: datetime) -> List[Dict[str, Any]]:
        """按用户统计操作次数"""
        session = await self.get_session()
        
        results = session.query(
            OperationLog.user_id,
            OperationLog.username,
            func.count(OperationLog.id).label('total_operations'),
            func.sum(
                func.case([(OperationLog.is_success == True, 1)], else_=0)
            ).label('successful_operations'),
            func.sum(
                func.case([(OperationLog.is_success == False, 1)], else_=0)
            ).label('failed_operations')
        ).filter(
            and_(
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).group_by(
            OperationLog.user_id, OperationLog.username
        ).order_by(desc('total_operations')).all()
        
        return [
            {
                'user_id': result.user_id,
                'username': result.username,
                'total_operations': result.total_operations,
                'successful_operations': result.successful_operations,
                'failed_operations': result.failed_operations,
                'success_rate': (result.successful_operations / result.total_operations * 100) 
                              if result.total_operations > 0 else 0
            }
            for result in results
        ]
    
    async def get_resource_access_stats(self, resource_type: str, 
                                       start_date: datetime, 
                                       end_date: datetime) -> Dict[str, Any]:
        """获取资源访问统计"""
        session = await self.get_session()
        
        total_access = session.query(func.count(OperationLog.id)).filter(
            and_(
                OperationLog.resource_type == resource_type,
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).scalar()
        
        unique_users = session.query(func.count(func.distinct(OperationLog.user_id))).filter(
            and_(
                OperationLog.resource_type == resource_type,
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).scalar()
        
        top_accessed_resources = session.query(
            OperationLog.resource_id,
            func.count(OperationLog.id).label('access_count')
        ).filter(
            and_(
                OperationLog.resource_type == resource_type,
                OperationLog.created_at >= start_date,
                OperationLog.created_at <= end_date
            )
        ).group_by(OperationLog.resource_id).order_by(
            desc('access_count')
        ).limit(10).all()
        
        return {
            'resource_type': resource_type,
            'total_access': total_access,
            'unique_users': unique_users,
            'top_accessed_resources': [
                {
                    'resource_id': resource.resource_id,
                    'access_count': resource.access_count
                }
                for resource in top_accessed_resources
            ]
        }
