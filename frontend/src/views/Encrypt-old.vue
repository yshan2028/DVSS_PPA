<template>
  <div class="encrypt-page">
    <NavHeader />
    
    <el-container class="main-container">
      <el-aside width="240px" class="sidebar">
        <SideNavigation />
      </el-aside>
      
      <el-main class="content-area">
        <div class="page-header">
          <h1>{{ t('encrypt.title') }}</h1>
          <p class="page-description">{{ t('encrypt.description') }}</p>
        </div>

        <el-row :gutter="20">
          <!-- 数据输入区域 -->
          <el-col :span="12">
            <el-card class="input-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Edit /></el-icon>
                  <span>{{ t('encrypt.dataInput') }}</span>
                </div>
              </template>

              <el-form :model="encryptForm" label-position="top">
                <el-form-item :label="t('encrypt.customerName')">
                  <el-input v-model="encryptForm.customer_name" />
                </el-form-item>

                <el-form-item :label="t('encrypt.customerPhone')">
                  <el-input v-model="encryptForm.customer_phone" />
                </el-form-item>

                <el-form-item :label="t('encrypt.paymentAmount')">
                  <el-input-number 
                    v-model="encryptForm.payment_amount" 
                    :min="0" 
                    style="width: 100%"
                  />
                </el-form-item>

                <el-form-item :label="t('encrypt.bankCard')">
                  <el-input v-model="encryptForm.bank_card_number" />
                </el-form-item>

                <el-form-item :label="t('encrypt.deliveryAddress')">
                  <el-input 
                    v-model="encryptForm.delivery_address" 
                    type="textarea"
                    :rows="3"
                  />
                </el-form-item>

                <el-form-item :label="t('encrypt.identityCard')">
                  <el-input v-model="encryptForm.identity_card" />
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <!-- 加密参数区域 -->
          <el-col :span="12">
            <el-card class="params-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <el-icon><Setting /></el-icon>
                  <span>{{ t('encrypt.parameters') }}</span>
                </div>
              </template>

              <el-form :model="encryptParams" label-position="top">
                <el-form-item :label="t('encrypt.threshold')">
                  <el-slider
                    v-model="encryptParams.threshold"
                    :min="2"
                    :max="encryptParams.total_shares"
                    show-stops
                    show-input
                  />
                </el-form-item>

                <el-form-item :label="t('encrypt.totalShares')">
                  <el-slider
                    v-model="encryptParams.total_shares"
                    :min="3"
                    :max="10"
                    show-stops
                    show-input
                  />
                </el-form-item>

                <el-form-item>
                  <el-button 
                    type="primary" 
                    size="large" 
                    @click="handleEncrypt"
                    :loading="encrypting"
                    style="width: 100%"
                  >
                    <el-icon><Lock /></el-icon>
                    {{ t('encrypt.executeEncrypt') }}
                  </el-button>
                </el-form-item>
              </el-form>

              <!-- 实时L/S值预览 -->
              <div class="live-preview" v-if="!encrypting">
                <h4>{{ t('encrypt.livePreview') }}</h4>
                <el-row :gutter="16">
                  <el-col :span="12">
                    <div class="preview-item l-value">
                      <div class="preview-label">L {{ t('encrypt.privacyLevel') }}</div>
                      <div class="preview-value">{{ previewLValue.toFixed(2) }}</div>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="preview-item s-value">
                      <div class="preview-label">S {{ t('encrypt.securityLevel') }}</div>
                      <div class="preview-value">{{ previewSValue.toFixed(2) }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 结果区域 -->
        <el-card v-if="encryptResult" class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><SuccessFilled /></el-icon>
              <span>{{ t('encrypt.result') }}</span>
            </div>
          </template>

          <div class="result-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item :label="t('encrypt.dataId')">
                <el-tag type="success" size="large">{{ encryptResult.data_id }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('encrypt.blockchainHash')">
                <el-link type="primary" @click="viewBlockchainRecord">
                  {{ encryptResult.blockchain_hash }}
                </el-link>
              </el-descriptions-item>
              <el-descriptions-item :label="t('encrypt.lValue')">
                <span class="l-value-result">{{ encryptResult.l_value }}</span>
              </el-descriptions-item>
              <el-descriptions-item :label="t('encrypt.sValue')">
                <span class="s-value-result">{{ encryptResult.s_value }}</span>
              </el-descriptions-item>
            </el-descriptions>

            <div class="action-buttons">
              <el-button type="primary" @click="copyDataId">
                <el-icon><CopyDocument /></el-icon>
                {{ t('encrypt.copyId') }}
              </el-button>
              <el-button type="success" @click="queryEncryptedData">
                <el-icon><Search /></el-icon>
                {{ t('encrypt.queryData') }}
              </el-button>
              <el-button @click="resetForm">
                <el-icon><Refresh /></el-icon>
                {{ t('encrypt.reset') }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import api from '@/api/index'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Setting,
  Lock,
  SuccessFilled,
  CopyDocument,
  Search,
  Refresh
} from '@element-plus/icons-vue'

// 导入组件
import NavHeader from '@/components/NavHeader.vue'
import SideNavigation from '@/components/SideNavigation.vue'

const router = useRouter()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore

const encrypting = ref(false)
const encryptForm = ref({
  customer_name: '',
  customer_phone: '',
  payment_amount: 0,
  bank_card_number: '',
  delivery_address: '',
  identity_card: ''
})

const encryptParams = ref({
  threshold: 3,
  total_shares: 5
})

const encryptResult = ref(null)

// 实时L/S值计算
const previewLValue = computed(() => {
  // 简化计算逻辑
  const role = authStore.currentUser?.role
  if (!role) return 0
  
  const sensitivity = 3.5 // 平均敏感度
  const accessRatio = 0.6 // 访问比例
  return sensitivity * accessRatio * 10
})

const previewSValue = computed(() => {
  const thresholdRatio = (encryptParams.value.threshold / encryptParams.value.total_shares) * 100
  const roleCoeff = 1.0
  return thresholdRatio * roleCoeff
})

const handleEncrypt = async () => {
  encrypting.value = true
  try {
    const response = await api.post('/data/encrypt', {
      data: encryptForm.value,
      threshold: encryptParams.value.threshold,
      total_shares: encryptParams.value.total_shares
    })
    
    encryptResult.value = response.data
    ElMessage.success(t('encrypt.success'))
  } catch (error) {
    ElMessage.error(t('encrypt.failed'))
    console.error('加密失败:', error)
  } finally {
    encrypting.value = false
  }
}

const copyDataId = () => {
  if (encryptResult.value?.data_id) {
    navigator.clipboard.writeText(encryptResult.value.data_id)
    ElMessage.success(t('encrypt.idCopied'))
  }
}

const queryEncryptedData = () => {
  if (encryptResult.value?.data_id) {
    router.push({
      path: '/query',
      query: { id: encryptResult.value.data_id }
    })
  }
}

const viewBlockchainRecord = () => {
  router.push('/blockchain')
}

const resetForm = () => {
  encryptForm.value = {
    customer_name: '',
    customer_phone: '',
    payment_amount: 0,
    bank_card_number: '',
    delivery_address: '',
    identity_card: ''
  }
  encryptParams.value = {
    threshold: 3,
    total_shares: 5
  }
  encryptResult.value = null
}
</script>

<style scoped>
.encrypt-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.content-area {
  padding: 20px;
  overflow-y: auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  font-weight: bold;
}

.page-description {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.input-card, .params-card, .result-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.live-preview {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.live-preview h4 {
  margin-bottom: 15px;
  color: #303133;
}

.preview-item {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background: #F8F9FA;
}

.preview-item.l-value {
  border-left: 4px solid #409EFF;
}

.preview-item.s-value {
  border-left: 4px solid #67C23A;
}

.preview-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.preview-value {
  font-size: 20px;
  font-weight: bold;
}

.l-value .preview-value {
  color: #409EFF;
}

.s-value .preview-value {
  color: #67C23A;
}

.result-content {
  padding: 10px 0;
}

.l-value-result {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.s-value-result {
  font-size: 18px;
  font-weight: bold;
  color: #67C23A;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  justify-content: center;
}
</style>
