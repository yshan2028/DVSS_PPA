<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>DVSS-PPA 系统</h1>
        <p>动态可验证密钥分享与隐私保护认证系统</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        label-width="0"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            :disabled="loading"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            :disabled="loading"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-links">
        <el-link type="primary" @click="goToRegister">
          还没有账号？立即注册
        </el-link>
        <el-divider direction="vertical" />
        <el-link type="info" @click="goToAdminLogin">
          管理员登录
        </el-link>
      </div>
      
      <div class="demo-accounts">
        <h4>演示账户 (前台用户)</h4>
        <div class="account-grid">
          <div class="account-card" @click="fillAccount('user001', 'password123')">
            <strong>普通用户</strong>
            <p>用户名: user001</p>
            <p>基础查询权限</p>
          </div>
          <div class="account-card" @click="fillAccount('merchant001', 'password123')">
            <strong>支付商</strong>
            <p>用户名: merchant001</p>
            <p>支付数据权限</p>
          </div>
          <div class="account-card" @click="fillAccount('logistics001', 'password123')">
            <strong>物流商</strong>
            <p>用户名: logistics001</p>
            <p>物流配送权限</p>
          </div>
          <div class="account-card" @click="fillAccount('platform001', 'password123')">
            <strong>平台方</strong>
            <p>用户名: platform001</p>
            <p>平台运营权限</p>
          </div>
          <div class="account-card" @click="fillAccount('auditor001', 'password123')">
            <strong>审计方</strong>
            <p>用户名: auditor001</p>
            <p>审计查看权限</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value === 'admin') {
          callback(new Error('请使用管理员登录入口'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const fillAccount = (username, password) => {
  loginForm.username = username
  loginForm.password = password
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    
    try {
      // 使用前台用户登录
      await authStore.login(loginForm)
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

const goToRegister = () => {
  router.push('/register')
}

const goToAdminLogin = () => {
  router.push('/admin/login')
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  margin: 0;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-links {
  text-align: center;
  margin-bottom: 30px;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.demo-accounts {
  margin-top: 20px;
}

.demo-accounts h4 {
  text-align: center;
  color: #666;
  margin: 0 0 20px 0;
  font-size: 14px;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

/* 当屏幕较小时，调整为单列 */
@media (max-width: 480px) {
  .account-grid {
    grid-template-columns: 1fr;
  }
}

.account-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: center;
}

.account-card:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
  transform: translateY(-2px);
}

.account-card strong {
  display: block;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.account-card p {
  color: #666;
  margin: 2px 0;
  font-size: 12px;
}
</style>
