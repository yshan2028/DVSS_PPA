#!/usr/bin/env python3

import sys
sys.path.append('/app')

try:
    from config.database import SessionLocal
    from module_dvss.entity.user import User
    from module_dvss.entity.role import Role
    
    print("✅ 导入模块成功")
    
    # 测试数据库连接
    db = SessionLocal()
    print("✅ 数据库连接成功")
    
    # 查询用户
    users = db.query(User).all()
    print(f"✅ 找到 {len(users)} 个用户")
    
    for user in users:
        print(f"  - 用户: {user.username}, 激活: {user.is_active}")
    
    # 查询admin用户
    admin_user = db.query(User).filter(User.username == 'admin').first()
    if admin_user:
        print(f"✅ 找到admin用户: ID={admin_user.id}, 密码哈希存在: {bool(admin_user.password_hash)}")
    else:
        print("❌ 未找到admin用户")
    
    db.close()
    print("✅ 测试完成")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
