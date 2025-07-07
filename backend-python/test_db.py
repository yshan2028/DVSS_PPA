#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import sys
import os
sys.path.insert(0, '/app')

def test_database_connection():
    """测试数据库连接"""
    print("开始测试数据库连接...")
    
    # 1. 测试原始PyMySQL连接
    try:
        import pymysql
        connection = pymysql.connect(
            host='mysql',
            user='root', 
            password='admin123',
            database='dvss_db',
            charset='utf8mb4'
        )
        print("✓ PyMySQL连接成功")
        
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            print(f"✓ 用户表记录数: {count}")
            
            cursor.execute('SELECT username, password_hash, is_active FROM users WHERE username=%s', ('admin',))
            user = cursor.fetchone()
            if user:
                print(f"✓ 找到admin用户: {user[0]}, 激活: {user[2]}")
                print(f"  密码哈希: {user[1][:50]}...")
            else:
                print("✗ 未找到admin用户")
                
        connection.close()
    except Exception as e:
        print(f"✗ PyMySQL连接失败: {e}")
        return False
    
    # 2. 测试SQLAlchemy连接
    try:
        from sqlalchemy import create_engine, text
        from config.settings import Settings
        
        settings = Settings()
        print(f"数据库URL: {settings.DATABASE_URL}")
        
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✓ SQLAlchemy连接成功")
            
            result = conn.execute(text('SELECT COUNT(*) FROM users'))
            count = result.fetchone()[0]
            print(f"✓ SQLAlchemy查询用户数: {count}")
            
    except Exception as e:
        print(f"✗ SQLAlchemy连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 测试SessionLocal
    try:
        from config.database import SessionLocal
        from module_dvss.entity.user import User
        
        db = SessionLocal()
        print("✓ SessionLocal创建成功")
        
        user = db.query(User).filter(User.username == 'admin').first()
        if user:
            print(f"✓ 找到admin用户: {user.username}, ID: {user.id}")
            print(f"  激活状态: {user.is_active}")
            print(f"  密码哈希: {user.password_hash[:50]}...")
        else:
            print("✗ SessionLocal未找到admin用户")
            
        db.close()
        
    except Exception as e:
        print(f"✗ SessionLocal测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 测试密码验证
    try:
        import bcrypt
        password = 'admin123'
        stored_hash = '$2b$12$QCVwJuN6VectR4.VugSObumXK3QBSxCE7ggiGs1KRYeNwW6oX7jyu'
        result = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        print(f"✓ 密码验证结果: {result}")
        
    except Exception as e:
        print(f"✗ 密码验证失败: {e}")
        return False
    
    print("所有数据库测试完成!")
    return True

if __name__ == "__main__":
    test_database_connection()
