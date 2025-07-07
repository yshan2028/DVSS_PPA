"""
通用工具类
提供常用的工具方法
"""

import hashlib
import json
import uuid

from datetime import datetime
from typing import Any, Dict, List


class CommonUtil:
    """通用工具类"""

    @staticmethod
    def generate_uuid() -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """生成短ID"""
        import secrets
        import string

        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def calculate_md5(text: str) -> str:
        """计算字符串MD5值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    @staticmethod
    def calculate_sha256(text: str) -> str:
        """计算字符串SHA256值"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def safe_json_loads(json_str: str, default: Any = None) -> Any:
        """安全的JSON解析"""
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default

    @staticmethod
    def safe_json_dumps(obj: Any, default: str = '{}') -> str:
        """安全的JSON序列化"""
        try:
            return json.dumps(obj, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def is_empty(value: Any) -> bool:
        """判断值是否为空"""
        if value is None:
            return True
        if isinstance(value, (str, list, dict, tuple)):
            return len(value) == 0
        return False

    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """安全获取字典值"""
        try:
            return data.get(key, default)
        except (AttributeError, TypeError):
            return default

    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f'{parent_key}{sep}{k}' if parent_key else k
            if isinstance(v, dict):
                items.extend(CommonUtil.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = CommonUtil.deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """将列表分块"""
        return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """移除字典中的None值"""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def convert_to_snake_case(camel_str: str) -> str:
        """驼峰转下划线"""
        import re

        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def convert_to_camel_case(snake_str: str) -> str:
        """下划线转驼峰"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])

    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = '*', start_visible: int = 2, end_visible: int = 2) -> str:
        """脱敏敏感数据"""
        if not data or len(data) <= start_visible + end_visible:
            return mask_char * len(data) if data else ''

        start = data[:start_visible]
        end = data[-end_visible:] if end_visible > 0 else ''
        middle = mask_char * (len(data) - start_visible - end_visible)

        return start + middle + end

    @staticmethod
    def parse_size(size_str: str) -> int:
        """解析大小字符串，返回字节数"""
        size_str = size_str.strip().upper()

        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024**2,
            'GB': 1024**3,
            'TB': 1024**4,
        }

        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    number = float(size_str[: -len(suffix)])
                    return int(number * multiplier)
                except ValueError:
                    break

        # 如果没有后缀，假设是字节
        try:
            return int(size_str)
        except ValueError:
            return 0

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return '0B'

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.1f}{unit}'
            size_bytes /= 1024.0

        return f'{size_bytes:.1f}PB'

    @staticmethod
    def get_client_ip(headers: Dict[str, str]) -> str:
        """从请求头获取客户端IP"""
        # 尝试从代理头获取真实IP
        for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP']:
            if header in headers:
                ip = headers[header].split(',')[0].strip()
                if ip:
                    return ip

        # 返回默认值
        return headers.get('Host', 'unknown')

    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
        """截断字符串"""
        if len(text) <= max_length:
            return text

        if len(suffix) >= max_length:
            return suffix[:max_length]

        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def validate_json(json_str: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def current_timestamp() -> int:
        """获取当前时间戳（毫秒）"""
        return int(datetime.now().timestamp() * 1000)

    @staticmethod
    def format_timestamp(timestamp: int | float, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        """格式化时间戳"""
        try:
            # 如果是毫秒时间戳，转换为秒
            if timestamp > 10**10:
                timestamp = timestamp / 1000

            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime(format_str)
        except (ValueError, OSError):
            return ''

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除不安全字符"""
        import re

        # 移除或替换不安全字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除控制字符
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        # 限制长度
        return sanitized[:255]

    @staticmethod
    def batch_process(items: List[Any], batch_size: int, processor_func) -> List[Any]:
        """批量处理数据"""
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            batch_results = processor_func(batch)
            if isinstance(batch_results, list):
                results.extend(batch_results)
            else:
                results.append(batch_results)
        return results
