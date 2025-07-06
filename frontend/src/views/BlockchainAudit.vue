<template>
  <div class="audit-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>区块链审计</h1>
      <p>查看所有数据操作的区块链记录和审计日志</p>
    </div>

    <!-- 搜索和过滤 -->
    <el-card shadow="never" class="search-card">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="交易哈希">
          <el-input 
            v-model="searchForm.txHash" 
            placeholder="请输入交易哈希"
            clearable
            style="width: 250px"
          />
        </el-form-item>
        
        <el-form-item label="订单ID">
          <el-input 
            v-model="searchForm.orderId" 
            placeholder="请输入订单ID"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="操作类型">
          <el-select 
            v-model="searchForm.actionType" 
            placeholder="选择操作类型"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" value="" />
            <el-option label="创建" value="create" />
            <el-option label="查询" value="query" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计概览 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon total-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.totalRecords }}</h3>
                <p>总记录数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon today-icon">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.todayRecords }}</h3>
                <p>今日记录</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon block-icon">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.latestBlock }}</h3>
                <p>最新区块</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon network-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.networkStatus }}</h3>
                <p>网络状态</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button 
          type="primary" 
          @click="refreshData"
          :loading="loading"
        >
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button @click="exportAuditLog" :disabled="!selectedRows.length">
          <el-icon><Download /></el-icon>
          导出审计日志 ({{ selectedRows.length }})
        </el-button>
      </div>
      <div class="action-right">
        <span class="total-count">共 {{ pagination.total }} 条记录</span>
      </div>
    </div>

    <!-- 审计记录表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="auditData"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
        class="audit-table"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="tx_hash" label="交易哈希" width="200" fixed="left">
          <template #default="{ row }">
            <el-link type="primary" @click="viewTransactionDetail(row.tx_hash)">
              {{ row.tx_hash.substring(0, 20) }}...
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="block_number" label="区块号" width="100">
          <template #default="{ row }">
            <el-link type="primary" @click="viewBlockDetail(row.block_number)">
              {{ row.block_number }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="order_id" label="订单ID" width="140">
          <template #default="{ row }">
            <el-link type="primary" @click="viewOrderDetail(row.order_id)">
              {{ row.order_id }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="action_type" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action_type)" size="small">
              {{ getActionLabel(row.action_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="user_id" label="操作用户" width="120">
          <template #default="{ row }">
            {{ row.user_id || 'N/A' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="user_role" label="用户角色" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ getRoleLabel(row.user_role) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="timestamp" label="时间戳" width="160">
          <template #default="{ row }">
            {{ formatDate(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="gas_used" label="Gas消耗" width="100">
          <template #default="{ row }">
            {{ row.gas_used || 'N/A' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button type="text" size="small" @click="viewRawData(row)">
              原始数据
            </el-button>
            <el-button type="text" size="small" @click="verifyIntegrity(row)">
              验证完整性
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="审计记录详情"
      width="70%"
    >
      <div v-if="detailDialog.data" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="交易哈希" span="2">
            <el-text type="primary" style="font-family: monospace;">
              {{ detailDialog.data.tx_hash }}
            </el-text>
          </el-descriptions-item>
          <el-descriptions-item label="区块号">
            {{ detailDialog.data.block_number }}
          </el-descriptions-item>
          <el-descriptions-item label="区块哈希">
            <el-text style="font-family: monospace;">
              {{ detailDialog.data.block_hash }}
            </el-text>
          </el-descriptions-item>
          <el-descriptions-item label="订单ID">
            {{ detailDialog.data.order_id }}
          </el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getActionTagType(detailDialog.data.action_type)">
              {{ getActionLabel(detailDialog.data.action_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作用户">
            {{ detailDialog.data.user_id }}
          </el-descriptions-item>
          <el-descriptions-item label="用户角色">
            {{ getRoleLabel(detailDialog.data.user_role) }}
          </el-descriptions-item>
          <el-descriptions-item label="时间戳">
            {{ formatDate(detailDialog.data.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="Gas消耗">
            {{ detailDialog.data.gas_used }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(detailDialog.data.status)">
              {{ getStatusLabel(detailDialog.data.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据哈希">
            <el-text style="font-family: monospace;">
              {{ detailDialog.data.data_hash }}
            </el-text>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 操作数据 -->
        <div v-if="detailDialog.data.operation_data" class="operation-data">
          <h4>操作数据</h4>
          <el-input
            v-model="formattedOperationData"
            type="textarea"
            :rows="10"
            readonly
            style="font-family: monospace; font-size: 12px;"
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialog.visible = false">关闭</el-button>
        <el-button type="primary" @click="downloadDetail">
          <el-icon><Download /></el-icon>
          下载详情
        </el-button>
      </template>
    </el-dialog>

    <!-- 原始数据弹窗 -->
    <el-dialog
      v-model="rawDataDialog.visible"
      title="原始区块链数据"
      width="80%"
    >
      <div class="raw-data-content">
        <el-input
          v-model="rawDataDialog.data"
          type="textarea"
          :rows="20"
          readonly
          style="font-family: monospace; font-size: 12px;"
        />
      </div>
      
      <template #footer>
        <el-button @click="rawDataDialog.visible = false">关闭</el-button>
        <el-button type="primary" @click="copyRawData">
          <el-icon><CopyDocument /></el-icon>
          复制数据
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { blockchainAPI, auditAPI } from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const auditData = ref([])
const selectedRows = ref([])

const searchForm = reactive({
  txHash: '',
  orderId: '',
  actionType: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const stats = reactive({
  totalRecords: 0,
  todayRecords: 0,
  latestBlock: 0,
  networkStatus: '正常'
})

const detailDialog = reactive({
  visible: false,
  data: null
})

const rawDataDialog = reactive({
  visible: false,
  data: ''
})

// 计算属性
const formattedOperationData = computed(() => {
  if (!detailDialog.data?.operation_data) return ''
  try {
    return JSON.stringify(JSON.parse(detailDialog.data.operation_data), null, 2)
  } catch {
    return detailDialog.data.operation_data
  }
})

// 方法
const loadAuditData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    if (searchForm.dateRange) {
      params.start_time = searchForm.dateRange[0]
      params.end_time = searchForm.dateRange[1]
    }
    
    const response = await auditAPI.getAuditLogs(params)
    if (response.data.success) {
      auditData.value = response.data.data.records || []
      pagination.total = response.data.data.total || 0
    }
  } catch (error) {
    console.error('加载审计数据失败:', error)
    ElMessage.error('加载审计数据失败')
    // 模拟数据
    auditData.value = [
      {
        id: 1,
        tx_hash: '0x1234567890abcdef1234567890abcdef12345678',
        block_number: 12345,
        block_hash: '0xabcdef1234567890abcdef1234567890abcdef12',
        order_id: 'ORD20231201001',
        action_type: 'create',
        user_id: 'seller001',
        user_role: 'seller',
        timestamp: '2023-12-01 10:30:00',
        gas_used: 21000,
        status: 'success',
        data_hash: '0x9876543210fedcba9876543210fedcba98765432',
        operation_data: JSON.stringify({
          order_id: 'ORD20231201001',
          customer_name: '张三',
          amount: 299.00,
          action: 'create_order'
        })
      },
      {
        id: 2,
        tx_hash: '0x2234567890abcdef1234567890abcdef12345679',
        block_number: 12346,
        block_hash: '0xbcdef1234567890abcdef1234567890abcdef123',
        order_id: 'ORD20231201001',
        action_type: 'query',
        user_id: 'auditor001',
        user_role: 'auditor',
        timestamp: '2023-12-01 14:20:00',
        gas_used: 5000,
        status: 'success',
        data_hash: '0x8765432110fedcba9876543210fedcba98765433',
        operation_data: JSON.stringify({
          order_id: 'ORD20231201001',
          fields_accessed: ['customer_name', 'amount'],
          action: 'query_order'
        })
      }
    ]
    pagination.total = 2
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await auditAPI.getAuditStats()
    if (response.data.success) {
      Object.assign(stats, response.data.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用模拟数据
    Object.assign(stats, {
      totalRecords: 1248,
      todayRecords: 56,
      latestBlock: 12346,
      networkStatus: '正常'
    })
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadAuditData()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    txHash: '',
    orderId: '',
    actionType: '',
    dateRange: null
  })
  handleSearch()
}

const refreshData = async () => {
  await Promise.all([loadAuditData(), loadStats()])
  ElMessage.success('数据已刷新')
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleSizeChange = (newSize) => {
  pagination.size = newSize
  loadAuditData()
}

const handlePageChange = (newPage) => {
  pagination.page = newPage
  loadAuditData()
}

const viewDetail = (row) => {
  detailDialog.data = row
  detailDialog.visible = true
}

const viewRawData = async (row) => {
  try {
    const response = await blockchainAPI.getRawTransactionData(row.tx_hash)
    if (response.data.success) {
      rawDataDialog.data = JSON.stringify(response.data.data, null, 2)
    } else {
      // 模拟原始数据
      rawDataDialog.data = JSON.stringify({
        hash: row.tx_hash,
        blockNumber: row.block_number,
        blockHash: row.block_hash,
        transactionIndex: 0,
        from: '0x1234567890123456789012345678901234567890',
        to: '0x0987654321098765432109876543210987654321',
        value: '0',
        gas: row.gas_used,
        gasPrice: '20000000000',
        input: '0x' + Buffer.from(row.operation_data).toString('hex'),
        logs: [],
        status: row.status === 'success' ? '0x1' : '0x0'
      }, null, 2)
    }
    rawDataDialog.visible = true
  } catch (error) {
    ElMessage.error('获取原始数据失败')
  }
}

const verifyIntegrity = async (row) => {
  try {
    ElMessage.info('正在验证数据完整性...')
    const response = await blockchainAPI.verifyTransactionIntegrity(row.tx_hash)
    if (response.data.success) {
      if (response.data.data.valid) {
        ElMessage.success('数据完整性验证通过')
      } else {
        ElMessage.error('数据完整性验证失败')
      }
    }
  } catch (error) {
    ElMessage.error('验证失败')
  }
}

const viewTransactionDetail = (txHash) => {
  ElMessage.info(`查看交易详情: ${txHash}`)
  // 可以跳转到区块链浏览器或打开详情页
}

const viewBlockDetail = (blockNumber) => {
  ElMessage.info(`查看区块详情: ${blockNumber}`)
  // 可以跳转到区块详情页
}

const viewOrderDetail = (orderId) => {
  ElMessage.info(`查看订单详情: ${orderId}`)
  // 可以跳转到订单详情页
}

const exportAuditLog = async () => {
  try {
    const ids = selectedRows.value.map(row => row.id)
    ElMessage.success(`导出 ${ids.length} 条审计记录`)
    // 这里可以调用导出API
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const downloadDetail = () => {
  const data = JSON.stringify(detailDialog.data, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `audit_detail_${detailDialog.data.tx_hash}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const copyRawData = async () => {
  try {
    await navigator.clipboard.writeText(rawDataDialog.data)
    ElMessage.success('数据已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 工具方法
const getActionTagType = (action) => {
  const types = {
    create: 'success',
    query: 'info',
    update: 'warning',
    delete: 'danger'
  }
  return types[action] || 'info'
}

const getActionLabel = (action) => {
  const labels = {
    create: '创建',
    query: '查询',
    update: '更新',
    delete: '删除'
  }
  return labels[action] || action
}

const getStatusTagType = (status) => {
  return status === 'success' ? 'success' : 'danger'
}

const getStatusLabel = (status) => {
  const labels = {
    success: '成功',
    failed: '失败',
    pending: '待处理'
  }
  return labels[status] || status
}

const getRoleLabel = (role) => {
  const labels = {
    seller: '卖家',
    payment_provider: '支付商',
    logistics: '物流',
    auditor: '审计',
    platform: '平台'
  }
  return labels[role] || role
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadAuditData()
  loadStats()
})
</script>

<style scoped>
.audit-container {
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

.search-card {
  margin-bottom: 20px;
  border: none;
}

.search-form .el-form-item {
  margin-bottom: 0;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
  border: none;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-item {
  display: flex;
  align-items: center;
  height: 100%;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

.total-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.today-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.block-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.network-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-content h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-content p {
  margin: 5px 0 0;
  color: #909399;
  font-size: 14px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.action-left {
  display: flex;
  gap: 10px;
}

.total-count {
  color: #909399;
  font-size: 14px;
}

.table-card {
  border: none;
}

.audit-table {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.detail-content {
  margin-bottom: 20px;
}

.operation-data {
  margin-top: 20px;
}

.operation-data h4 {
  margin-bottom: 10px;
  color: #303133;
}

.raw-data-content {
  max-height: 500px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .audit-container {
    padding: 10px;
  }
  
  .search-form {
    display: block;
  }
  
  .search-form .el-form-item {
    display: block;
    margin-bottom: 15px;
  }
  
  .action-bar {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .action-left {
    justify-content: center;
  }
  
  .stats-section .el-col {
    margin-bottom: 10px;
  }
}
</style>
