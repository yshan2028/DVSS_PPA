"""
数据库初始化脚本 - 异步版本
创建默认角色和用户
"""

import asyncio
import bcrypt

from config.database import AsyncSessionLocal
from config.settings import Settings
from module_dvss.entity.role import Role
from module_dvss.entity.user import User
from sqlalchemy.future import select

settings = Settings()

DEFAULT_ROLES = [
    {
        'name': 'seller',
        'description': '商家角色，可以查看订单基本信息',
        'is_active': True,
    },
    {
        'name': 'payment_provider',
        'description': '支付服务商角色，可以查看支付相关信息',
        'is_active': True,
    },
    {
        'name': 'logistics',
        'description': '物流角色，可以查看配送相关信息',
        'is_active': True,
    },
    {
        'name': 'auditor',
        'description': '审计员角色，可以查看审计相关信息',
        'is_active': True,
    },
    {
        'name': 'platform',
        'description': '平台角色，具有管理权限',
        'is_active': True,
    },
    {
        'name': 'admin',
        'description': '系统管理员，具有所有权限',
        'is_active': True,
    },
]


async def create_default_roles():
    """创建默认角色"""
    async with AsyncSessionLocal() as db:
        try:
            for role_data in DEFAULT_ROLES:
                # 检查角色是否已存在
                result = await db.execute(select(Role).filter(Role.name == role_data['name']))
                existing_role = result.scalar_one_or_none()

                if not existing_role:
                    role = Role(**role_data)
                    db.add(role)
                    print(f'创建角色: {role_data["name"]}')
                else:
                    print(f'角色已存在: {role_data["name"]}')

            await db.commit()
            print('默认角色创建完成')
        except Exception as e:
            await db.rollback()
            print(f'创建默认角色失败: {e}')
            raise


async def create_default_users():
    """创建默认用户"""
    async with AsyncSessionLocal() as db:
        try:
            # 获取角色映射
            result = await db.execute(select(Role))
            roles = {role.name: role for role in result.scalars().all()}

            # 创建默认用户
            default_users = [{'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123', 'role': 'admin'}]

            for user_data in default_users:
                # 检查用户是否已存在
                result = await db.execute(select(User).filter(User.username == user_data['username']))
                existing_user = result.scalar_one_or_none()

                if not existing_user:
                    role = roles.get(user_data['role'])
                    if not role:
                        print(f'角色不存在: {user_data["role"]}')
                        continue

                    # 生成密码哈希
                    password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=password_hash,
                        full_name=user_data['username'],
                        role_id=role.id,
                        is_active=True,
                    )
                    db.add(user)
                    print(f'创建用户: {user_data["username"]} ({role.display_name})')
                else:
                    print(f'用户已存在: {user_data["username"]}')

            await db.commit()
            print('默认用户创建完成')
        except Exception as e:
            await db.rollback()
            print(f'创建默认用户失败: {e}')
            raise


async def init_database():
    """初始化数据库"""
    print('开始异步初始化数据库...')

    try:
        # 创建默认角色
        await create_default_roles()

        # 创建默认用户
        await create_default_users()

        print('数据库初始化完成!')

    except Exception as e:
        print(f'数据库初始化失败: {e}')
        raise


if __name__ == '__main__':
    asyncio.run(init_database())
