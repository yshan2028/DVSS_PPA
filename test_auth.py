#!/usr/bin/env python3

import sys
sys.path.append('/app')

try:
    from config.database import SessionLocal
    import bcrypt
    
    print("✅ 导入模块成功")
    
    # 测试数据库连接
    db = SessionLocal()
    print("✅ 数据库连接成功")
    
    # 使用原始SQL查询避免ORM关系问题
    from sqlalchemy import text
    result = db.execute(text("SELECT id, username, password_hash, is_active FROM users WHERE username = 'admin'"))
    user_row = result.fetchone()
    
    if user_row:
        print(f"✅ 找到admin用户: ID={user_row.id}, 用户名={user_row.username}")
        print(f"  - 激活状态: {user_row.is_active}")
        print(f"  - 密码哈希: {user_row.password_hash[:50]}...")
        
        # 测试密码验证
        password = 'admin123'
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), user_row.password_hash.encode('utf-8'))
            print(f"  - 密码验证结果: {result}")
        except Exception as e:
            print(f"  - 密码验证失败: {e}")
        
    else:
        print("❌ 未找到admin用户")
    
    db.close()
    print("✅ 测试完成")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
