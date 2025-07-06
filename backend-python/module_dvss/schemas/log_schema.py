"""
日志管理相关数据模式
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OperationType(str, Enum):
    """操作类型枚举"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    CREATE_ORDER = "create_order"
    UPDATE_ORDER = "update_order"
    DELETE_ORDER = "delete_order"
    ENCRYPT_ORDER = "encrypt_order"
    DECRYPT_ORDER = "decrypt_order"
    CREATE_SHARD = "create_shard"
    RECONSTRUCT_SHARD = "reconstruct_shard"
    VIEW_SENSITIVE_DATA = "view_sensitive_data"
    EXPORT_DATA = "export_data"
    SYSTEM_CONFIG = "system_config"
    BACKUP = "backup"
    RESTORE = "restore"


class OperationLogBase(BaseModel):
    """操作日志基础模型"""
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    operation_type: OperationType = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    operation_details: str = Field(..., description="操作详情")
    ip_address: str = Field(..., description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    request_data: Optional[Dict[str, Any]] = Field(None, description="请求数据")
    response_data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    duration_ms: Optional[int] = Field(None, description="执行时长（毫秒）")
    is_success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")


class OperationLogCreate(OperationLogBase):
    """创建操作日志请求"""
    pass


class OperationLogResponse(OperationLogBase):
    """操作日志响应"""
    id: int = Field(..., description="日志ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class OperationLogList(BaseModel):
    """操作日志列表项"""
    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    operation_type: OperationType = Field(..., description="操作类型")
    resource_type: str = Field(..., description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    operation_details: str = Field(..., description="操作详情")
    ip_address: str = Field(..., description="IP地址")
    is_success: bool = Field(..., description="是否成功")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class SystemLogBase(BaseModel):
    """系统日志基础模型"""
    level: LogLevel = Field(..., description="日志级别")
    logger_name: str = Field(..., description="日志器名称")
    module: str = Field(..., description="模块名称")
    function: str = Field(..., description="函数名称")
    message: str = Field(..., description="日志消息")
    exception_info: Optional[str] = Field(None, description="异常信息")
    trace_id: Optional[str] = Field(None, description="追踪ID")
    request_id: Optional[str] = Field(None, description="请求ID")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="额外数据")


class SystemLogCreate(SystemLogBase):
    """创建系统日志请求"""
    pass


class SystemLogResponse(SystemLogBase):
    """系统日志响应"""
    id: int = Field(..., description="日志ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class LogSearchRequest(BaseModel):
    """日志搜索请求"""
    keyword: Optional[str] = Field(None, description="关键词")
    log_type: Optional[str] = Field(None, description="日志类型", pattern="^(operation|system)$")
    level: Optional[LogLevel] = Field(None, description="日志级别")
    operation_type: Optional[OperationType] = Field(None, description="操作类型")
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[str] = Field(None, description="资源ID")
    ip_address: Optional[str] = Field(None, description="IP地址")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    is_success: Optional[bool] = Field(None, description="是否成功")
    has_error: Optional[bool] = Field(None, description="是否有错误")


class LogStatsRequest(BaseModel):
    """日志统计请求"""
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    group_by: str = Field(default="day", description="分组方式", pattern="^(hour|day|week|month)$")
    metrics: List[str] = Field(default=["count", "success_rate"], description="统计指标")


class LogStatsResponse(BaseModel):
    """日志统计响应"""
    total_logs: int = Field(..., description="总日志数")
    operation_logs: int = Field(..., description="操作日志数")
    system_logs: int = Field(..., description="系统日志数")
    success_count: int = Field(..., description="成功次数")
    error_count: int = Field(..., description="错误次数")
    success_rate: float = Field(..., description="成功率")
    top_operations: List[Dict[str, Any]] = Field(..., description="热门操作")
    top_users: List[Dict[str, Any]] = Field(..., description="活跃用户")
    error_distribution: Dict[str, int] = Field(..., description="错误分布")
    hourly_distribution: List[Dict[str, Any]] = Field(..., description="小时分布")
    daily_trends: List[Dict[str, Any]] = Field(..., description="日趋势")


class SecurityLogBase(BaseModel):
    """安全日志基础模型"""
    event_type: str = Field(..., description="事件类型")
    severity: str = Field(..., description="严重程度")
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    ip_address: str = Field(..., description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    location: Optional[str] = Field(None, description="地理位置")
    event_details: Dict[str, Any] = Field(..., description="事件详情")
    risk_score: float = Field(..., ge=0, le=1, description="风险分值")
    is_blocked: bool = Field(default=False, description="是否被阻止")
    action_taken: Optional[str] = Field(None, description="采取的行动")


class SecurityLogCreate(SecurityLogBase):
    """创建安全日志请求"""
    pass


class SecurityLogResponse(SecurityLogBase):
    """安全日志响应"""
    id: int = Field(..., description="日志ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class AuditReportRequest(BaseModel):
    """审计报告请求"""
    report_type: str = Field(..., description="报告类型")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    user_ids: Optional[List[int]] = Field(None, description="用户ID列表")
    operation_types: Optional[List[OperationType]] = Field(None, description="操作类型列表")
    include_system_logs: bool = Field(default=False, description="是否包含系统日志")
    include_security_logs: bool = Field(default=True, description="是否包含安全日志")
    format: str = Field(default="pdf", description="报告格式", pattern="^(pdf|excel|csv)$")


class AuditReportResponse(BaseModel):
    """审计报告响应"""
    report_id: str = Field(..., description="报告ID")
    report_type: str = Field(..., description="报告类型")
    file_path: str = Field(..., description="文件路径")
    file_size_bytes: int = Field(..., description="文件大小（字节）")
    generated_at: datetime = Field(..., description="生成时间")
    generated_by: int = Field(..., description="生成人ID")
    download_url: str = Field(..., description="下载链接")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class LogRetentionPolicy(BaseModel):
    """日志保留策略"""
    log_type: str = Field(..., description="日志类型")
    retention_days: int = Field(..., ge=1, description="保留天数")
    archive_after_days: Optional[int] = Field(None, description="归档天数")
    compression_enabled: bool = Field(default=True, description="是否启用压缩")
    encryption_enabled: bool = Field(default=False, description="是否启用加密")


class LogExportRequest(BaseModel):
    """日志导出请求"""
    log_type: str = Field(..., description="日志类型")
    filters: Optional[LogSearchRequest] = Field(None, description="过滤条件")
    format: str = Field(default="json", description="导出格式", pattern="^(json|csv|excel)$")
    compress: bool = Field(default=True, description="是否压缩")
    password_protect: bool = Field(default=False, description="是否密码保护")


class LogExportResponse(BaseModel):
    """日志导出响应"""
    export_id: str = Field(..., description="导出ID")
    file_path: str = Field(..., description="文件路径")
    file_size_bytes: int = Field(..., description="文件大小（字节）")
    record_count: int = Field(..., description="记录数量")
    export_time: datetime = Field(..., description="导出时间")
    download_url: str = Field(..., description="下载链接")
    expires_at: datetime = Field(..., description="过期时间")


class LogAlertRule(BaseModel):
    """日志告警规则"""
    rule_name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    log_type: str = Field(..., description="日志类型")
    conditions: Dict[str, Any] = Field(..., description="告警条件")
    threshold: Dict[str, Any] = Field(..., description="阈值配置")
    time_window_minutes: int = Field(..., ge=1, description="时间窗口（分钟）")
    severity: str = Field(..., description="严重程度")
    enabled: bool = Field(default=True, description="是否启用")
    notification_channels: List[str] = Field(..., description="通知渠道")


class LogAlert(BaseModel):
    """日志告警"""
    alert_id: str = Field(..., description="告警ID")
    rule_name: str = Field(..., description="规则名称")
    severity: str = Field(..., description="严重程度")
    message: str = Field(..., description="告警消息")
    triggered_at: datetime = Field(..., description="触发时间")
    acknowledged_at: Optional[datetime] = Field(None, description="确认时间")
    acknowledged_by: Optional[int] = Field(None, description="确认人ID")
    resolved_at: Optional[datetime] = Field(None, description="解决时间")
    status: str = Field(..., description="告警状态")
    details: Dict[str, Any] = Field(..., description="告警详情")


class LogMetrics(BaseModel):
    """日志指标"""
    total_logs_today: int = Field(..., description="今日总日志数")
    error_logs_today: int = Field(..., description="今日错误日志数")
    active_users_today: int = Field(..., description="今日活跃用户数")
    failed_logins_today: int = Field(..., description="今日失败登录数")
    suspicious_activities: int = Field(..., description="可疑活动数")
    average_response_time_ms: float = Field(..., description="平均响应时间（毫秒）")
    top_error_types: List[Dict[str, Any]] = Field(..., description="热门错误类型")
    recent_alerts: List[LogAlert] = Field(..., description="最近告警")
    system_health_score: float = Field(..., description="系统健康分值")
