<template>
  <div class="query-page">
    <NavHeader />
    
    <el-container class="main-container">
      <el-aside width="240px" class="sidebar">
        <SideNavigation />
      </el-aside>
      
      <el-main class="content-area">
        <div class="page-header">
          <h1>{{ t('query.title') }}</h1>
          <p class="page-description">{{ t('query.description') }}</p>
        </div>

        <!-- 查询输入区域 -->
        <el-card class="query-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>{{ t('query.dataQuery') }}</span>
            </div>
          </template>

          <el-form inline class="query-form">
            <el-form-item :label="t('query.dataId')">
              <el-input
                v-model="queryId"
                :placeholder="t('query.enterDataId')"
                style="width: 300px;"
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="handleQuery"
                :loading="querying"
              >
                <el-icon><Search /></el-icon>
                {{ t('query.execute') }}
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 当前用户信息 -->
          <div class="user-context" v-if="authStore.isLoggedIn">
            <el-alert
              :title="t('query.currentUser') + ': ' + authStore.currentUser?.username"
              type="info"
              :description="t('query.roleDescription') + ': ' + getRoleLabel(authStore.currentUser?.role)"
              show-icon
              :closable="false"
            />
          </div>
        </el-card>

        <!-- 查询结果区域 -->
        <el-card v-if="queryResult" class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>{{ t('query.result') }}</span>
              <el-tag :type="getResultTagType(queryResult.status)">
                {{ queryResult.status }}
              </el-tag>
            </div>
          </template>

          <div class="result-content">
            <!-- 数据字段显示 -->
            <div class="data-fields">
              <h4>{{ t('query.dataFields') }}</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item
                  v-for="(value, key) in queryResult.decrypted_data"
                  :key="key"
                  :label="getFieldLabel(key)"
                >
                  <span v-if="value !== null" class="field-value">{{ value }}</span>
                  <el-tag v-else type="warning" size="small">{{ t('query.noAccess') }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 隐私分析 -->
            <div class="privacy-analysis" v-if="queryResult.privacy_analysis">
              <h4>{{ t('query.privacyAnalysis') }}</h4>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="analysis-item">
                    <div class="analysis-label">{{ t('query.accessibleFields') }}</div>
                    <div class="analysis-value">
                      {{ queryResult.privacy_analysis.accessible_field_count }} / {{ queryResult.privacy_analysis.total_field_count }}
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item l-value">
                    <div class="analysis-label">L {{ t('query.privacyLevel') }}</div>
                    <div class="analysis-value">{{ queryResult.privacy_analysis.l_value }}</div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="analysis-item s-value">
                    <div class="analysis-label">S {{ t('query.securityLevel') }}</div>
                    <div class="analysis-value">{{ queryResult.privacy_analysis.s_value }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 区块链记录 -->
            <div class="blockchain-info" v-if="queryResult.blockchain_hash">
              <h4>{{ t('query.blockchainRecord') }}</h4>
              <el-card class="blockchain-card" shadow="never">
                <div class="blockchain-content">
                  <div class="blockchain-item">
                    <span class="blockchain-label">{{ t('query.hash') }}:</span>
                    <el-link type="primary" @click="viewBlockchainRecord">
                      {{ queryResult.blockchain_hash }}
                    </el-link>
                  </div>
                  <div class="blockchain-item">
                    <span class="blockchain-label">{{ t('query.timestamp') }}:</span>
                    <span>{{ formatTimestamp(queryResult.timestamp) }}</span>
                  </div>
                </div>
              </el-card>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button type="primary" @click="exportResult">
                <el-icon><Download /></el-icon>
                {{ t('query.export') }}
              </el-button>
              <el-button @click="queryAnother">
                <el-icon><Plus /></el-icon>
                {{ t('query.queryAnother') }}
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 历史查询记录 -->
        <el-card class="history-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>{{ t('query.history') }}</span>
            </div>
          </template>

          <el-table :data="queryHistory" style="width: 100%">
            <el-table-column prop="data_id" :label="t('query.dataId')" width="200" />
            <el-table-column prop="timestamp" :label="t('query.timestamp')" width="180">
              <template #default="scope">
                {{ formatTimestamp(scope.row.timestamp) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="t('query.status')" width="120">
              <template #default="scope">
                <el-tag :type="getResultTagType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('query.actions')">
              <template #default="scope">
                <el-button type="text" @click="requery(scope.row.data_id)">
                  {{ t('query.requery') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import { dataAPI } from '@/api/index'
import { ElMessage } from 'element-plus'
import {
  Search,
  Document,
  Download,
  Plus,
  Clock
} from '@element-plus/icons-vue'

// 导入组件
import NavHeader from '@/components/NavHeader.vue'
import SideNavigation from '@/components/SideNavigation.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore

const querying = ref(false)
const queryId = ref('')
const queryResult = ref(null)
const queryHistory = ref([])

// 字段标签映射
const fieldLabels = {
  customer_name: 'query.customerName',
  customer_phone: 'query.customerPhone',
  payment_amount: 'query.paymentAmount',
  bank_card_number: 'query.bankCard',
  delivery_address: 'query.deliveryAddress',
  identity_card: 'query.identityCard'
}

const getRoleLabel = (role) => {
  const labels = {
    seller: t('roles.seller'),
    payment_provider: t('roles.payment'),
    logistics: t('roles.logistics'),
    auditor: t('roles.auditor'),
    platform: t('roles.platform')
  }
  return labels[role] || role
}

const getFieldLabel = (field) => {
  return t(fieldLabels[field] || field)
}

const getResultTagType = (status) => {
  const types = {
    success: 'success',
    partial: 'warning',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const handleQuery = async () => {
  if (!queryId.value.trim()) {
    ElMessage.warning(t('query.enterDataId'))
    return
  }

  querying.value = true
  try {
    // 使用新的dataAPI.query方法
    const response = await dataAPI.query(queryId.value, authStore.currentUser?.id)
    queryResult.value = response
    
    // 添加到历史记录
    addToHistory(queryId.value, response.status)
    
    ElMessage.success(t('query.success'))
  } catch (error) {
    ElMessage.error(t('query.failed'))
    console.error('查询失败:', error)
  } finally {
    querying.value = false
  }
}

const addToHistory = (dataId, status) => {
  const historyItem = {
    data_id: dataId,
    status: status,
    timestamp: new Date().toISOString()
  }
  queryHistory.value.unshift(historyItem)
  
  // 只保留最近20条记录
  if (queryHistory.value.length > 20) {
    queryHistory.value = queryHistory.value.slice(0, 20)
  }
  
  // 保存到本地存储
  localStorage.setItem('query_history', JSON.stringify(queryHistory.value))
}

const loadHistory = () => {
  const saved = localStorage.getItem('query_history')
  if (saved) {
    queryHistory.value = JSON.parse(saved)
  }
}

const requery = (dataId) => {
  queryId.value = dataId
  handleQuery()
}

const queryAnother = () => {
  queryId.value = ''
  queryResult.value = null
}

const exportResult = () => {
  if (!queryResult.value) return
  
  const data = JSON.stringify(queryResult.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `query_result_${queryId.value}.json`
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success(t('query.exported'))
}

const viewBlockchainRecord = () => {
  router.push('/blockchain')
}

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

onMounted(() => {
  loadHistory()
  
  // 如果URL中有查询参数，自动填入
  if (route.query.id) {
    queryId.value = route.query.id
    handleQuery()
  }
})
</script>

<style scoped>
.query-page {
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

.query-card, .result-card, .history-card {
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

.query-form {
  display: flex;
  align-items: end;
  gap: 20px;
}

.user-context {
  margin-top: 20px;
}

.result-content {
  padding: 10px 0;
}

.data-fields, .privacy-analysis, .blockchain-info {
  margin-bottom: 30px;
}

.data-fields h4, .privacy-analysis h4, .blockchain-info h4 {
  margin-bottom: 15px;
  color: #303133;
}

.field-value {
  font-weight: 500;
}

.analysis-item {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background: #F8F9FA;
}

.analysis-item.l-value {
  border-left: 4px solid #409EFF;
}

.analysis-item.s-value {
  border-left: 4px solid #67C23A;
}

.analysis-label {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.analysis-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.l-value .analysis-value {
  color: #409EFF;
}

.s-value .analysis-value {
  color: #67C23A;
}

.blockchain-card {
  background: #F8F9FA;
}

.blockchain-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.blockchain-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.blockchain-label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}
</style>
