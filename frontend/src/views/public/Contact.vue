<template>
  <div class="contact-container">
    <div class="contact-header">
      <h1>联系我们</h1>
      <p class="subtitle">有问题或建议？我们随时为您提供帮助</p>
    </div>

    <el-row :gutter="40" class="contact-content">
      <!-- 联系信息 -->
      <el-col :span="12">
        <div class="contact-info">
          <h2>联系方式</h2>
          
          <div class="info-item">
            <div class="info-icon">
              <el-icon size="24" color="#409EFF"><Location /></el-icon>
            </div>
            <div class="info-content">
              <h3>地址</h3>
              <p>北京市海淀区中关村软件园</p>
              <p>创新大厦A座10层</p>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon size="24" color="#409EFF"><Phone /></el-icon>
            </div>
            <div class="info-content">
              <h3>电话</h3>
              <p>400-123-4567</p>
              <p>010-8888-9999</p>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon size="24" color="#409EFF"><Message /></el-icon>
            </div>
            <div class="info-content">
              <h3>邮箱</h3>
              <p>support@dvss-ppa.com</p>
              <p>info@dvss-ppa.com</p>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon">
              <el-icon size="24" color="#409EFF"><Clock /></el-icon>
            </div>
            <div class="info-content">
              <h3>工作时间</h3>
              <p>周一至周五：9:00 - 18:00</p>
              <p>周六：9:00 - 12:00</p>
            </div>
          </div>

          <!-- 社交媒体 -->
          <div class="social-media">
            <h3>关注我们</h3>
            <div class="social-links">
              <el-button circle size="large" class="social-btn wechat">
                <el-icon><ChatDotRound /></el-icon>
              </el-button>
              <el-button circle size="large" class="social-btn weibo">
                <el-icon><Star /></el-icon>
              </el-button>
              <el-button circle size="large" class="social-btn email">
                <el-icon><Message /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 联系表单 -->
      <el-col :span="12">
        <div class="contact-form">
          <h2>发送消息</h2>
          <el-form
            ref="contactFormRef"
            :model="contactForm"
            :rules="contactRules"
            label-position="top"
            size="large"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="contactForm.name" placeholder="请输入您的姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="contactForm.email" placeholder="请输入您的邮箱" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="电话" prop="phone">
                  <el-input v-model="contactForm.phone" placeholder="请输入您的电话" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="公司" prop="company">
                  <el-input v-model="contactForm.company" placeholder="请输入您的公司名称" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="主题" prop="subject">
              <el-select v-model="contactForm.subject" placeholder="请选择咨询主题" style="width: 100%">
                <el-option label="产品咨询" value="product" />
                <el-option label="技术支持" value="support" />
                <el-option label="商务合作" value="business" />
                <el-option label="意见反馈" value="feedback" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>

            <el-form-item label="消息内容" prop="message">
              <el-input
                v-model="contactForm.message"
                type="textarea"
                :rows="6"
                placeholder="请详细描述您的问题或需求..."
                show-word-limit
                maxlength="500"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                size="large" 
                style="width: 100%" 
                :loading="submitLoading"
                @click="handleSubmit"
              >
                <el-icon v-if="!submitLoading"><Position /></el-icon>
                {{ submitLoading ? '发送中...' : '发送消息' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>

    <!-- 地图区域 -->
    <div class="map-section">
      <h2>位置信息</h2>
      <div class="map-container">
        <div class="map-placeholder">
          <el-icon size="48" color="#C0C4CC"><Location /></el-icon>
          <p>地图加载中...</p>
          <p class="map-tip">北京市海淀区中关村软件园创新大厦A座</p>
        </div>
      </div>
    </div>

    <!-- FAQ 常见问题 -->
    <div class="faq-section">
      <h2>常见问题</h2>
      <el-collapse v-model="activeFaq">
        <el-collapse-item title="什么是DVSS-PPA系统？" name="1">
          <p>DVSS-PPA是一个基于区块链技术的数据分片与隐私保护系统，旨在为企业和个人提供安全、可靠的数据存储和处理解决方案。</p>
        </el-collapse-item>
        <el-collapse-item title="如何申请试用账号？" name="2">
          <p>您可以通过我们的官网注册页面申请试用账号，或者联系我们的销售团队获取更多信息。试用期为30天，包含完整功能。</p>
        </el-collapse-item>
        <el-collapse-item title="系统支持哪些数据格式？" name="3">
          <p>系统支持多种常见数据格式，包括JSON、XML、CSV、Excel等结构化数据，以及图片、文档等非结构化数据。</p>
        </el-collapse-item>
        <el-collapse-item title="数据安全如何保障？" name="4">
          <p>我们采用多层次的安全保护机制，包括数据加密、区块链不可篡改性、分布式存储、访问控制等，确保您的数据安全。</p>
        </el-collapse-item>
        <el-collapse-item title="是否提供技术支持？" name="5">
          <p>是的，我们提供7×24小时技术支持服务，包括在线文档、技术论坛、邮件支持和电话支持等多种方式。</p>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Location, Phone, Message, Clock, ChatDotRound, 
  Star, Position 
} from '@element-plus/icons-vue'

// 响应式数据
const contactFormRef = ref()
const submitLoading = ref(false)
const activeFaq = ref(['1'])

// 联系表单
const contactForm = reactive({
  name: '',
  email: '',
  phone: '',
  company: '',
  subject: '',
  message: ''
})

// 表单验证规则
const contactRules = {
  name: [
    { required: true, message: '请输入您的姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入电话号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  subject: [
    { required: true, message: '请选择咨询主题', trigger: 'change' }
  ],
  message: [
    { required: true, message: '请输入消息内容', trigger: 'blur' },
    { min: 10, message: '消息内容至少需要10个字符', trigger: 'blur' }
  ]
}

// 提交表单
const handleSubmit = async () => {
  try {
    await contactFormRef.value.validate()
    
    submitLoading.value = true
    
    // 模拟提交延迟
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 这里应该调用实际的API
    console.log('提交联系表单:', contactForm)
    
    ElMessage.success('消息发送成功！我们会尽快与您联系。')
    
    // 重置表单
    contactFormRef.value.resetFields()
    
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.contact-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 60px 20px;
}

.contact-header {
  text-align: center;
  margin-bottom: 60px;
}

.contact-header h1 {
  font-size: 3rem;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin: 0;
}

.contact-content {
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 80px;
}

.contact-info {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.contact-info h2 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
}

.info-icon {
  margin-right: 20px;
  margin-top: 5px;
}

.info-content h3 {
  color: #34495e;
  margin: 0 0 10px 0;
  font-size: 1.1rem;
}

.info-content p {
  color: #7f8c8d;
  margin: 5px 0;
  line-height: 1.6;
}

.social-media {
  margin-top: 40px;
}

.social-media h3 {
  color: #34495e;
  margin-bottom: 20px;
}

.social-links {
  display: flex;
  gap: 15px;
}

.social-btn {
  width: 50px;
  height: 50px;
}

.social-btn.wechat {
  background: #07c160;
  border-color: #07c160;
  color: white;
}

.social-btn.weibo {
  background: #e6162d;
  border-color: #e6162d;
  color: white;
}

.social-btn.email {
  background: #409EFF;
  border-color: #409EFF;
  color: white;
}

.contact-form {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.contact-form h2 {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.map-section {
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 80px;
}

.map-section h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.map-container {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
}

.map-placeholder {
  height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
  background: #f8f9fa;
}

.map-tip {
  margin-top: 10px;
  font-weight: 500;
  color: #34495e;
}

.faq-section {
  max-width: 1200px;
  margin: 0 auto;
}

.faq-section h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8rem;
}

.faq-section .el-collapse {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

:deep(.el-collapse-item__header) {
  padding: 20px 30px;
  font-size: 1.1rem;
  font-weight: 500;
  color: #2c3e50;
}

:deep(.el-collapse-item__content) {
  padding: 0 30px 30px 30px;
  color: #7f8c8d;
  line-height: 1.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .contact-header h1 {
    font-size: 2rem;
  }
  
  .contact-content {
    padding: 0 10px;
  }
  
  .contact-info,
  .contact-form {
    padding: 20px;
  }
  
  .social-links {
    justify-content: center;
  }
}
</style>
