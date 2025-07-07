#!/usr/bin/env python3
"""
数据库连接测试脚本 - 异步版本
"""

import asyncio
import sys

sys.path.insert(0, '/app')


async def test_database_connection():
    """测试数据库连接"""
    print('开始测试数据库连接...')

    # 1. 测试原始PyMySQL连接
    try:
        import aiomysql

        connection = await aiomysql.connect(
            host='mysql', user='root', password='admin123', db='dvss_db', charset='utf8mb4'
        )
        print('✓ aiomysql连接成功')

        async with connection.cursor() as cursor:
            await cursor.execute('SELECT COUNT(*) FROM users')
            result = await cursor.fetchone()
            count = result[0]
            print(f'✓ 用户表记录数: {count}')

            await cursor.execute('SELECT username, password_hash, is_active FROM users WHERE username=%s', ('admin',))
            user = await cursor.fetchone()
            if user:
                print(f'✓ 找到admin用户: {user[0]}, 激活: {user[2]}')
                print(f'  密码哈希: {user[1][:50]}...')
            else:
                print('✗ 未找到admin用户')

        connection.close()
    except Exception as e:
        print(f'✗ aiomysql连接失败: {e}')
        return False

    # 2. 测试SQLAlchemy异步连接
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text

        from config.settings import Settings

        settings = Settings()
        print(f'数据库URL: {settings.DATABASE_URL}')

        engine = create_async_engine(settings.DATABASE_URL)

        async with engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('✓ SQLAlchemy异步连接成功')

            result = await conn.execute(text('SELECT COUNT(*) FROM users'))
            row = result.fetchone()
            count = row[0]
            print(f'✓ SQLAlchemy异步查询用户数: {count}')

        await engine.dispose()

    except Exception as e:
        print(f'✗ SQLAlchemy异步连接失败: {e}')
        import traceback

        traceback.print_exc()
        return False

    # 3. 测试AsyncSessionLocal
    try:
        from config.database import AsyncSessionLocal
        from module_dvss.entity.user import User
        from sqlalchemy.future import select

        async with AsyncSessionLocal() as db:
            print('✓ AsyncSessionLocal创建成功')

            result = await db.execute(select(User).filter(User.username == 'admin'))
            user = result.scalar_one_or_none()
            if user:
                print(f'✓ 找到admin用户: {user.username}, ID: {user.id}')
                print(f'  激活状态: {user.is_active}')
                print(f'  密码哈希: {user.password_hash[:50]}...')
            else:
                print('✗ AsyncSessionLocal未找到admin用户')

    except Exception as e:
        print(f'✗ AsyncSessionLocal测试失败: {e}')
        import traceback

        traceback.print_exc()
        return False

    # 4. 测试密码验证
    try:
        import bcrypt

        password = 'admin123'
        stored_hash = '$2b$12$QCVwJuN6VectR4.VugSObumXK3QBSxCE7ggiGs1KRYeNwW6oX7jyu'
        result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f'✓ 密码验证结果: {result}')

    except Exception as e:
        print(f'✗ 密码验证失败: {e}')
        return False

    print('所有数据库测试完成!')
    return True


if __name__ == '__main__':
    asyncio.run(test_database_connection())
