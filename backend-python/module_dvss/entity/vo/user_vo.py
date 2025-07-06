"""
用户视图对象 (VO)
View Object - 用于API响应的数据传输对象
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRoleEnum(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"

class UserStatusEnum(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class UserCreateRequest(BaseModel):
    """用户创建请求"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.USER
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

    @validator('username')
    def username_validator(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('用户名长度必须在3-50个字符之间')
        return v

    @validator('password')
    def password_validator(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8个字符')
        return v

class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    full_name: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    permissions: Optional[List[str]] = None

class UserPasswordChangeRequest(BaseModel):
    """用户密码修改请求"""
    old_password: str
    new_password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('新密码和确认密码不匹配')
        return v

class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str
    password: str

class UserLoginResponse(BaseModel):
    """用户登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: 'UserDetailResponse'

class UserBaseResponse(BaseModel):
    """用户基础响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    role: UserRoleEnum
    status: UserStatusEnum
    is_superuser: bool = False
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserDetailResponse(UserBaseResponse):
    """用户详细信息响应"""
    address: Optional[str] = None
    last_login: Optional[datetime] = None
    permissions: Optional[List[str]] = None
    public_key: Optional[str] = None

class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    page: int
    page_size: int
    items: List[UserBaseResponse]

class UserPermissionRequest(BaseModel):
    """用户权限设置请求"""
    user_id: int
    permissions: List[str]
    granted_by: int

class UserPermissionResponse(BaseModel):
    """用户权限响应"""
    user_id: int
    username: str
    permissions: List[str]
    granted_by: int
    granted_at: datetime

class UserSearchRequest(BaseModel):
    """用户搜索请求"""
    keyword: Optional[str] = None
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    page: int = 1
    page_size: int = 20

class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    regular_users: int
    new_users_this_month: int

# 为了避免循环导入，在这里更新前向引用
UserLoginResponse.model_rebuild()
