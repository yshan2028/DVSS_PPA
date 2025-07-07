"""
角色相关的 Pydantic 模式
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """角色基础模式"""

    name: str = Field(..., description='角色名称', max_length=50)
    description: Optional[str] = Field(None, description='角色描述', max_length=255)
    is_active: bool = Field(True, description='是否激活')


class RoleCreate(RoleBase):
    """创建角色模式"""

    pass


class RoleUpdate(BaseModel):
    """更新角色模式"""

    name: Optional[str] = Field(None, description='角色名称', max_length=50)
    description: Optional[str] = Field(None, description='角色描述', max_length=255)
    is_active: Optional[bool] = Field(None, description='是否激活')


class RoleList(BaseModel):
    """角色列表模式"""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class RoleResponse(RoleBase):
    """角色响应模式"""

    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# 角色字段权限相关模式
class RolePermissionBase(BaseModel):
    """角色字段权限基础模式"""

    role_id: int = Field(..., description='角色ID')
    field_id: int = Field(..., description='字段ID')
    can_view: bool = Field(True, description='可查看')
    can_decrypt: bool = Field(False, description='可解密')


class RolePermissionCreate(RolePermissionBase):
    """创建角色字段权限模式"""

    pass


class RolePermissionUpdate(BaseModel):
    """更新角色字段权限模式"""

    can_view: Optional[bool] = Field(None, description='可查看')
    can_decrypt: Optional[bool] = Field(None, description='可解密')


class RolePermissionResponse(RolePermissionBase):
    """角色字段权限响应模式"""

    id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
