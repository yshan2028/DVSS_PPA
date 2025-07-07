"""
日志管理控制器
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from module_dvss.dao.log_dao import LogDAO
from module_dvss.entity.user import User
from module_dvss.schemas.common_schema import ApiResponse, PageResponse
from module_dvss.schemas.log_schema import (
    AuditReportRequest,
    AuditReportResponse,
    LogSearchRequest,
    LogStatsResponse,
)
from module_dvss.service.audit_service import AuditService
from utils.response_util import ResponseUtil

router = APIRouter(prefix='/api/v1/logs', tags=['日志管理'])


@router.get('', response_model=PageResponse)
async def get_logs(
    page: int = Query(1, ge=1, description='页码'),
    size: int = Query(20, ge=1, le=100, description='每页大小'),
    log_type: Optional[str] = Query(None, description='日志类型'),
    operation_type: Optional[str] = Query(None, description='操作类型'),
    user_id: Optional[int] = Query(None, description='用户ID'),
    start_date: Optional[datetime] = Query(None, description='开始日期'),
    end_date: Optional[datetime] = Query(None, description='结束日期'),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取系统操作日志列表"""
    try:
        log_dao = LogDAO(db)
        service = AuditService(log_dao)
        search_request = LogSearchRequest(
            keyword=None,
            log_type=log_type,
            level=None,
            operation_type=operation_type,
            user_id=user_id,
            username=None,
            resource_type=None,
            resource_id=None,
            ip_address=None,
            start_date=start_date,
            end_date=end_date,
            is_success=None,
            has_error=None,
            page=page,
            size=size,
        )
        result = await service.search_logs(search_request, page, size)
        return ResponseUtil.success(data=result, message='获取日志列表成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取日志列表失败: {str(e)}')


@router.post('/search', response_model=PageResponse)
async def search_logs(
    request: LogSearchRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """高级日志搜索"""
    try:
        log_dao = LogDAO(db)
        service = AuditService(log_dao)
        result = await service.search_logs(request, request.page or 1, request.size or 20)
        return ResponseUtil.success(data=result, message='搜索日志成功')
    except Exception as e:
        return ResponseUtil.error(message=f'搜索日志失败: {str(e)}')


@router.get('/stats', response_model=ApiResponse[LogStatsResponse])
async def get_log_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取日志统计信息"""
    try:
        log_dao = LogDAO(db)
        service = AuditService(log_dao)
        # 使用默认的30天统计
        from datetime import datetime, timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        stats = await service.get_log_statistics(start_date, end_date)
        return ResponseUtil.success(data=stats, message='获取日志统计成功')
    except Exception as e:
        return ResponseUtil.error(message=f'获取日志统计失败: {str(e)}')


@router.post('/audit-report', response_model=ApiResponse[AuditReportResponse])
async def generate_audit_report(
    request: AuditReportRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """生成审计报告"""
    try:
        log_dao = LogDAO(db)
        service = AuditService(log_dao)
        report = await service.generate_audit_report(request)
        return ResponseUtil.success(data=report, message='审计报告生成成功')
    except Exception as e:
        return ResponseUtil.error(message=f'生成审计报告失败: {str(e)}')
