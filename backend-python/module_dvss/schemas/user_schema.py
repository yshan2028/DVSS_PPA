"""
用户相关模式
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")

class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role_id: int = Field(..., description="角色ID")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否超级用户")

class UserUpdate(BaseModel):
    """更新用户模式"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    role_id: Optional[int] = Field(None, description="角色ID")
    is_active: Optional[bool] = Field(None, description="是否激活")

class UserList(BaseModel):
    """用户列表模式"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    role_id: Optional[int]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """用户响应模式"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级用户")
    role_id: Optional[int] = Field(None, description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

    class Config:
        from_attributes = True

class UserPasswordChange(BaseModel):
    """修改密码模式"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

class LoginRequest(BaseModel):
    """登录请求模式"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class LoginResponse(BaseModel):
    """登录响应模式"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserResponse = Field(..., description="用户信息")
    refresh_token: str = Field(..., description="刷新令牌")
    user_info: UserResponse = Field(..., description="用户信息")

class ChangePasswordRequest(BaseModel):
    """修改密码请求模式"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")
