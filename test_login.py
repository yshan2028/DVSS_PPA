#!/usr/bin/env python3

import sys
sys.path.append('/app')

try:
    from config.database import SessionLocal
    from module_dvss.service.auth_service import AuthService
    from module_dvss.schemas.user_schema import LoginRequest
    
    print("✅ 导入模块成功")
    
    # 测试登录服务
    db = SessionLocal()
    auth_service = AuthService(db)
    
    login_data = LoginRequest(username="admin", password="admin123")
    
    print("🔄 开始测试登录...")
    result = auth_service.login(login_data)
    print(f"✅ 登录成功! Token: {result.access_token[:50]}...")
    
    db.close()
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
