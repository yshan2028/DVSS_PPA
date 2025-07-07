"""
数据库初始化脚本
创建默认角色和用户
"""

import bcrypt

from config.database import SessionLocal
from config.settings import Settings
from module_dvss.entity.role import Role
from module_dvss.entity.user import User

settings = Settings()

DEFAULT_ROLES = [
    {
        'name': 'seller',
        'display_name': '商家',
        'description': '商家角色，可以查看订单基本信息',
        'permissions': '["read_order", "read_customer_basic"]',
        'field_access': '{"allowed_fields": ["customer_name", "customer_phone", "delivery_address"]}',
    },
    {
        'name': 'payment_provider',
        'display_name': '支付服务商',
        'description': '支付服务商角色，可以查看支付相关信息',
        'permissions': '["read_payment", "write_payment"]',
        'field_access': '{"allowed_fields": ["payment_amount", "bank_card_number"]}',
    },
    {
        'name': 'logistics',
        'display_name': '物流',
        'description': '物流角色，可以查看配送相关信息',
        'permissions': '["read_shipping", "write_shipping"]',
        'field_access': '{"allowed_fields": ["customer_phone", "delivery_address"]}',
    },
    {
        'name': 'auditor',
        'display_name': '审计员',
        'description': '审计员角色，可以查看审计相关信息',
        'permissions': '["read_audit", "read_all"]',
        'field_access': '{"allowed_fields": ["customer_name", "payment_amount", "identity_card"]}',
    },
    {
        'name': 'platform',
        'display_name': '平台',
        'description': '平台角色，具有管理权限',
        'permissions': '["read_all", "write_all", "admin"]',
        'field_access': '{"allowed_fields": ["customer_name", "payment_amount", "bank_card_number", "identity_card"]}',
    },
    {
        'name': 'admin',
        'display_name': '系统管理员',
        'description': '系统管理员，具有所有权限',
        'permissions': '["*"]',
        'field_access': '{"allowed_fields": ["*"]}',
    },
]


def create_default_roles():
    """创建默认角色"""
    db = SessionLocal()
    try:
        for role_data in DEFAULT_ROLES:
            # 检查角色是否已存在
            existing_role = db.query(Role).filter(Role.name == role_data['name']).first()

            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                print(f'创建角色: {role_data["display_name"]}')
            else:
                print(f'角色已存在: {role_data["display_name"]}')

        db.commit()
        print('默认角色创建完成')
    except Exception as e:
        db.rollback()
        print(f'创建默认角色失败: {e}')
        raise
    finally:
        db.close()


def create_default_users():
    """创建默认用户"""
    db = SessionLocal()
    try:
        # 获取角色映射
        roles = {role.name: role for role in db.query(Role).all()}

        # 创建默认用户
        default_users = [{'username': 'admin', 'email': 'admin@example.com', 'password': 'admin123', 'role': 'admin'}]

        for user_data in default_users:
            # 检查用户是否已存在
            existing_user = db.query(User).filter(User.username == user_data['username']).first()

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

        db.commit()
        print('默认用户创建完成')
    except Exception as e:
        db.rollback()
        print(f'创建默认用户失败: {e}')
        raise
    finally:
        db.close()


def init_database():
    """初始化数据库"""
    print('开始初始化数据库...')

    try:
        # 创建默认角色
        create_default_roles()

        # 创建默认用户
        create_default_users()

        print('数据库初始化完成!')

    except Exception as e:
        print(f'数据库初始化失败: {e}')
        raise


if __name__ == '__main__':
    init_database()
