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
      
      <div class="demo-accounts">
        <h4>演示账户</h4>
        <div class="account-grid">
          <div class="account-card" @click="fillAccount('platform', 'admin')">
            <strong>平台管理</strong>
            <p>用户名: platform</p>
            <p>平台管理权限</p>
          </div>
          <div class="account-card" @click="fillAccount('auditor', 'admin')">
            <strong>审计人员</strong>
            <p>用户名: auditor</p>
            <p>审计查看权限</p>
          </div>
          <div class="account-card" @click="fillAccount('seller', 'admin')">
            <strong>卖家</strong>
            <p>用户名: seller</p>
            <p>订单客户权限</p>
          </div>
          <div class="account-card" @click="fillAccount('payment_provider', 'admin')">
            <strong>支付服务商</strong>
            <p>用户名: payment_provider</p>
            <p>支付数据权限</p>
          </div>
          <div class="account-card" @click="fillAccount('logistics', 'admin')">
            <strong>物流</strong>
            <p>用户名: logistics</p>
            <p>物流配送权限</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
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
      await userStore.login(loginForm)
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
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
  margin-bottom: 30px;
}

.demo-accounts {
  border-top: 1px solid #eee;
  padding-top: 20px;
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
