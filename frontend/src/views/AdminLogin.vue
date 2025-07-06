<template>
  <div class="admin-login">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h2>DVSS-PPA 管理后台</h2>
          <p>系统管理员登录</p>
        </div>
        
        <el-form 
          ref="loginFormRef"
          :model="loginForm" 
          :rules="rules" 
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="管理员账号 (admin)"
              prefix-icon="User"
              size="large"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码 (admin)"
              prefix-icon="Lock"
              size="large"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              class="login-button"
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '管理员登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-footer">
          <el-link type="primary" @click="goToUserLogin">
            前台用户登录
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const loginFormRef = ref()

// 登录表单
const loginForm = reactive({
  username: 'admin',
  password: 'admin'
})

// 验证规则
const rules = {
  username: [
    { required: true, message: '请输入管理员账号', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== 'admin') {
          callback(new Error('管理员账号只能是 admin'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 5, message: '密码长度至少5位', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 使用管理员登录接口
    await authStore.adminLogin(loginForm)
    
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loading.value = false
  }
}

// 跳转到前台用户登录
const goToUserLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.admin-login {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #303133;
  margin: 0 0 10px 0;
  font-weight: 600;
}

.login-header p {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: 500;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

:deep(.el-input__inner) {
  height: 45px;
  line-height: 45px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
