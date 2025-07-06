<template>
  <MainLayout>
    <div class="encrypt-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>数据上传与加密</h1>
      <p>上传订单数据，系统将自动进行敏感度分析和分片加密</p>
    </div>

    <!-- 操作选项卡 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 单个订单上传 -->
      <el-tab-pane label="单个订单" name="single">
        <el-card shadow="never" class="form-card">
          <el-form 
            :model="orderForm" 
            :rules="formRules"
            ref="orderFormRef" 
            label-width="120px"
            class="order-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="订单ID" prop="order_id">
                  <el-input 
                    v-model="orderForm.order_id" 
                    placeholder="请输入订单ID"
                    :disabled="uploading"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="客户名称" prop="customer_name">
                  <el-input 
                    v-model="orderForm.customer_name" 
                    placeholder="请输入客户姓名"
                    :disabled="uploading"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="联系电话" prop="customer_phone">
                  <el-input 
                    v-model="orderForm.customer_phone" 
                    placeholder="请输入联系电话"
                    :disabled="uploading"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="订单金额" prop="order_amount">
                  <el-input-number 
                    v-model="orderForm.order_amount" 
                    :min="0" 
                    :precision="2"
                    style="width: 100%"
                    placeholder="请输入订单金额"
                    :disabled="uploading"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="支付方式" prop="payment_method">
                  <el-select 
                    v-model="orderForm.payment_method" 
                    style="width: 100%"
                    placeholder="请选择支付方式"
                    :disabled="uploading"
                  >
                    <el-option label="支付宝" value="alipay" />
                    <el-option label="微信支付" value="wechat" />
                    <el-option label="银行卡" value="bank_card" />
                    <el-option label="现金" value="cash" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="银行卡号" v-if="orderForm.payment_method === 'bank_card'">
                  <el-input 
                    v-model="orderForm.bank_card_number" 
                    placeholder="请输入银行卡号"
                    :disabled="uploading"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="收货地址" prop="shipping_address">
              <el-input 
                v-model="orderForm.shipping_address" 
                type="textarea"
                :rows="3"
                placeholder="请输入详细收货地址"
                :disabled="uploading"
              />
            </el-form-item>

            <el-form-item label="备注信息">
              <el-input 
                v-model="orderForm.notes" 
                type="textarea"
                :rows="2"
                placeholder="订单备注信息（可选）"
                :disabled="uploading"
              />
            </el-form-item>

            <!-- 分析预览 -->
            <div v-if="analysisResult" class="analysis-preview">
              <el-divider content-position="left">敏感度分析结果</el-divider>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="analysis-item">
                    <span class="label">敏感度等级:</span>
                    <el-tag :type="getSensitivityTagType(analysisResult.sensitivity_level)">
                      {{ getSensitivityLabel(analysisResult.sensitivity_level) }}
                    </el-tag>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item">
                    <span class="label">L/S值:</span>
                    <span class="value">{{ analysisResult.ls_value }}</span>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item">
                    <span class="label">分片数量:</span>
                    <span class="value">{{ analysisResult.shard_count }}</span>
                  </div>
                </el-col>
              </el-row>
            </div>

            <el-form-item class="form-actions">
              <el-button 
                type="primary" 
                @click="analyzeOrder"
                :loading="analyzing"
                :disabled="uploading"
              >
                <el-icon><Search /></el-icon>
                敏感度分析
              </el-button>
              <el-button 
                type="success" 
                @click="submitOrder"
                :loading="uploading"
                :disabled="!analysisResult || analyzing"
              >
                <el-icon><Upload /></el-icon>
                提交加密上传
              </el-button>
              <el-button @click="resetForm" :disabled="uploading || analyzing">
                <el-icon><Refresh /></el-icon>
                重置表单
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 批量上传 -->
      <el-tab-pane label="批量上传" name="batch">
        <el-card shadow="never" class="upload-card">
          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              :action="uploadUrl"
              :headers="uploadHeaders"
              :data="uploadData"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :on-progress="handleUploadProgress"
              :before-upload="beforeUpload"
              :file-list="fileList"
              accept=".csv,.xlsx,.json"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 CSV、Excel、JSON 格式，文件大小不超过10MB
                </div>
              </template>
            </el-upload>

            <!-- 模板下载 -->
            <div class="template-section">
              <el-divider content-position="left">数据模板</el-divider>
              <p>首次使用？下载数据模板了解正确的数据格式：</p>
              <el-button-group>
                <el-button @click="downloadTemplate('csv')">
                  <el-icon><Document /></el-icon>
                  CSV模板
                </el-button>
                <el-button @click="downloadTemplate('excel')">
                  <el-icon><Document /></el-icon>
                  Excel模板
                </el-button>
                <el-button @click="downloadTemplate('json')">
                  <el-icon><Document /></el-icon>
                  JSON模板
                </el-button>
              </el-button-group>
            </div>

            <!-- 上传进度 -->
            <div v-if="batchProgress.visible" class="progress-section">
              <el-divider content-position="left">上传进度</el-divider>
              <el-progress 
                :percentage="batchProgress.percentage" 
                :status="batchProgress.status"
              />
              <p class="progress-text">{{ batchProgress.text }}</p>
            </div>

            <!-- 上传结果 -->
            <div v-if="batchResult" class="result-section">
              <el-divider content-position="left">上传结果</el-divider>
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-statistic title="总记录数" :value="batchResult.total" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="成功" :value="batchResult.success" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="失败" :value="batchResult.failed" />
                </el-col>
                <el-col :span="6">
                  <el-statistic title="跳过" :value="batchResult.skipped" />
                </el-col>
              </el-row>
              
              <!-- 错误详情 -->
              <div v-if="batchResult.errors && batchResult.errors.length > 0" class="error-details">
                <h4>错误详情:</h4>
                <el-table :data="batchResult.errors" size="small" max-height="200">
                  <el-table-column prop="row" label="行号" width="80" />
                  <el-table-column prop="field" label="字段" width="120" />
                  <el-table-column prop="error" label="错误信息" />
                </el-table>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 最近上传记录 -->
    <el-card shadow="never" class="history-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近上传记录</span>
          <el-button type="text" @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </template>
      
      <el-table :data="uploadHistory" v-loading="historyLoading">
        <el-table-column prop="order_id" label="订单ID" width="120" />
        <el-table-column prop="customer_name" label="客户名称" width="120">
          <template #default="{ row }">
            {{ maskSensitiveData(row.customer_name) }}
          </template>
        </el-table-column>
        <el-table-column prop="sensitivity_level" label="敏感度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSensitivityTagType(row.sensitivity_level)" size="small">
              {{ getSensitivityLabel(row.sensitivity_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dvssAPI, orderAPI } from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'
import MainLayout from '@/components/MainLayout.vue'

const authStore = useAuthStore()

// 响应式数据
const activeTab = ref('single')
const uploading = ref(false)
const analyzing = ref(false)
const historyLoading = ref(false)

const orderFormRef = ref(null)
const uploadRef = ref(null)

// 表单数据
const orderForm = reactive({
  order_id: '',
  customer_name: '',
  customer_phone: '',
  order_amount: null,
  payment_method: '',
  bank_card_number: '',
  shipping_address: '',
  notes: ''
})

// 表单验证规则
const formRules = {
  order_id: [
    { required: true, message: '请输入订单ID', trigger: 'blur' }
  ],
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  customer_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  order_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' }
  ],
  payment_method: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ],
  shipping_address: [
    { required: true, message: '请输入收货地址', trigger: 'blur' }
  ]
}

// 分析结果
const analysisResult = ref(null)

// 批量上传相关
const fileList = ref([])
const batchProgress = reactive({
  visible: false,
  percentage: 0,
  status: '',
  text: ''
})
const batchResult = ref(null)

// 上传历史
const uploadHistory = ref([])

// 计算属性
const uploadUrl = computed(() => '/api/v1/dvss/batch-upload')
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}))
const uploadData = computed(() => ({
  uploader: authStore.currentUser?.username
}))

// 方法
const analyzeOrder = async () => {
  if (!orderFormRef.value) return
  
  const valid = await orderFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  analyzing.value = true
  try {
    const response = await dvssAPI.analyzeOrder(orderForm)
    if (response.data.success) {
      analysisResult.value = response.data.data
      ElMessage.success('敏感度分析完成')
    } else {
      throw new Error(response.data.message || '分析失败')
    }
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('敏感度分析失败: ' + error.message)
    // 模拟分析结果
    analysisResult.value = {
      sensitivity_level: 'medium',
      ls_value: 0.75,
      shard_count: 3,
      encryption_algorithm: 'AES-256'
    }
  } finally {
    analyzing.value = false
  }
}

const submitOrder = async () => {
  if (!analysisResult.value) {
    ElMessage.warning('请先进行敏感度分析')
    return
  }
  
  uploading.value = true
  try {
    const orderData = {
      ...orderForm,
      ...analysisResult.value
    }
    
    const response = await dvssAPI.uploadOrder(orderData)
    if (response.data.success) {
      ElMessage.success('订单上传成功，已记录到区块链')
      resetForm()
      refreshHistory()
    } else {
      throw new Error(response.data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('订单上传失败: ' + error.message)
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  if (orderFormRef.value) {
    orderFormRef.value.resetFields()
  }
  Object.assign(orderForm, {
    order_id: '',
    customer_name: '',
    customer_phone: '',
    order_amount: null,
    payment_method: '',
    bank_card_number: '',
    shipping_address: '',
    notes: ''
  })
  analysisResult.value = null
}

// 批量上传相关方法
const beforeUpload = (file) => {
  const isValidType = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只支持 CSV、Excel、JSON 格式文件')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  batchProgress.visible = true
  batchProgress.percentage = 0
  batchProgress.status = 'active'
  batchProgress.text = '准备上传...'
  
  return true
}

const handleUploadProgress = (event) => {
  batchProgress.percentage = Math.round(event.percent)
  batchProgress.text = `上传中... ${batchProgress.percentage}%`
}

const handleUploadSuccess = (response) => {
  batchProgress.status = 'success'
  batchProgress.text = '上传完成，正在处理数据...'
  
  if (response.success) {
    batchResult.value = response.data
    ElMessage.success('批量上传成功')
    refreshHistory()
  } else {
    ElMessage.error(response.message || '上传失败')
  }
  
  fileList.value = []
}

const handleUploadError = (error) => {
  batchProgress.status = 'exception'
  batchProgress.text = '上传失败'
  ElMessage.error('文件上传失败')
  console.error('Upload error:', error)
}

const downloadTemplate = (format) => {
  const templates = {
    csv: '/templates/order_template.csv',
    excel: '/templates/order_template.xlsx',
    json: '/templates/order_template.json'
  }
  
  const url = templates[format]
  if (url) {
    window.open(url, '_blank')
  } else {
    ElMessage.info(`${format.toUpperCase()} 模板下载功能开发中...`)
  }
}

const refreshHistory = async () => {
  historyLoading.value = true
  try {
    const response = await orderAPI.getRecentUploads({ limit: 10 })
    if (response.data.success) {
      uploadHistory.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    // 模拟数据
    uploadHistory.value = [
      {
        id: 1,
        order_id: 'ORD20231201001',
        customer_name: '张三',
        sensitivity_level: 'medium',
        status: 'completed',
        created_at: '2023-12-01 10:30:00'
      },
      {
        id: 2,
        order_id: 'ORD20231201002',
        customer_name: '李四',
        sensitivity_level: 'high',
        status: 'processing',
        created_at: '2023-12-01 14:20:00'
      }
    ]
  } finally {
    historyLoading.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info(`查看订单 ${row.order_id} 详情`)
  // 可以跳转到详情页或打开弹窗
}

// 工具方法
const maskSensitiveData = (value) => {
  if (!value) return 'N/A'
  const user = authStore.currentUser
  if (user && user.access_level >= 3) {
    return value
  }
  return '***'
}

const getSensitivityTagType = (level) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return types[level] || 'info'
}

const getSensitivityLabel = (level) => {
  const labels = {
    high: '高敏感',
    medium: '中敏感',
    low: '低敏感'
  }
  return labels[level] || '未知'
}

const getStatusTagType = (status) => {
  const types = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    pending: '待处理'
  }
  return labels[status] || '未知'
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.encrypt-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px;
  color: #303133;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.main-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.form-card, .upload-card, .history-card {
  border: none;
}

.order-form .el-form-item {
  margin-bottom: 20px;
}

.analysis-preview {
  margin: 20px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.analysis-item .label {
  font-weight: 500;
  color: #606266;
}

.analysis-item .value {
  font-weight: 600;
  color: #409eff;
}

.form-actions {
  text-align: center;
  margin-top: 30px;
}

.upload-demo {
  margin-bottom: 20px;
}

.template-section {
  margin: 30px 0;
  text-align: center;
}

.template-section p {
  margin-bottom: 15px;
  color: #606266;
}

.progress-section {
  margin: 20px 0;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  color: #606266;
}

.result-section {
  margin: 20px 0;
}

.error-details {
  margin-top: 20px;
}

.error-details h4 {
  margin-bottom: 10px;
  color: #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .encrypt-container {
    padding: 10px;
  }
  
  .main-tabs {
    padding: 10px;
  }
  
  .order-form .el-row {
    margin: 0;
  }
  
  .order-form .el-col {
    margin-bottom: 20px;
  }
}
</style>
