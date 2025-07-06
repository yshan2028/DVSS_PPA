"""
用户认证和管理控制器
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from core.database import get_db
from core.models import User, Role
from utils.response_util import success_response, error_response
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT设置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境需要从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role_name: str
    department: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

@router.post("/login")
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    try:
        # 查询用户
        result = await db.execute(
            select(User, Role)
            .join(Role, User.role_id == Role.id)
            .where(User.username == login_data.username)
            .where(User.is_active == True)
        )
        
        user_role = result.first()
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        user, role = user_role
        
        # 验证密码
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        await db.commit()
        
        # 创建访问令牌
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": role.name,
                "department": user.department
            }
        )
        
        return success_response({
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_info": {
                "id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": role.name,
                "department": user.department,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        return error_response("登录失败")

@router.post("/register")
async def register(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册（仅管理员可用）"""
    try:
        # 检查用户名是否已存在
        existing_user = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已存在"
            )
        
        # 查询角色
        role_result = await db.execute(
            select(Role).where(Role.name == user_data.role_name)
        )
        role = role_result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="角色不存在"
            )
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            role_id=role.id,
            department=user_data.department,
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return success_response({
            "user_id": str(new_user.id),
            "username": new_user.username,
            "email": new_user.email,
            "role": user_data.role_name,
            "message": "用户创建成功"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await db.rollback()
        return error_response("注册失败")

# 依赖注入：获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    try:
        # 验证令牌
        payload = verify_token(credentials.credentials)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id).where(User.is_active == True)
        )
        
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已禁用",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败",
            headers={"WWW-Authenticate": "Bearer"}
        )

