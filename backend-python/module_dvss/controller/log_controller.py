"""
日志管理控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta

from ..schemas.log_schema import (
    OperationLogResponse, LogSearchRequest, LogStatsResponse,
    AuditReportRequest, AuditReportResponse
)
from ..schemas.common_schema import ApiResponse, PageResponse
from ..service.audit_service import AuditService
from core.deps import get_audit_service, get_current_user
from utils.response_util import success_response, error_response

router = APIRouter(prefix="/api/v1/logs", tags=["日志管理"])


@router.get("", response_model=ApiResponse[PageResponse[OperationLogResponse]])
async def get_logs(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    log_type: Optional[str] = Query(None, description="日志类型"),
    operation_type: Optional[str] = Query(None, description="操作类型"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    service: AuditService = Depends(get_audit_service)
):
    """获取日志列表"""
    try:
        search_request = LogSearchRequest(
            log_type=log_type,
            operation_type=operation_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        result = await service.search_logs(search_request, page, size)
        return success_response(data=result, message="获取日志列表成功")
    except Exception as e:
        return error_response(message=f"获取日志列表失败: {str(e)}")


@router.post("/search", response_model=ApiResponse[PageResponse[OperationLogResponse]])
async def search_logs(
    search_request: LogSearchRequest,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    service: AuditService = Depends(get_audit_service)
):
    """搜索日志"""
    try:
        result = await service.search_logs(search_request, page, size)
        return success_response(data=result, message="搜索日志成功")
    except Exception as e:
        return error_response(message=f"搜索日志失败: {str(e)}")


@router.get("/stats", response_model=ApiResponse[LogStatsResponse])
async def get_log_statistics(
    start_date: datetime = Query(..., description="开始日期"),
    end_date: datetime = Query(..., description="结束日期"),
    service: AuditService = Depends(get_audit_service)
):
    """获取日志统计信息"""
    try:
        stats = await service.get_log_statistics(start_date, end_date)
        return success_response(data=stats, message="获取日志统计成功")
    except Exception as e:
        return error_response(message=f"获取日志统计失败: {str(e)}")


@router.post("/audit-report", response_model=ApiResponse[AuditReportResponse])
async def generate_audit_report(
    request: AuditReportRequest,
    current_user = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service)
):
    """生成审计报告"""
    try:
        report = await service.generate_audit_report(request)
        return success_response(data=report, message="审计报告生成成功")
    except Exception as e:
        return error_response(message=f"生成审计报告失败: {str(e)}")


@router.get("/user/{user_id}/activity", response_model=ApiResponse[List[dict]])
async def get_user_activity_timeline(
    user_id: int,
    days: int = Query(30, ge=1, le=90, description="天数"),
    service: AuditService = Depends(get_audit_service)
):
    """获取用户活动时间线"""
    try:
        timeline = await service.get_user_activity_timeline(user_id, days)
        return success_response(data=timeline, message="获取用户活动时间线成功")
    except Exception as e:
        return error_response(message=f"获取用户活动时间线失败: {str(e)}")


@router.get("/user/{user_id}/anomaly", response_model=ApiResponse[dict])
async def detect_user_anomalous_behavior(
    user_id: int,
    service: AuditService = Depends(get_audit_service)
):
    """检测用户异常行为"""
    try:
        result = await service.detect_anomalous_behavior(user_id)
        return success_response(data=result, message="异常行为检测完成")
    except Exception as e:
        return error_response(message=f"异常行为检测失败: {str(e)}")


@router.post("/track/data-access", response_model=ApiResponse[bool])
async def track_data_access(
    data_type: str,
    data_id: str,
    access_type: str,
    sensitive_fields: Optional[List[str]] = None,
    current_user = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service)
):
    """跟踪数据访问"""
    try:
        result = await service.track_data_access(
            user_id=current_user.id,
            data_type=data_type,
            data_id=data_id,
            access_type=access_type,
            sensitive_fields=sensitive_fields
        )
        return success_response(data=result, message="数据访问跟踪成功")
    except Exception as e:
        return error_response(message=f"数据访问跟踪失败: {str(e)}")


@router.post("/track/sensitive-operation", response_model=ApiResponse[str])
async def track_sensitive_operation(
    operation: str,
    target: str,
    justification: str,
    approval_required: bool = True,
    current_user = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service)
):
    """跟踪敏感操作"""
    try:
        operation_id = await service.track_sensitive_operation(
            user_id=current_user.id,
            operation=operation,
            target=target,
            justification=justification,
            approval_required=approval_required
        )
        return success_response(data=operation_id, message="敏感操作跟踪成功")
    except Exception as e:
        return error_response(message=f"敏感操作跟踪失败: {str(e)}")


@router.get("/recent-errors", response_model=ApiResponse[List[dict]])
async def get_recent_errors(
    hours: int = Query(24, ge=1, le=168, description="小时数"),
    limit: int = Query(50, ge=1, le=200, description="限制数量"),
    service: AuditService = Depends(get_audit_service)
):
    """获取最近的错误日志"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        search_request = LogSearchRequest(
            start_date=start_date,
            end_date=end_date,
            is_success=False
        )
        
        result = await service.search_logs(search_request, 1, limit)
        return success_response(data=result['logs'], message="获取错误日志成功")
    except Exception as e:
        return error_response(message=f"获取错误日志失败: {str(e)}")


@router.get("/security-events", response_model=ApiResponse[List[dict]])
async def get_security_events(
    days: int = Query(7, ge=1, le=30, description="天数"),
    severity: Optional[str] = Query(None, description="严重程度"),
    service: AuditService = Depends(get_audit_service)
):
    """获取安全事件"""
    try:
        # 这里应该有专门的安全日志查询方法
        # 暂时返回空列表
        return success_response(data=[], message="获取安全事件成功")
    except Exception as e:
        return error_response(message=f"获取安全事件失败: {str(e)}")


@router.delete("/cleanup", response_model=ApiResponse[int])
async def cleanup_old_logs(
    days_to_keep: int = Query(90, ge=30, le=365, description="保留天数"),
    current_user = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service)
):
    """清理旧日志"""
    try:
        # 这里应该检查用户权限
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 实际的清理逻辑应该在service层实现
        deleted_count = 0  # 暂时返回0
        
        return success_response(data=deleted_count, message=f"清理了 {deleted_count} 条旧日志")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"清理旧日志失败: {str(e)}")


@router.get("/export", response_model=ApiResponse[dict])
async def export_logs(
    format: str = Query("json", description="导出格式"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    current_user = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service)
):
    """导出日志"""
    try:
        # 这里应该实现日志导出逻辑
        export_info = {
            'export_id': 'temp_export_id',
            'download_url': '/api/v1/logs/download/temp_export_id',
            'format': format,
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return success_response(data=export_info, message="日志导出请求已提交")
    except Exception as e:
        return error_response(message=f"导出日志失败: {str(e)}")


@router.get("/metrics", response_model=ApiResponse[dict])
async def get_log_metrics(
    service: AuditService = Depends(get_audit_service)
):
    """获取日志指标"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        stats = await service.get_log_statistics(start_date, end_date)
        
        metrics = {
            'total_logs_today': stats.total_logs,
            'error_logs_today': stats.error_count,
            'success_rate': stats.success_rate,
            'top_operations': stats.top_operations[:5],
            'recent_trends': stats.daily_trends[-7:]  # 最近7天
        }
        
        return success_response(data=metrics, message="获取日志指标成功")
    except Exception as e:
        return error_response(message=f"获取日志指标失败: {str(e)}")
