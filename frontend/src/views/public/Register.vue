<template>
  <div class="register-container">
    <div class="register-content">
      <!-- 左侧介绍 -->
      <div class="intro-section">
        <div class="intro-content">
          <div class="logo-section">
            <div class="logo-icon">
              <el-icon size="48"><Lock /></el-icon>
            </div>
            <h1>DVSS-PPA</h1>
            <p class="tagline">数据分片与隐私保护系统</p>
          </div>
          
          <div class="features">
            <div class="feature-item">
              <el-icon size="24" color="#67C23A"><Shield /></el-icon>
              <div>
                <h3>安全可靠</h3>
                <p>基于区块链技术，确保数据安全不被篡改</p>
              </div>
            </div>
            <div class="feature-item">
              <el-icon size="24" color="#409EFF"><Connection /></el-icon>
              <div>
                <h3>分布式存储</h3>
                <p>数据分片存储，提高可靠性和访问效率</p>
              </div>
            </div>
            <div class="feature-item">
              <el-icon size="24" color="#E6A23C"><View /></el-icon>
              <div>
                <h3>隐私保护</h3>
                <p>多层加密机制，保护个人隐私数据</p>
              </div>
            </div>
            <div class="feature-item">
              <el-icon size="24" color="#F56C6C"><Setting /></el-icon>
              <div>
                <h3>智能管理</h3>
                <p>自动化数据处理和智能权限管控</p>
              </div>
            </div>
          </div>

          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">1000+</div>
              <div class="stat-label">企业用户</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">99.9%</div>
              <div class="stat-label">系统可用性</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">50TB+</div>
              <div class="stat-label">数据处理量</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="form-section">
        <div class="form-container">
          <div class="form-header">
            <h2>创建账户</h2>
            <p>开始您的数据安全之旅</p>
          </div>

          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            size="large"
            class="register-form"
          >
            <!-- 账户类型选择 -->
            <el-form-item label="账户类型" prop="accountType">
              <el-radio-group v-model="registerForm.accountType" class="account-type">
                <el-radio-button label="personal">个人用户</el-radio-button>
                <el-radio-button label="enterprise">企业用户</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 基本信息 -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input 
                    v-model="registerForm.username" 
                    placeholder="请输入用户名"
                    :prefix-icon="User"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱地址" prop="email">
                  <el-input 
                    v-model="registerForm.email" 
                    placeholder="请输入邮箱地址"
                    :prefix-icon="Message"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="手机号码" prop="phone">
                  <el-input 
                    v-model="registerForm.phone" 
                    placeholder="请输入手机号码"
                    :prefix-icon="Phone"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item 
                  :label="registerForm.accountType === 'personal' ? '真实姓名' : '企业名称'" 
                  prop="realName"
                >
                  <el-input 
                    v-model="registerForm.realName" 
                    :placeholder="registerForm.accountType === 'personal' ? '请输入真实姓名' : '请输入企业名称'"
                    :prefix-icon="OfficeBuilding"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 企业用户额外信息 -->
            <template v-if="registerForm.accountType === 'enterprise'">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="统一社会信用代码" prop="creditCode">
                    <el-input 
                      v-model="registerForm.creditCode" 
                      placeholder="请输入统一社会信用代码"
                      :prefix-icon="Document"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="行业类型" prop="industry">
                    <el-select v-model="registerForm.industry" placeholder="请选择行业类型">
                      <el-option label="金融服务" value="finance" />
                      <el-option label="医疗健康" value="healthcare" />
                      <el-option label="教育培训" value="education" />
                      <el-option label="电子商务" value="ecommerce" />
                      <el-option label="制造业" value="manufacturing" />
                      <el-option label="互联网" value="internet" />
                      <el-option label="其他" value="other" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <!-- 密码设置 -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="登录密码" prop="password">
                  <el-input 
                    v-model="registerForm.password" 
                    type="password" 
                    placeholder="请输入登录密码"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input 
                    v-model="registerForm.confirmPassword" 
                    type="password" 
                    placeholder="请再次输入密码"
                    :prefix-icon="Lock"
                    show-password
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 验证码 -->
            <el-form-item label="邮箱验证码" prop="verificationCode">
              <div class="verification-input">
                <el-input 
                  v-model="registerForm.verificationCode" 
                  placeholder="请输入邮箱验证码"
                  :prefix-icon="Key"
                />
                <el-button 
                  type="primary" 
                  :disabled="!canSendCode || sendCodeLoading"
                  :loading="sendCodeLoading"
                  @click="handleSendCode"
                  class="send-code-btn"
                >
                  {{ sendCodeText }}
                </el-button>
              </div>
            </el-form-item>

            <!-- 协议同意 -->
            <el-form-item prop="agreements">
              <el-checkbox v-model="registerForm.agreements">
                我已阅读并同意 
                <el-link type="primary" @click="showTerms = true">《用户服务协议》</el-link>
                和 
                <el-link type="primary" @click="showPrivacy = true">《隐私政策》</el-link>
              </el-checkbox>
            </el-form-item>

            <!-- 注册按钮 -->
            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                class="register-btn"
                :loading="registerLoading"
                @click="handleRegister"
              >
                <el-icon v-if="!registerLoading"><UserFilled /></el-icon>
                {{ registerLoading ? '注册中...' : '立即注册' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <p>已有账户？ <router-link to="/login" class="login-link">立即登录</router-link></p>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务协议对话框 -->
    <el-dialog v-model="showTerms" title="用户服务协议" width="800px">
      <div class="agreement-content">
        <h3>1. 服务条款的接受</h3>
        <p>欢迎使用DVSS-PPA数据分片与隐私保护系统。通过注册和使用本服务，您表示同意遵守本协议的所有条款和条件。</p>
        
        <h3>2. 服务描述</h3>
        <p>DVSS-PPA是一个基于区块链技术的数据安全管理平台，为用户提供数据加密、分片存储、隐私保护等服务。</p>
        
        <h3>3. 用户责任</h3>
        <p>用户应当：</p>
        <ul>
          <li>提供真实、准确的注册信息</li>
          <li>保护账户安全，不向他人泄露登录凭证</li>
          <li>合法使用本服务，不从事违法活动</li>
          <li>遵守相关法律法规和平台规则</li>
        </ul>
        
        <h3>4. 隐私保护</h3>
        <p>我们承诺保护用户隐私，采用先进的加密技术和安全措施保护用户数据。详细信息请参阅隐私政策。</p>
        
        <h3>5. 服务变更</h3>
        <p>我们保留在必要时修改本协议的权利，修改后的协议将在平台上公布并生效。</p>
      </div>
      <template #footer>
        <el-button @click="showTerms = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog v-model="showPrivacy" title="隐私政策" width="800px">
      <div class="agreement-content">
        <h3>信息收集</h3>
        <p>我们收集以下类型的信息：</p>
        <ul>
          <li>注册信息：用户名、邮箱、手机号等</li>
          <li>使用信息：登录日志、操作记录等</li>
          <li>设备信息：IP地址、浏览器类型等</li>
        </ul>
        
        <h3>信息使用</h3>
        <p>收集的信息用于：</p>
        <ul>
          <li>提供和改进服务</li>
          <li>账户安全验证</li>
          <li>法律合规要求</li>
        </ul>
        
        <h3>信息保护</h3>
        <p>我们采用多层安全措施保护用户信息，包括但不限于：</p>
        <ul>
          <li>数据加密存储</li>
          <li>访问权限控制</li>
          <li>安全审计日志</li>
          <li>定期安全评估</li>
        </ul>
        
        <h3>信息共享</h3>
        <p>除法律要求外，我们不会与第三方共享用户个人信息。</p>
      </div>
      <template #footer>
        <el-button @click="showPrivacy = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User, Message, Phone, Lock, Key, UserFilled,
  OfficeBuilding, Document, Shield, Connection,
  View, Setting
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const registerFormRef = ref()
const registerLoading = ref(false)
const sendCodeLoading = ref(false)
const countdown = ref(0)
const showTerms = ref(false)
const showPrivacy = ref(false)

// 注册表单
const registerForm = reactive({
  accountType: 'personal',
  username: '',
  email: '',
  phone: '',
  realName: '',
  creditCode: '',
  industry: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
  agreements: false
})

// 验证码发送文本
const sendCodeText = computed(() => {
  return countdown.value > 0 ? `${countdown.value}s` : '发送验证码'
})

// 是否可以发送验证码
const canSendCode = computed(() => {
  return registerForm.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email) && countdown.value === 0
})

// 自定义验证器
const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少8位'))
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含大小写字母和数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreements = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  accountType: [
    { required: true, message: '请选择账户类型', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '用户名只能包含字母、数字、下划线和短横线', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名/企业名称', trigger: 'blur' }
  ],
  creditCode: [
    { 
      required: true, 
      message: '请输入统一社会信用代码', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (registerForm.accountType === 'enterprise') {
          if (!value) {
            callback(new Error('企业用户必须输入统一社会信用代码'))
          } else if (!/^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/.test(value)) {
            callback(new Error('请输入正确的统一社会信用代码'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      }
    }
  ],
  industry: [
    { 
      required: true, 
      message: '请选择行业类型', 
      trigger: 'change',
      validator: (rule, value, callback) => {
        if (registerForm.accountType === 'enterprise' && !value) {
          callback(new Error('企业用户必须选择行业类型'))
        } else {
          callback()
        }
      }
    }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  verificationCode: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  agreements: [
    { required: true, validator: validateAgreements, trigger: 'change' }
  ]
}

// 发送验证码
const handleSendCode = async () => {
  if (!canSendCode.value) return
  
  sendCodeLoading.value = true
  
  try {
    // 这里应该调用发送验证码的API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('验证码已发送到您的邮箱')
    
    // 开始倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
    
  } catch (error) {
    ElMessage.error('发送验证码失败：' + error.message)
  } finally {
    sendCodeLoading.value = false
  }
}

// 注册
const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    
    registerLoading.value = true
    
    // 模拟注册API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 这里应该调用实际的注册API
    console.log('注册数据:', registerForm)
    
    ElMessage.success('注册成功！请前往邮箱激活账户')
    
    // 跳转到登录页面
    router.push('/login')
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('注册失败：' + error.message)
    }
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-content {
  display: flex;
  max-width: 1200px;
  width: 100%;
  background: white;
  border-radius: 20px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  min-height: 700px;
}

.intro-section {
  flex: 1;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 60px;
  position: relative;
}

.intro-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('/src/assets/pattern.svg') no-repeat center;
  background-size: cover;
  opacity: 0.1;
}

.intro-content {
  position: relative;
  z-index: 1;
}

.logo-section {
  text-align: center;
  margin-bottom: 50px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.logo-section h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.tagline {
  font-size: 1.2rem;
  opacity: 0.8;
  margin: 0;
}

.features {
  margin-bottom: 50px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.feature-item .el-icon {
  margin-right: 20px;
  background: rgba(255, 255, 255, 0.1);
  padding: 12px;
  border-radius: 12px;
}

.feature-item h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
}

.feature-item p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.stats {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.form-section {
  flex: 1;
  padding: 60px;
  display: flex;
  align-items: center;
}

.form-container {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0 0 10px 0;
}

.form-header p {
  color: #7f8c8d;
  margin: 0;
}

.register-form {
  margin-bottom: 30px;
}

.account-type {
  width: 100%;
}

.account-type .el-radio-button {
  flex: 1;
}

.verification-input {
  display: flex;
  gap: 10px;
}

.verification-input .el-input {
  flex: 1;
}

.send-code-btn {
  min-width: 120px;
}

.register-btn {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
  font-weight: 600;
}

.form-footer {
  text-align: center;
  color: #7f8c8d;
}

.login-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
}

.agreement-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
}

.agreement-content h3 {
  color: #2c3e50;
  margin: 20px 0 10px 0;
}

.agreement-content p {
  margin: 10px 0;
  color: #555;
}

.agreement-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.agreement-content li {
  margin: 5px 0;
  color: #555;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-content {
    flex-direction: column;
    margin: 10px;
  }
  
  .intro-section,
  .form-section {
    padding: 30px;
  }
  
  .intro-section {
    min-height: 300px;
  }
  
  .stats {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
