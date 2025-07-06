"""
审计服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..dao.log_dao import LogDAO
from ..schemas.log_schema import (
    OperationLogCreate, OperationLogResponse,
    SystemLogCreate, SystemLogResponse,
    SecurityLogCreate, SecurityLogResponse,
    LogSearchRequest, LogStatsResponse,
    AuditReportRequest, AuditReportResponse
)
from ..entity.operation_log import OperationLog
from config.get_db import get_db_session
from exceptions.custom_exception import BusinessException
import json
import uuid


class AuditService:
    """审计服务"""
    
    def __init__(self, log_dao: LogDAO):
        self.log_dao = log_dao
    
    async def log_operation(self, user_id: int, operation: str, resource_type: str,
                           resource_id: str = None, details: str = None,
                           ip_address: str = None, user_agent: str = None,
                           request_data: Dict[str, Any] = None,
                           response_data: Dict[str, Any] = None,
                           duration_ms: int = None, is_success: bool = True,
                           error_message: str = None) -> OperationLogResponse:
        """记录操作日志"""
        try:
            # 获取用户名（这里应该从用户服务获取）
            username = f"user_{user_id}"  # 临时处理
            
            log_data = OperationLogCreate(
                user_id=user_id,
                username=username,
                operation_type=operation,
                resource_type=resource_type,
                resource_id=resource_id,
                operation_details=details or f"{operation} {resource_type}",
                ip_address=ip_address or "127.0.0.1",
                user_agent=user_agent,
                request_data=request_data,
                response_data=response_data,
                duration_ms=duration_ms,
                is_success=is_success,
                error_message=error_message
            )
            
            log_entity = OperationLog(
                user_id=log_data.user_id,
                username=log_data.username,
                operation_type=log_data.operation_type,
                resource_type=log_data.resource_type,
                resource_id=log_data.resource_id,
                operation_details=log_data.operation_details,
                ip_address=log_data.ip_address,
                user_agent=log_data.user_agent,
                request_data=json.dumps(log_data.request_data) if log_data.request_data else None,
                response_data=json.dumps(log_data.response_data) if log_data.response_data else None,
                duration_ms=log_data.duration_ms,
                is_success=log_data.is_success,
                error_message=log_data.error_message
            )
            
            saved_log = await self.log_dao.create_operation_log(log_entity)
            
            # 检查是否需要触发安全告警
            await self._check_security_alerts(log_data)
            
            return OperationLogResponse.from_orm(saved_log)
            
        except Exception as e:
            # 审计日志记录失败不应该影响主要业务流程
            print(f"记录操作日志失败: {str(e)}")
            return None
    
    async def log_system_event(self, level: str, logger_name: str, module: str,
                              function: str, message: str, exception_info: str = None,
                              trace_id: str = None, request_id: str = None,
                              extra_data: Dict[str, Any] = None) -> SystemLogResponse:
        """记录系统日志"""
        try:
            log_data = SystemLogCreate(
                level=level,
                logger_name=logger_name,
                module=module,
                function=function,
                message=message,
                exception_info=exception_info,
                trace_id=trace_id or str(uuid.uuid4()),
                request_id=request_id,
                extra_data=extra_data
            )
            
            saved_log = await self.log_dao.create_system_log(log_data)
            return SystemLogResponse.from_orm(saved_log)
            
        except Exception as e:
            print(f"记录系统日志失败: {str(e)}")
            return None
    
    async def log_security_event(self, event_type: str, severity: str,
                                user_id: int = None, username: str = None,
                                ip_address: str = None, user_agent: str = None,
                                location: str = None, event_details: Dict[str, Any] = None,
                                risk_score: float = 0.0, is_blocked: bool = False,
                                action_taken: str = None) -> SecurityLogResponse:
        """记录安全日志"""
        try:
            log_data = SecurityLogCreate(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                username=username,
                ip_address=ip_address or "127.0.0.1",
                user_agent=user_agent,
                location=location,
                event_details=event_details or {},
                risk_score=risk_score,
                is_blocked=is_blocked,
                action_taken=action_taken
            )
            
            saved_log = await self.log_dao.create_security_log(log_data)
            
            # 高风险事件需要立即处理
            if risk_score >= 0.8 or severity in ['critical', 'high']:
                await self._handle_high_risk_event(log_data)
            
            return SecurityLogResponse.from_orm(saved_log)
            
        except Exception as e:
            print(f"记录安全日志失败: {str(e)}")
            return None
    
    async def search_logs(self, search_request: LogSearchRequest,
                         page: int = 1, size: int = 20) -> Dict[str, Any]:
        """搜索日志"""
        try:
            result = await self.log_dao.search_logs(search_request, page, size)
            return result
        except Exception as e:
            raise BusinessException(f"搜索日志失败: {str(e)}")
    
    async def get_log_statistics(self, start_date: datetime, end_date: datetime) -> LogStatsResponse:
        """获取日志统计信息"""
        try:
            stats = await self.log_dao.get_statistics(start_date, end_date)
            return LogStatsResponse(**stats)
        except Exception as e:
            raise BusinessException(f"获取日志统计失败: {str(e)}")
    
    async def generate_audit_report(self, request: AuditReportRequest) -> AuditReportResponse:
        """生成审计报告"""
        try:
            report_id = str(uuid.uuid4())
            
            # 收集审计数据
            audit_data = await self._collect_audit_data(request)
            
            # 生成报告文件
            file_path = await self._generate_report_file(report_id, audit_data, request.format)
            
            # 计算文件大小
            import os
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # 生成下载链接
            download_url = f"/api/v1/audit/reports/{report_id}/download"
            
            # 设置过期时间（7天后）
            expires_at = datetime.now() + timedelta(days=7)
            
            return AuditReportResponse(
                report_id=report_id,
                report_type=request.report_type,
                file_path=file_path,
                file_size_bytes=file_size,
                generated_at=datetime.now(),
                generated_by=1,  # 这里应该从上下文获取当前用户ID
                download_url=download_url,
                expires_at=expires_at
            )
            
        except Exception as e:
            raise BusinessException(f"生成审计报告失败: {str(e)}")
    
    async def track_data_access(self, user_id: int, data_type: str, data_id: str,
                               access_type: str, sensitive_fields: List[str] = None) -> bool:
        """跟踪数据访问"""
        try:
            details = {
                'data_type': data_type,
                'data_id': data_id,
                'access_type': access_type,
                'sensitive_fields': sensitive_fields or []
            }
            
            await self.log_operation(
                user_id=user_id,
                operation="DATA_ACCESS",
                resource_type=data_type,
                resource_id=data_id,
                details=f"访问{data_type}数据: {access_type}",
                request_data=details
            )
            
            return True
        except Exception as e:
            print(f"跟踪数据访问失败: {str(e)}")
            return False
    
    async def track_sensitive_operation(self, user_id: int, operation: str,
                                       target: str, justification: str,
                                       approval_required: bool = True) -> str:
        """跟踪敏感操作"""
        try:
            operation_id = str(uuid.uuid4())
            
            details = {
                'operation_id': operation_id,
                'target': target,
                'justification': justification,
                'approval_required': approval_required,
                'status': 'pending' if approval_required else 'executed'
            }
            
            await self.log_operation(
                user_id=user_id,
                operation="SENSITIVE_OPERATION",
                resource_type="SECURITY",
                resource_id=operation_id,
                details=f"敏感操作: {operation}",
                request_data=details
            )
            
            # 如果需要审批，记录安全事件
            if approval_required:
                await self.log_security_event(
                    event_type="SENSITIVE_OPERATION_REQUEST",
                    severity="medium",
                    user_id=user_id,
                    event_details=details,
                    risk_score=0.6
                )
            
            return operation_id
            
        except Exception as e:
            raise BusinessException(f"跟踪敏感操作失败: {str(e)}")
    
    async def get_user_activity_timeline(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """获取用户活动时间线"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            activities = await self.log_dao.get_user_activities(user_id, start_date, end_date)
            
            timeline = []
            for activity in activities:
                timeline.append({
                    'timestamp': activity.created_at,
                    'operation': activity.operation_type,
                    'resource': f"{activity.resource_type}:{activity.resource_id}",
                    'details': activity.operation_details,
                    'success': activity.is_success,
                    'ip_address': activity.ip_address
                })
            
            return timeline
            
        except Exception as e:
            raise BusinessException(f"获取用户活动时间线失败: {str(e)}")
    
    async def detect_anomalous_behavior(self, user_id: int) -> Dict[str, Any]:
        """检测异常行为"""
        try:
            # 获取用户最近的活动
            recent_activities = await self.log_dao.get_user_recent_activities(user_id, hours=24)
            
            anomalies = []
            risk_score = 0.0
            
            # 检测异常登录时间
            if await self._detect_unusual_login_time(recent_activities):
                anomalies.append("unusual_login_time")
                risk_score += 0.3
            
            # 检测异常IP地址
            if await self._detect_unusual_ip(user_id, recent_activities):
                anomalies.append("unusual_ip_address")
                risk_score += 0.4
            
            # 检测大量数据访问
            if await self._detect_bulk_data_access(recent_activities):
                anomalies.append("bulk_data_access")
                risk_score += 0.5
            
            # 检测权限提升尝试
            if await self._detect_privilege_escalation(recent_activities):
                anomalies.append("privilege_escalation")
                risk_score += 0.8
            
            return {
                'user_id': user_id,
                'risk_score': min(1.0, risk_score),
                'anomalies': anomalies,
                'recommendations': await self._get_security_recommendations(anomalies),
                'analyzed_at': datetime.now()
            }
            
        except Exception as e:
            raise BusinessException(f"检测异常行为失败: {str(e)}")
    
    async def _check_security_alerts(self, log_data: OperationLogCreate) -> None:
        """检查安全告警"""
        # 检测失败的登录尝试
        if log_data.operation_type == "LOGIN" and not log_data.is_success:
            await self._handle_failed_login(log_data)
        
        # 检测敏感数据访问
        if "DECRYPT" in log_data.operation_type or "VIEW_SENSITIVE" in log_data.operation_type:
            await self._handle_sensitive_data_access(log_data)
    
    async def _handle_high_risk_event(self, log_data: SecurityLogCreate) -> None:
        """处理高风险事件"""
        # 这里应该实现高风险事件的处理逻辑
        # 例如：发送告警、自动封禁、通知管理员等
        pass
    
    async def _collect_audit_data(self, request: AuditReportRequest) -> Dict[str, Any]:
        """收集审计数据"""
        # 这里应该根据报告类型收集相应的数据
        return {
            'operation_logs': [],
            'system_logs': [],
            'security_logs': [],
            'statistics': {}
        }
    
    async def _generate_report_file(self, report_id: str, data: Dict[str, Any], format: str) -> str:
        """生成报告文件"""
        # 这里应该实现报告文件的生成逻辑
        file_path = f"/tmp/audit_report_{report_id}.{format}"
        
        # 创建空文件作为占位符
        with open(file_path, 'w') as f:
            f.write(f"Audit Report {report_id}\n")
        
        return file_path
    
    async def _detect_unusual_login_time(self, activities: List[Any]) -> bool:
        """检测异常登录时间"""
        # 简单实现：检查是否在非工作时间登录
        for activity in activities:
            if activity.operation_type == "LOGIN":
                hour = activity.created_at.hour
                if hour < 6 or hour > 22:  # 非工作时间
                    return True
        return False
    
    async def _detect_unusual_ip(self, user_id: int, activities: List[Any]) -> bool:
        """检测异常IP地址"""
        # 简单实现：检查是否有新的IP地址
        current_ips = set()
        for activity in activities:
            if activity.ip_address:
                current_ips.add(activity.ip_address)
        
        # 这里应该与历史IP进行比较
        return len(current_ips) > 3  # 如果有超过3个不同IP则认为异常
    
    async def _detect_bulk_data_access(self, activities: List[Any]) -> bool:
        """检测大量数据访问"""
        data_access_count = 0
        for activity in activities:
            if "VIEW" in activity.operation_type or "EXPORT" in activity.operation_type:
                data_access_count += 1
        
        return data_access_count > 50  # 超过50次数据访问认为异常
    
    async def _detect_privilege_escalation(self, activities: List[Any]) -> bool:
        """检测权限提升尝试"""
        for activity in activities:
            if not activity.is_success and "ADMIN" in activity.operation_type:
                return True
        return False
    
    async def _get_security_recommendations(self, anomalies: List[str]) -> List[str]:
        """获取安全建议"""
        recommendations = []
        
        if "unusual_login_time" in anomalies:
            recommendations.append("监控非工作时间的登录活动")
        
        if "unusual_ip_address" in anomalies:
            recommendations.append("验证新IP地址的合法性")
        
        if "bulk_data_access" in anomalies:
            recommendations.append("限制批量数据访问权限")
        
        if "privilege_escalation" in anomalies:
            recommendations.append("加强权限管理和监控")
        
        return recommendations
    
    async def _handle_failed_login(self, log_data: OperationLogCreate) -> None:
        """处理失败的登录尝试"""
        # 记录安全事件
        await self.log_security_event(
            event_type="FAILED_LOGIN",
            severity="medium",
            user_id=log_data.user_id,
            username=log_data.username,
            ip_address=log_data.ip_address,
            event_details={'error': log_data.error_message},
            risk_score=0.4
        )
    
    async def _handle_sensitive_data_access(self, log_data: OperationLogCreate) -> None:
        """处理敏感数据访问"""
        # 记录安全事件
        await self.log_security_event(
            event_type="SENSITIVE_DATA_ACCESS",
            severity="high",
            user_id=log_data.user_id,
            username=log_data.username,
            ip_address=log_data.ip_address,
            event_details={
                'resource_type': log_data.resource_type,
                'resource_id': log_data.resource_id
            },
            risk_score=0.7
        )
