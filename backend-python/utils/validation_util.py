"""
数据验证工具类
提供各种数据验证方法
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class ValidationUtil:
    """验证工具类"""

    # 正则表达式模式
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')  # 中国手机号
    ID_CARD_PATTERN = re.compile(r'^\d{17}[\dXx]$')  # 中国身份证
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        if not email or not isinstance(email, str):
            return False
        return bool(ValidationUtil.EMAIL_PATTERN.match(email.strip()))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证手机号格式"""
        if not phone or not isinstance(phone, str):
            return False
        return bool(ValidationUtil.PHONE_PATTERN.match(phone.strip()))

    @staticmethod
    def is_valid_id_card(id_card: str) -> bool:
        """验证身份证号"""
        if not id_card or not isinstance(id_card, str):
            return False
        
        id_card = id_card.strip().upper()
        if not ValidationUtil.ID_CARD_PATTERN.match(id_card):
            return False
        
        # 验证校验位
        try:
            weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
            
            sum_val = sum(int(id_card[i]) * weights[i] for i in range(17))
            check_code = check_codes[sum_val % 11]
            
            return id_card[17] == check_code
        except (ValueError, IndexError):
            return False

    @staticmethod
    def is_valid_username(username: str) -> bool:
        """验证用户名格式"""
        if not username or not isinstance(username, str):
            return False
        return bool(ValidationUtil.USERNAME_PATTERN.match(username.strip()))

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        if not password or not isinstance(password, str):
            return False, "密码不能为空"
        
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        if len(password) > 128:
            return False, "密码长度不能超过128位"
        
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        
        if not re.search(r'[@$!%*?&]', password):
            return False, "密码必须包含特殊字符(@$!%*?&)"
        
        return True, "密码强度符合要求"

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        if not url or not isinstance(url, str):
            return False
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url.strip()))

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """验证IP地址格式"""
        if not ip or not isinstance(ip, str):
            return False
        
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_date(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
        """验证日期格式"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str.strip(), format_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """验证JSON格式"""
        if not json_str or not isinstance(json_str, str):
            return False
        
        try:
            import json
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def validate_number_range(value: Union[int, float], min_val: Optional[Union[int, float]] = None,
                            max_val: Optional[Union[int, float]] = None) -> Tuple[bool, str]:
        """验证数值范围"""
        try:
            num_val = float(value)
        except (TypeError, ValueError):
            return False, "值必须是数字"
        
        if min_val is not None and num_val < min_val:
            return False, f"值不能小于{min_val}"
        
        if max_val is not None and num_val > max_val:
            return False, f"值不能大于{max_val}"
        
        return True, "数值范围正确"

    @staticmethod
    def validate_string_length(value: str, min_len: Optional[int] = None,
                             max_len: Optional[int] = None) -> Tuple[bool, str]:
        """验证字符串长度"""
        if not isinstance(value, str):
            return False, "值必须是字符串"
        
        length = len(value)
        
        if min_len is not None and length < min_len:
            return False, f"长度不能少于{min_len}个字符"
        
        if max_len is not None and length > max_len:
            return False, f"长度不能超过{max_len}个字符"
        
        return True, "字符串长度正确"

    @staticmethod
    def validate_in_choices(value: Any, choices: List[Any]) -> Tuple[bool, str]:
        """验证值是否在选择列表中"""
        if value not in choices:
            return False, f"值必须是以下之一: {', '.join(map(str, choices))}"
        
        return True, "值在允许范围内"

    @staticmethod
    def validate_regex_pattern(value: str, pattern: str) -> Tuple[bool, str]:
        """使用正则表达式验证值"""
        if not isinstance(value, str):
            return False, "值必须是字符串"
        
        try:
            if not re.match(pattern, value):
                return False, "值格式不正确"
            return True, "格式正确"
        except re.error:
            return False, "正则表达式格式错误"

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> Tuple[bool, str]:
        """验证文件扩展名"""
        if not filename or not isinstance(filename, str):
            return False, "文件名不能为空"
        
        if '.' not in filename:
            return False, "文件名必须包含扩展名"
        
        extension = filename.rsplit('.', 1)[1].lower()
        allowed_lower = [ext.lower() for ext in allowed_extensions]
        
        if extension not in allowed_lower:
            return False, f"允许的文件类型: {', '.join(allowed_extensions)}"
        
        return True, "文件类型正确"

    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> Tuple[bool, str]:
        """验证文件大小"""
        if file_size > max_size:
            return False, f"文件大小不能超过{ValidationUtil._format_file_size(max_size)}"
        
        return True, "文件大小符合要求"

    @staticmethod
    def _format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"

    @staticmethod
    def validate_credit_card(card_number: str) -> Tuple[bool, str]:
        """验证信用卡号（Luhn算法）"""
        if not card_number or not isinstance(card_number, str):
            return False, "信用卡号不能为空"
        
        # 移除空格和连字符
        card_number = re.sub(r'[\s-]', '', card_number)
        
        # 检查是否全为数字
        if not card_number.isdigit():
            return False, "信用卡号只能包含数字"
        
        # 检查长度（一般为13-19位）
        if len(card_number) < 13 or len(card_number) > 19:
            return False, "信用卡号长度不正确"
        
        # Luhn算法验证
        try:
            def luhn_check(card_num):
                digits = [int(d) for d in card_num]
                for i in range(len(digits) - 2, -1, -2):
                    digits[i] *= 2
                    if digits[i] > 9:
                        digits[i] -= 9
                return sum(digits) % 10 == 0
            
            if not luhn_check(card_number):
                return False, "信用卡号格式不正确"
            
            return True, "信用卡号格式正确"
        except Exception:
            return False, "信用卡号验证失败"

    @staticmethod
    def validate_dict_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
        """验证字典必填字段"""
        if not isinstance(data, dict):
            return False, "数据必须是字典格式"
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"缺少必填字段: {', '.join(missing_fields)}"
        
        return True, "所有必填字段都已提供"

    @staticmethod
    def sanitize_input(value: str, max_length: int = 1000) -> str:
        """清理输入数据，防止XSS等攻击"""
        if not isinstance(value, str):
            return str(value)
        
        # 移除HTML标签
        import html
        value = html.escape(value)
        
        # 限制长度
        if len(value) > max_length:
            value = value[:max_length]
        
        # 移除控制字符
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        return value.strip()

    @staticmethod
    def validate_batch_data(data_list: List[Dict[str, Any]], 
                          validation_rules: Dict[str, callable]) -> Tuple[bool, List[str]]:
        """批量验证数据"""
        errors = []
        
        for index, data in enumerate(data_list):
            for field, validator in validation_rules.items():
                if field in data:
                    try:
                        is_valid, message = validator(data[field])
                        if not is_valid:
                            errors.append(f"第{index + 1}行，字段'{field}': {message}")
                    except Exception as e:
                        errors.append(f"第{index + 1}行，字段'{field}': 验证出错 - {str(e)}")
        
        return len(errors) == 0, errors
