<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="error-icon">
        <el-icon :size="120" color="#409EFF">
          <WarningFilled />
        </el-icon>
      </div>
      
      <h1 class="error-title">404</h1>
      <h2 class="error-subtitle">页面未找到</h2>
      
      <p class="error-description">
        抱歉，您访问的页面不存在或已被移动。
      </p>
      
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上页
        </el-button>
      </div>
      
      <div class="help-links">
        <h3>您可能想要：</h3>
        <ul>
          <li><router-link to="/public/home">访问首页</router-link></li>
          <li><router-link to="/public/query">数据查询</router-link></li>
          <li><router-link to="/public/encrypt">数据加密</router-link></li>
          <li><router-link to="/public/about">了解我们</router-link></li>
          <li><router-link to="/public/contact">联系我们</router-link></li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { WarningFilled, HomeFilled, Back } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/public/home')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.not-found-content {
  text-align: center;
  max-width: 600px;
  background: white;
  padding: 60px 40px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.error-icon {
  margin-bottom: 30px;
}

.error-title {
  font-size: 6rem;
  font-weight: 700;
  color: #409EFF;
  margin: 0 0 20px 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-subtitle {
  font-size: 2rem;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.error-description {
  font-size: 1.1rem;
  color: #606266;
  margin-bottom: 40px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
}

.help-links {
  border-top: 1px solid #ebeef5;
  padding-top: 30px;
}

.help-links h3 {
  font-size: 1.2rem;
  color: #303133;
  margin-bottom: 20px;
}

.help-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-links li {
  margin-bottom: 12px;
}

.help-links a {
  color: #409EFF;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.help-links a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-content {
    padding: 40px 20px;
  }
  
  .error-title {
    font-size: 4rem;
  }
  
  .error-subtitle {
    font-size: 1.5rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
