"""
日期时间工具类
提供日期时间处理相关的工具方法
"""

from datetime import datetime, timedelta, date
from typing import Optional, Union, Tuple
import calendar


class DateUtil:
    """日期时间工具类"""

    # 常用日期格式
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    TIME_FORMAT = '%H:%M:%S'
    ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'

    @staticmethod
    def now() -> datetime:
        """获取当前时间"""
        return datetime.now()

    @staticmethod
    def today() -> date:
        """获取今天日期"""
        return date.today()

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = DATETIME_FORMAT) -> str:
        """格式化日期时间"""
        if not isinstance(dt, datetime):
            return ''
        return dt.strftime(format_str)

    @staticmethod
    def format_date(d: date, format_str: str = DATE_FORMAT) -> str:
        """格式化日期"""
        if not isinstance(d, date):
            return ''
        return d.strftime(format_str)

    @staticmethod
    def parse_datetime(date_str: str, format_str: str = DATETIME_FORMAT) -> Optional[datetime]:
        """解析日期时间字符串"""
        try:
            return datetime.strptime(date_str, format_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def parse_date(date_str: str, format_str: str = DATE_FORMAT) -> Optional[date]:
        """解析日期字符串"""
        try:
            return datetime.strptime(date_str, format_str).date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def to_timestamp(dt: datetime) -> int:
        """转换为时间戳（秒）"""
        return int(dt.timestamp())

    @staticmethod
    def to_timestamp_ms(dt: datetime) -> int:
        """转换为毫秒时间戳"""
        return int(dt.timestamp() * 1000)

    @staticmethod
    def from_timestamp(timestamp: Union[int, float]) -> datetime:
        """从时间戳创建datetime对象"""
        # 如果是毫秒时间戳，转换为秒
        if timestamp > 10**10:
            timestamp = timestamp / 1000
        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def add_days(dt: Union[datetime, date], days: int) -> Union[datetime, date]:
        """增加天数"""
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """增加小时"""
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """增加分钟"""
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def add_seconds(dt: datetime, seconds: int) -> datetime:
        """增加秒数"""
        return dt + timedelta(seconds=seconds)

    @staticmethod
    def diff_days(dt1: Union[datetime, date], dt2: Union[datetime, date]) -> int:
        """计算日期差（天数）"""
        if isinstance(dt1, datetime):
            dt1 = dt1.date()
        if isinstance(dt2, datetime):
            dt2 = dt2.date()
        return (dt1 - dt2).days

    @staticmethod
    def diff_seconds(dt1: datetime, dt2: datetime) -> int:
        """计算时间差（秒数）"""
        return int((dt1 - dt2).total_seconds())

    @staticmethod
    def is_same_day(dt1: Union[datetime, date], dt2: Union[datetime, date]) -> bool:
        """判断是否为同一天"""
        if isinstance(dt1, datetime):
            dt1 = dt1.date()
        if isinstance(dt2, datetime):
            dt2 = dt2.date()
        return dt1 == dt2

    @staticmethod
    def is_weekend(dt: Union[datetime, date]) -> bool:
        """判断是否为周末"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday

    @staticmethod
    def is_workday(dt: Union[datetime, date]) -> bool:
        """判断是否为工作日"""
        return not DateUtil.is_weekend(dt)

    @staticmethod
    def get_week_start(dt: Union[datetime, date]) -> date:
        """获取本周开始日期（周一）"""
        if isinstance(dt, datetime):
            dt = dt.date()
        days_since_monday = dt.weekday()
        return dt - timedelta(days=days_since_monday)

    @staticmethod
    def get_week_end(dt: Union[datetime, date]) -> date:
        """获取本周结束日期（周日）"""
        week_start = DateUtil.get_week_start(dt)
        return week_start + timedelta(days=6)

    @staticmethod
    def get_month_start(dt: Union[datetime, date]) -> date:
        """获取本月开始日期"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.replace(day=1)

    @staticmethod
    def get_month_end(dt: Union[datetime, date]) -> date:
        """获取本月结束日期"""
        if isinstance(dt, datetime):
            dt = dt.date()
        # 获取下个月第一天，然后减去一天
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        return next_month - timedelta(days=1)

    @staticmethod
    def get_year_start(dt: Union[datetime, date]) -> date:
        """获取本年开始日期"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.replace(month=1, day=1)

    @staticmethod
    def get_year_end(dt: Union[datetime, date]) -> date:
        """获取本年结束日期"""
        if isinstance(dt, datetime):
            dt = dt.date()
        return dt.replace(month=12, day=31)

    @staticmethod
    def get_quarter_start(dt: Union[datetime, date]) -> date:
        """获取季度开始日期"""
        if isinstance(dt, datetime):
            dt = dt.date()
        
        quarter_month = ((dt.month - 1) // 3) * 3 + 1
        return dt.replace(month=quarter_month, day=1)

    @staticmethod
    def get_quarter_end(dt: Union[datetime, date]) -> date:
        """获取季度结束日期"""
        quarter_start = DateUtil.get_quarter_start(dt)
        # 加3个月，然后减去一天
        if quarter_start.month >= 10:
            next_quarter = quarter_start.replace(year=quarter_start.year + 1, month=(quarter_start.month + 3) % 12)
        else:
            next_quarter = quarter_start.replace(month=quarter_start.month + 3)
        return next_quarter - timedelta(days=1)

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """获取指定月份的天数"""
        return calendar.monthrange(year, month)[1]

    @staticmethod
    def get_age(birth_date: date, reference_date: Optional[date] = None) -> int:
        """计算年龄"""
        if reference_date is None:
            reference_date = DateUtil.today()
        
        age = reference_date.year - birth_date.year
        
        # 检查是否已过生日
        if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age

    @staticmethod
    def format_relative_time(dt: datetime, reference_dt: Optional[datetime] = None) -> str:
        """格式化相对时间"""
        if reference_dt is None:
            reference_dt = DateUtil.now()
        
        diff = reference_dt - dt
        seconds = int(diff.total_seconds())
        
        if seconds < 0:
            return "未来时间"
        elif seconds < 60:
            return f"{seconds}秒前"
        elif seconds < 3600:
            return f"{seconds // 60}分钟前"
        elif seconds < 86400:
            return f"{seconds // 3600}小时前"
        elif seconds < 604800:  # 7天
            return f"{seconds // 86400}天前"
        else:
            return DateUtil.format_datetime(dt, DateUtil.DATE_FORMAT)

    @staticmethod
    def get_date_range(range_type: str, reference_date: Optional[date] = None) -> Tuple[date, date]:
        """获取日期范围"""
        if reference_date is None:
            reference_date = DateUtil.today()
        
        if range_type == 'today':
            return reference_date, reference_date
        elif range_type == 'yesterday':
            yesterday = reference_date - timedelta(days=1)
            return yesterday, yesterday
        elif range_type == 'this_week':
            return DateUtil.get_week_start(reference_date), DateUtil.get_week_end(reference_date)
        elif range_type == 'last_week':
            last_week = reference_date - timedelta(days=7)
            return DateUtil.get_week_start(last_week), DateUtil.get_week_end(last_week)
        elif range_type == 'this_month':
            return DateUtil.get_month_start(reference_date), DateUtil.get_month_end(reference_date)
        elif range_type == 'last_month':
            if reference_date.month == 1:
                last_month = reference_date.replace(year=reference_date.year - 1, month=12)
            else:
                last_month = reference_date.replace(month=reference_date.month - 1)
            return DateUtil.get_month_start(last_month), DateUtil.get_month_end(last_month)
        elif range_type == 'this_year':
            return DateUtil.get_year_start(reference_date), DateUtil.get_year_end(reference_date)
        elif range_type == 'last_year':
            last_year = reference_date.replace(year=reference_date.year - 1)
            return DateUtil.get_year_start(last_year), DateUtil.get_year_end(last_year)
        elif range_type == 'last_7_days':
            start_date = reference_date - timedelta(days=6)
            return start_date, reference_date
        elif range_type == 'last_30_days':
            start_date = reference_date - timedelta(days=29)
            return start_date, reference_date
        elif range_type == 'last_90_days':
            start_date = reference_date - timedelta(days=89)
            return start_date, reference_date
        else:
            raise ValueError(f"不支持的日期范围类型: {range_type}")

    @staticmethod
    def is_valid_date_range(start_date: Union[datetime, date], 
                          end_date: Union[datetime, date]) -> bool:
        """验证日期范围是否有效"""
        return start_date <= end_date

    @staticmethod
    def get_business_days(start_date: date, end_date: date) -> int:
        """计算工作日天数（排除周末）"""
        if start_date > end_date:
            return 0
        
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if DateUtil.is_workday(current_date):
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days

    @staticmethod
    def get_next_business_day(dt: date) -> date:
        """获取下一个工作日"""
        next_day = dt + timedelta(days=1)
        while DateUtil.is_weekend(next_day):
            next_day += timedelta(days=1)
        return next_day

    @staticmethod
    def timezone_aware_now(timezone_name: str = 'Asia/Shanghai') -> datetime:
        """获取带时区的当前时间"""
        try:
            from zoneinfo import ZoneInfo
            return datetime.now(ZoneInfo(timezone_name))
        except ImportError:
            # 如果zoneinfo不可用，返回本地时间
            return datetime.now()

    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """转换时区"""
        try:
            from zoneinfo import ZoneInfo
            
            if dt.tzinfo is None:
                # 如果没有时区信息，假设是from_tz时区
                dt = dt.replace(tzinfo=ZoneInfo(from_tz))
            
            return dt.astimezone(ZoneInfo(to_tz))
        except ImportError:
            # 如果zoneinfo不可用，返回原时间
            return dt
