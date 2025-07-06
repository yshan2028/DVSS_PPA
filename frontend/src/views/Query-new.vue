<template>
  <div class="query-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>数据查询</h1>
      <p>根据您的权限查看和搜索订单数据</p>
    </div>

    <!-- 搜索和过滤区域 -->
    <el-card shadow="never" class="search-card">
      <el-form :model="searchForm" :inline="true" class="search-form">
        <el-form-item label="订单ID">
          <el-input 
            v-model="searchForm.orderId" 
            placeholder="请输入订单ID"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="客户名称" v-if="canViewCustomer">
          <el-input 
            v-model="searchForm.customerName" 
            placeholder="请输入客户名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        
        <el-form-item label="敏感度等级">
          <el-select 
            v-model="searchForm.sensitivityLevel" 
            placeholder="选择敏感度"
            clearable
            @clear="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="高敏感" value="high" />
            <el-option label="中敏感" value="medium" />
            <el-option label="低敏感" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleSearch"
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

    <!-- 操作按钮区域 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button 
          type="primary" 
          @click="$router.push('/encrypt')"
          v-if="canUploadData"
        >
          <el-icon><Upload /></el-icon>
          上传新数据
        </el-button>
        <el-button 
          @click="exportData"
          :disabled="!selectedRows.length"
        >
          <el-icon><Download /></el-icon>
          导出选中 ({{ selectedRows.length }})
        </el-button>
      </div>
      <div class="action-right">
        <span class="total-count">共 {{ pagination.total }} 条记录</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
        @row-click="handleRowClick"
        class="order-table"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="order_id" label="订单ID" width="120" fixed="left">
          <template #default="{ row }">
            <el-link type="primary" @click="viewOrderDetail(row)">
              {{ row.order_id }}
            </el-link>
          </template>
        </el-table-column>
        
        <!-- 根据权限显示不同字段 -->
        <el-table-column 
          v-if="canViewCustomer" 
          prop="customer_name" 
          label="客户名称" 
          width="120"
        >
          <template #default="{ row }">
            {{ getFieldValue(row, 'customer_name') }}
          </template>
        </el-table-column>
        
        <el-table-column prop="order_amount" label="订单金额" width="120">
          <template #default="{ row }">
            <span :class="getSensitivityClass(row, 'order_amount')">
              {{ getFieldValue(row, 'order_amount') }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="canViewPayment" 
          prop="payment_method" 
          label="支付方式" 
          width="120"
        >
          <template #default="{ row }">
            {{ getFieldValue(row, 'payment_method') }}
          </template>
        </el-table-column>
        
        <el-table-column 
          v-if="canViewShipping" 
          prop="shipping_address" 
          label="配送地址" 
          width="200"
        >
          <template #default="{ row }">
            <span :class="getSensitivityClass(row, 'shipping_address')">
              {{ getFieldValue(row, 'shipping_address') }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="sensitivity_level" label="敏感度" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="getSensitivityTagType(row.sensitivity_level)"
              size="small"
            >
              {{ getSensitivityLabel(row.sensitivity_level) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="text" 
              size="small" 
              @click="viewOrderDetail(row)"
            >
              查看详情
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="viewBlockchainRecord(row)"
            >
              区块链记录
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

    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="detailDialog.visible"
      title="订单详情"
      width="60%"
    >
      <div v-if="detailDialog.data" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单ID">
            {{ detailDialog.data.order_id }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(detailDialog.data.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="客户名称" v-if="canViewCustomer">
            {{ getFieldValue(detailDialog.data, 'customer_name') }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话" v-if="canViewCustomer">
            {{ getFieldValue(detailDialog.data, 'customer_phone') }}
          </el-descriptions-item>
          <el-descriptions-item label="订单金额">
            {{ getFieldValue(detailDialog.data, 'order_amount') }}
          </el-descriptions-item>
          <el-descriptions-item label="支付方式" v-if="canViewPayment">
            {{ getFieldValue(detailDialog.data, 'payment_method') }}
          </el-descriptions-item>
          <el-descriptions-item label="配送地址" v-if="canViewShipping" span="2">
            {{ getFieldValue(detailDialog.data, 'shipping_address') }}
          </el-descriptions-item>
          <el-descriptions-item label="敏感度等级">
            <el-tag :type="getSensitivityTagType(detailDialog.data.sensitivity_level)">
              {{ getSensitivityLabel(detailDialog.data.sensitivity_level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="L/S分析值">
            {{ detailDialog.data.ls_value || 'N/A' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 分片信息 -->
        <div v-if="detailDialog.data.shards" class="shard-info">
          <h4>数据分片信息</h4>
          <el-table :data="detailDialog.data.shards" size="small">
            <el-table-column prop="shard_id" label="分片ID" />
            <el-table-column prop="location" label="存储位置" />
            <el-table-column prop="encryption_algorithm" label="加密算法" />
            <el-table-column prop="created_at" label="创建时间" />
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialog.visible = false">关闭</el-button>
        <el-button type="primary" @click="viewBlockchainRecord(detailDialog.data)">
          查看区块链记录
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dvssAPI, orderAPI } from '@/api/index'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])

const searchForm = ref({
  orderId: '',
  customerName: '',
  sensitivityLevel: '',
  dateRange: null
})

const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

const detailDialog = ref({
  visible: false,
  data: null
})

// 计算属性 - 权限控制
const currentUser = computed(() => authStore.currentUser)

const canViewCustomer = computed(() => {
  const permissions = currentUser.value?.permissions || []
  return permissions.includes('read_customer') || permissions.includes('read_all')
})

const canViewPayment = computed(() => {
  const permissions = currentUser.value?.permissions || []
  return permissions.includes('read_payment') || permissions.includes('read_all')
})

const canViewShipping = computed(() => {
  const permissions = currentUser.value?.permissions || []
  return permissions.includes('read_shipping') || permissions.includes('read_all')
})

const canUploadData = computed(() => {
  const permissions = currentUser.value?.permissions || []
  return permissions.includes('write_order') || permissions.includes('manage')
})

// 方法
const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size,
      ...searchForm.value
    }
    
    if (searchForm.value.dateRange) {
      params.start_date = searchForm.value.dateRange[0]
      params.end_date = searchForm.value.dateRange[1]
    }
    
    const response = await orderAPI.getOrders(params)
    if (response.data.success) {
      tableData.value = response.data.data.orders || []
      pagination.value.total = response.data.data.total || 0
    }
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单数据失败')
    // 模拟数据
    tableData.value = [
      {
        id: 1,
        order_id: 'ORD20231201001',
        customer_name: currentUser.value?.access_level >= 3 ? '张三' : '***',
        customer_phone: currentUser.value?.access_level >= 3 ? '138****5678' : '***',
        order_amount: '299.00',
        payment_method: canViewPayment.value ? '支付宝' : '***',
        shipping_address: canViewShipping.value ? '北京市朝阳区**路**号' : '***',
        sensitivity_level: 'medium',
        ls_value: 0.75,
        created_at: '2023-12-01 10:30:00'
      },
      {
        id: 2,
        order_id: 'ORD20231201002',
        customer_name: currentUser.value?.access_level >= 3 ? '李四' : '***',
        customer_phone: currentUser.value?.access_level >= 3 ? '139****1234' : '***',
        order_amount: '1599.00',
        payment_method: canViewPayment.value ? '微信支付' : '***',
        shipping_address: canViewShipping.value ? '上海市浦东新区**街**弄' : '***',
        sensitivity_level: 'high',
        ls_value: 0.95,
        created_at: '2023-12-01 14:20:00'
      }
    ]
    pagination.value.total = 2
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  loadOrders()
}

const resetSearch = () => {
  searchForm.value = {
    orderId: '',
    customerName: '',
    sensitivityLevel: '',
    dateRange: null
  }
  handleSearch()
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleRowClick = (row) => {
  // 可以在这里添加行点击处理逻辑
}

const handleSizeChange = (newSize) => {
  pagination.value.size = newSize
  loadOrders()
}

const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  loadOrders()
}

const viewOrderDetail = (row) => {
  detailDialog.value.data = row
  detailDialog.value.visible = true
}

const viewBlockchainRecord = (row) => {
  ElMessage.info(`查看订单 ${row.order_id} 的区块链记录`)
  // 这里可以跳转到区块链审计页面或打开新的弹窗
}

const exportData = async () => {
  try {
    const orderIds = selectedRows.value.map(row => row.order_id)
    ElMessage.success(`导出 ${orderIds.length} 条记录`)
    // 这里可以调用导出API
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 工具方法
const getFieldValue = (row, field) => {
  const value = row[field]
  if (!value) return 'N/A'
  
  // 根据用户权限进行数据脱敏
  const user = currentUser.value
  if (!user) return '***'
  
  // 高敏感字段需要高权限
  if (['customer_phone', 'payment_method'].includes(field) && user.access_level < 4) {
    return '***'
  }
  
  // 地址信息部分脱敏
  if (field === 'shipping_address' && user.access_level < 3) {
    return value.replace(/\d+号.*/, '***')
  }
  
  return value
}

const getSensitivityClass = (row, field) => {
  // 根据字段敏感度添加样式类
  const sensitiveFields = ['order_amount', 'shipping_address', 'customer_phone']
  return sensitiveFields.includes(field) ? 'sensitive-field' : ''
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

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.query-container {
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

.order-table {
  margin-bottom: 20px;
}

.sensitive-field {
  background: rgba(245, 108, 108, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.order-detail {
  margin-bottom: 20px;
}

.shard-info {
  margin-top: 20px;
}

.shard-info h4 {
  margin-bottom: 10px;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .query-container {
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
}
</style>
