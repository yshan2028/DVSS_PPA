"""
用户数据对象 (DO)
Data Object - 对应数据库表结构
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from config.get_db import Base
import enum

class UserRole(enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"
    RESEARCHER = "researcher"

class UserStatus(enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class DvssUser(Base):
    """
    DVSS用户表
    """
    __tablename__ = "dvss_users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), nullable=True, comment="全名")
    organization = Column(String(100), nullable=True, comment="所属机构")
    department = Column(String(100), nullable=True, comment="部门")
    
    # 角色和状态
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, comment="用户角色")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="用户状态")
    
    # 权限相关
    permissions = Column(Text, nullable=True, comment="JSON格式的权限列表")
    is_superuser = Column(Boolean, default=False, comment="是否为超级用户")
    
    # 安全相关
    public_key = Column(Text, nullable=True, comment="用户公钥")
    private_key_encrypted = Column(Text, nullable=True, comment="加密的私钥")
    last_login = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    login_attempts = Column(Integer, default=0, comment="登录尝试次数")
    account_locked_until = Column(DateTime(timezone=True), nullable=True, comment="账户锁定截止时间")
    
    # 审计字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建者ID")
    updated_by = Column(Integer, nullable=True, comment="更新者ID")
    
    # 其他字段
    phone = Column(String(20), nullable=True, comment="电话号码")
    address = Column(Text, nullable=True, comment="地址")
    notes = Column(Text, nullable=True, comment="备注")
    
    def __repr__(self):
        return f"<DvssUser(id={self.id}, username='{self.username}', email='{self.email}')>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "organization": self.organization,
            "department": self.department,
            "role": self.role.value if self.role else None,
            "status": self.status.value if self.status else None,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "phone": self.phone,
            "address": self.address
        }
