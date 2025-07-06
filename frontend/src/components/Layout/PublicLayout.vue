<template>
  <div class="public-layout">
    <!-- 顶部导航 -->
    <el-header class="public-header" height="60px">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-text">DVSS</div>
          <h1 class="app-title">DVSS-PPA 系统</h1>
        </div>
        
        <div class="header-right">
          <el-button type="primary" @click="goToLogin">登录</el-button>
        </div>
      </div>
    </el-header>

    <!-- 主内容 -->
    <el-main class="public-main">
      <router-view />
    </el-main>

    <!-- 底部 -->
    <el-footer class="public-footer" height="60px">
      <div class="footer-content">
        <p>&copy; 2024 DVSS-PPA System. All rights reserved.</p>
      </div>
    </el-footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
.public-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.public-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  
  .header-content {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    
    .logo-text {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 16px;
      font-weight: bold;
      margin-right: 12px;
      letter-spacing: 1px;
    }
    
    .app-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.public-main {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
}

.public-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  
  .footer-content {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    p {
      margin: 0;
      color: #909399;
      font-size: 14px;
    }
  }
}
</style>
