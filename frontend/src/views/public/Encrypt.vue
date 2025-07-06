<template>
  <div class="encrypt-page">
    <div class="page-header">
      <h1>数据加密服务</h1>
      <p>使用先进的加密算法保护您的敏感数据</p>
    </div>

    <el-row :gutter="20">
      <!-- 加密配置 -->
      <el-col :span="10">
        <el-card class="encrypt-config-card">
          <template #header>
            <div class="card-header">
              <span>加密配置</span>
              <el-button type="text" @click="resetForm">重置</el-button>
            </div>
          </template>
          
          <el-form :model="encryptForm" ref="encryptFormRef" label-width="120px">
            <el-form-item label="数据类型" required>
              <el-select v-model="encryptForm.data_type" placeholder="请选择数据类型" style="width: 100%">
                <el-option label="文本数据" value="text" />
                <el-option label="文件数据" value="file" />
                <el-option label="JSON数据" value="json" />
                <el-option label="CSV数据" value="csv" />
              </el-select>
            </el-form-item>

            <el-form-item label="加密算法" required>
              <el-select v-model="encryptForm.algorithm" placeholder="请选择加密算法" style="width: 100%">
                <el-option label="AES-256" value="AES256">
                  <span>AES-256</span>
                  <span style="float: right; color: #8cc8ff; font-size: 13px">推荐</span>
                </el-option>
                <el-option label="RSA-2048" value="RSA2048" />
                <el-option label="ChaCha20" value="ChaCha20" />
                <el-option label="SM4 (国密)" value="SM4" />
              </el-select>
            </el-form-item>

            <el-form-item label="敏感度级别" required>
              <el-select v-model="encryptForm.sensitivity_level" placeholder="请选择敏感度级别" style="width: 100%">
                <el-option label="低敏感" value="low">
                  <span>低敏感</span>
                  <el-tag size="small" type="success" style="margin-left: 8px">公开</el-tag>
                </el-option>
                <el-option label="中敏感" value="medium">
                  <span>中敏感</span>
                  <el-tag size="small" type="warning" style="margin-left: 8px">内部</el-tag>
                </el-option>
                <el-option label="高敏感" value="high">
                  <span>高敏感</span>
                  <el-tag size="small" type="danger" style="margin-left: 8px">机密</el-tag>
                </el-option>
                <el-option label="极敏感" value="critical">
                  <span>极敏感</span>
                  <el-tag size="small" type="danger" style="margin-left: 8px">绝密</el-tag>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="分片设置">
              <div class="shard-config">
                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-input-number 
                      v-model="encryptForm.shard_count" 
                      :min="1" 
                      :max="10"
                      placeholder="分片数量"
                      style="width: 100%"
                    />
                  </el-col>
                  <el-col :span="12">
                    <el-input-number 
                      v-model="encryptForm.threshold" 
                      :min="1" 
                      :max="encryptForm.shard_count"
                      placeholder="恢复阈值"
                      style="width: 100%"
                    />
                  </el-col>
                </el-row>
                <div class="shard-description">
                  <small>将数据分为 {{ encryptForm.shard_count }} 片，需要 {{ encryptForm.threshold }} 片才能恢复</small>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="数据输入" required>
              <el-tabs v-model="inputTab" class="input-tabs">
                <el-tab-pane label="文本输入" name="text">
                  <el-input
                    v-model="encryptForm.input_data"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入要加密的数据..."
                    show-word-limit
                    maxlength="10000"
                  />
                </el-tab-pane>
                <el-tab-pane label="文件上传" name="file">
                  <el-upload
                    ref="uploadRef"
                    class="upload-demo"
                    drag
                    action="#"
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :show-file-list="false"
                    accept=".txt,.csv,.json"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      将文件拖到此处，或<em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        支持 txt/csv/json 文件，且不超过 10MB
                      </div>
                    </template>
                  </el-upload>
                  <div v-if="uploadedFile" class="uploaded-file">
                    <el-icon><Document /></el-icon>
                    <span>{{ uploadedFile.name }}</span>
                    <el-button type="text" @click="removeFile">移除</el-button>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="startEncryption" 
                :loading="encrypting"
                :disabled="!canEncrypt"
                style="width: 100%"
                size="large"
              >
                <el-icon><Lock /></el-icon>
                开始加密
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 加密结果 -->
      <el-col :span="14">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>加密结果</span>
              <div class="result-actions" v-if="encryptResult.success">
                <el-button type="text" @click="downloadResult">
                  <el-icon><Download /></el-icon>
                  下载
                </el-button>
                <el-button type="text" @click="shareResult">
                  <el-icon><Share /></el-icon>
                  分享
                </el-button>
              </div>
            </div>
          </template>

          <div v-loading="encrypting" class="result-content">
            <!-- 空状态 -->
            <div v-if="!encryptResult.data && !encrypting" class="empty-result">
              <el-empty description="请配置加密参数并开始加密" />
            </div>

            <!-- 加密成功 -->
            <div v-else-if="encryptResult.success" class="success-result">
              <div class="result-summary">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="加密算法">{{ encryptResult.algorithm }}</el-descriptions-item>
                  <el-descriptions-item label="分片数量">{{ encryptResult.shard_count }}</el-descriptions-item>
                  <el-descriptions-item label="数据大小">{{ formatBytes(encryptResult.original_size) }}</el-descriptions-item>
                  <el-descriptions-item label="加密时间">{{ encryptResult.encrypt_time }}ms</el-descriptions-item>
                  <el-descriptions-item label="加密ID" span="2">{{ encryptResult.encrypt_id }}</el-descriptions-item>
                </el-descriptions>
              </div>

              <!-- 分片信息 -->
              <div class="shard-info" style="margin-top: 20px">
                <h4>分片信息</h4>
                <el-table :data="encryptResult.shards" style="width: 100%">
                  <el-table-column prop="shard_id" label="分片ID" width="200" />
                  <el-table-column prop="size" label="大小">
                    <template #default="{ row }">
                      {{ formatBytes(row.size) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="hash" label="哈希值" show-overflow-tooltip />
                  <el-table-column label="操作" width="120">
                    <template #default="{ row }">
                      <el-button type="text" size="small" @click="downloadShard(row)">
                        下载
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>

              <!-- 区块链记录 -->
              <div class="blockchain-info" style="margin-top: 20px">
                <h4>区块链记录</h4>
                <el-alert
                  title="加密操作已记录到区块链"
                  type="success"
                  :closable="false"
                  show-icon
                >
                  <template #default>
                    <p>交易哈希: {{ encryptResult.tx_hash }}</p>
                    <p>区块高度: {{ encryptResult.block_height }}</p>
                  </template>
                </el-alert>
              </div>
            </div>

            <!-- 加密失败 -->
            <div v-else-if="encryptResult.error" class="error-result">
              <el-alert
                title="加密失败"
                :description="encryptResult.error"
                type="error"
                show-icon
                :closable="false"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 加密历史 -->
    <el-card class="history-card" style="margin-top: 20px">
      <template #header>
        <span>加密历史</span>
      </template>
      <el-table :data="encryptHistory" style="width: 100%">
        <el-table-column prop="encrypt_id" label="加密ID" width="200" />
        <el-table-column prop="algorithm" label="算法" width="120" />
        <el-table-column prop="sensitivity_level" label="敏感度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSensitivityColor(row.sensitivity_level)">
              {{ getSensitivityText(row.sensitivity_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shard_count" label="分片数" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewEncryptDetail(row)">
              查看详情
            </el-button>
            <el-button type="text" size="small" @click="downloadEncryptResult(row)">
              下载结果
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Lock, Download, Share, UploadFilled, Document } from '@element-plus/icons-vue'

const encrypting = ref(false)
const inputTab = ref('text')
const uploadedFile = ref(null)
const encryptFormRef = ref()
const uploadRef = ref()

const encryptForm = reactive({
  data_type: 'text',
  algorithm: 'AES256',
  sensitivity_level: 'medium',
  shard_count: 3,
  threshold: 2,
  input_data: ''
})

const encryptResult = reactive({
  success: false,
  data: null,
  algorithm: '',
  shard_count: 0,
  original_size: 0,
  encrypt_time: 0,
  encrypt_id: '',
  shards: [],
  tx_hash: '',
  block_height: 0,
  error: null
})

const encryptHistory = ref([])

const canEncrypt = computed(() => {
  if (inputTab.value === 'text') {
    return encryptForm.input_data.trim().length > 0
  } else {
    return uploadedFile.value !== null
  }
})

const getSensitivityColor = (level) => {
  const colorMap = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return colorMap[level] || ''
}

const getSensitivityText = (level) => {
  const textMap = {
    'low': '低敏感',
    'medium': '中敏感',
    'high': '高敏感',
    'critical': '极敏感'
  }
  return textMap[level] || level
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const handleFileChange = (file) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  uploadedFile.value = file
  // 读取文件内容
  const reader = new FileReader()
  reader.onload = (e) => {
    encryptForm.input_data = e.target.result
  }
  reader.readAsText(file.raw)
}

const removeFile = () => {
  uploadedFile.value = null
  encryptForm.input_data = ''
  uploadRef.value?.clearFiles()
}

const resetForm = () => {
  Object.assign(encryptForm, {
    data_type: 'text',
    algorithm: 'AES256',
    sensitivity_level: 'medium',
    shard_count: 3,
    threshold: 2,
    input_data: ''
  })
  uploadedFile.value = null
  inputTab.value = 'text'
  encryptResult.success = false
  encryptResult.error = null
}

const startEncryption = async () => {
  if (!canEncrypt.value) {
    ElMessage.warning('请输入要加密的数据')
    return
  }

  encrypting.value = true
  try {
    // 模拟加密过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 模拟加密结果
    const mockResult = {
      success: true,
      algorithm: encryptForm.algorithm,
      shard_count: encryptForm.shard_count,
      original_size: new Blob([encryptForm.input_data]).size,
      encrypt_time: Math.floor(Math.random() * 1000) + 500,
      encrypt_id: 'ENC_' + Date.now(),
      shards: Array.from({ length: encryptForm.shard_count }, (_, i) => ({
        shard_id: `SHARD_${i + 1}_${Date.now()}`,
        size: Math.floor(Math.random() * 1000) + 500,
        hash: `hash_${Math.random().toString(36).substr(2, 9)}`
      })),
      tx_hash: '0x' + Math.random().toString(16).substr(2, 64),
      block_height: Math.floor(Math.random() * 1000000) + 500000,
      error: null
    }

    Object.assign(encryptResult, mockResult)
    
    // 添加到历史记录
    encryptHistory.value.unshift({
      encrypt_id: mockResult.encrypt_id,
      algorithm: mockResult.algorithm,
      sensitivity_level: encryptForm.sensitivity_level,
      shard_count: mockResult.shard_count,
      created_at: new Date().toISOString(),
      status: 'success'
    })

    ElMessage.success('数据加密成功')
  } catch (error) {
    encryptResult.error = error.message || '加密过程中发生错误'
    encryptResult.success = false
    ElMessage.error('数据加密失败')
  } finally {
    encrypting.value = false
  }
}

const downloadResult = () => {
  ElMessage.info('下载功能开发中')
}

const shareResult = () => {
  ElMessage.info('分享功能开发中')
}

const downloadShard = (shard) => {
  ElMessage.info(`下载分片 ${shard.shard_id}`)
}

const viewEncryptDetail = (record) => {
  ElMessage.info(`查看加密详情: ${record.encrypt_id}`)
}

const downloadEncryptResult = (record) => {
  ElMessage.info(`下载加密结果: ${record.encrypt_id}`)
}

const loadEncryptHistory = () => {
  // 模拟历史数据
  encryptHistory.value = [
    {
      encrypt_id: 'ENC_1642751234567',
      algorithm: 'AES256',
      sensitivity_level: 'high',
      shard_count: 3,
      created_at: '2024-01-20T10:30:00Z',
      status: 'success'
    },
    {
      encrypt_id: 'ENC_1642637834567',
      algorithm: 'RSA2048',
      sensitivity_level: 'medium',
      shard_count: 5,
      created_at: '2024-01-19T15:20:00Z',
      status: 'success'
    }
  ]
}

onMounted(() => {
  loadEncryptHistory()
})
</script>

<style scoped>
.encrypt-page {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #606266;
  font-size: 1.1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.encrypt-config-card {
  min-height: 600px;
}

.shard-config {
  width: 100%;
}

.shard-description {
  margin-top: 8px;
  text-align: center;
  color: #909399;
}

.input-tabs {
  width: 100%;
}

.upload-demo {
  width: 100%;
}

.uploaded-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.result-card {
  min-height: 600px;
}

.result-content {
  min-height: 500px;
}

.empty-result {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.success-result {
  padding: 16px 0;
}

.error-result {
  padding: 16px 0;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.history-card {
  margin-top: 20px;
}

.result-summary {
  margin-bottom: 20px;
}

.shard-info h4,
.blockchain-info h4 {
  margin-bottom: 12px;
  color: #303133;
}
</style>
