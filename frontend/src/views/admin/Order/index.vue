<template>
  <div class="order-management">
    <div class="page-header">
      <h2>订单管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新增订单
        </el-button>
        <el-button type="success" @click="showBatchEncryptDialog = true">
          <el-icon><Lock /></el-icon>
          批量加密
        </el-button>
      </div>
    </div>

    <!-- 搜索过滤器 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="100px" inline>
        <el-form-item label="订单ID">
          <el-input 
            v-model="searchForm.order_id" 
            placeholder="请输入订单ID"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input 
            v-model="searchForm.customer_name" 
            placeholder="请输入客户名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="加密状态">
          <el-select v-model="searchForm.is_encrypted" placeholder="请选择加密状态" clearable style="width: 120px">
            <el-option label="未加密" :value="false" />
            <el-option label="已加密" :value="true" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchOrders">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="table-card">
      <el-table 
        :data="orderList" 
        v-loading="loading"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="订单ID" width="120" />
        <el-table-column prop="customer_name" label="客户名称" />
        <el-table-column prop="customer_phone" label="客户电话" />
        <el-table-column prop="product_name" label="产品名称" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="unit_price" label="单价" width="100">
          <template #default="{ row }">
            ¥{{ row.unit_price }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="120">
          <template #default="{ row }">
            ¥{{ row.total_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_encrypted" label="加密状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_encrypted ? 'success' : 'info'">
              {{ row.is_encrypted ? '已加密' : '未加密' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewOrder(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="editOrder(row)" v-if="!row.is_encrypted">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="encryptOrder(row)" v-if="!row.is_encrypted">
              加密
            </el-button>
            <el-button type="info" size="small" @click="viewShards(row)" v-if="row.is_encrypted">
              查看分片
            </el-button>
            <el-button type="danger" size="small" @click="deleteOrder(row)" v-if="!row.is_encrypted">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑订单对话框 -->
    <el-dialog 
      :title="editingOrder ? '编辑订单' : '新增订单'" 
      v-model="showCreateDialog"
      width="600px"
    >
      <el-form :model="orderForm" :rules="orderRules" ref="orderFormRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名" prop="customer_name">
              <el-input v-model="orderForm.customer_name" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户电话" prop="customer_phone">
              <el-input v-model="orderForm.customer_phone" placeholder="请输入客户电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户邮箱" prop="customer_email">
              <el-input v-model="orderForm.customer_email" placeholder="请输入客户邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="product_name">
              <el-input v-model="orderForm.product_name" placeholder="请输入产品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量" prop="quantity">
              <el-input-number 
                v-model="orderForm.quantity" 
                :min="1" 
                style="width: 100%"
                @change="calculateTotal"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价" prop="unit_price">
              <el-input-number 
                v-model="orderForm.unit_price" 
                :min="0" 
                :precision="2"
                style="width: 100%"
                @change="calculateTotal"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总金额">
              <el-input :value="orderForm.total_amount" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="订单状态" prop="status">
          <el-select v-model="orderForm.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input 
            v-model="orderForm.notes" 
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveOrder" :loading="saving">
          {{ editingOrder ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看订单对话框 -->
    <el-dialog title="订单详情" v-model="showViewDialog" width="600px">
      <div class="order-detail" v-if="viewingOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单ID">{{ viewingOrder.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(viewingOrder.status)">
              {{ getStatusText(viewingOrder.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户姓名">{{ viewingOrder.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="客户电话">{{ viewingOrder.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="客户邮箱">{{ viewingOrder.customer_email }}</el-descriptions-item>
          <el-descriptions-item label="产品名称">{{ viewingOrder.product_name }}</el-descriptions-item>
          <el-descriptions-item label="数量">{{ viewingOrder.quantity }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ viewingOrder.unit_price }}</el-descriptions-item>
          <el-descriptions-item label="总金额">¥{{ viewingOrder.total_amount }}</el-descriptions-item>
          <el-descriptions-item label="加密状态">
            <el-tag :type="viewingOrder.is_encrypted ? 'success' : 'info'">
              {{ viewingOrder.is_encrypted ? '已加密' : '未加密' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(viewingOrder.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(viewingOrder.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="备注" span="2">{{ viewingOrder.notes || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 批量加密对话框 -->
    <el-dialog title="批量加密订单" v-model="showBatchEncryptDialog" width="500px">
      <div class="batch-encrypt">
        <el-alert
          title="提示"
          type="info"
          description="选择要加密的订单，加密后的订单将无法直接查看原始数据。"
          :closable="false"
          style="margin-bottom: 20px"
        />
        <div class="selected-orders">
          <div class="selected-count">
            已选择 {{ selectedOrders.length }} 个订单
          </div>
          <div class="order-list" v-if="selectedOrders.length > 0">
            <div 
              v-for="order in selectedOrders" 
              :key="order.id" 
              class="order-item"
            >
              <span>{{ order.id }} - {{ order.customer_name }}</span>
              <el-tag size="small">¥{{ order.total_amount }}</el-tag>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showBatchEncryptDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="batchEncryptOrders" 
          :loading="saving"
          :disabled="selectedOrders.length === 0"
        >
          开始加密
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Lock } from '@element-plus/icons-vue'
import { orderApi } from '@/api/order'

const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const showBatchEncryptDialog = ref(false)
const editingOrder = ref(null)
const viewingOrder = ref(null)
const selectedOrders = ref([])

const orderList = ref([])
const dateRange = ref([])

const searchForm = reactive({
  order_id: '',
  customer_name: '',
  status: '',
  is_encrypted: null,
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const orderForm = reactive({
  customer_name: '',
  customer_phone: '',
  customer_email: '',
  product_name: '',
  quantity: 1,
  unit_price: 0,
  total_amount: 0,
  status: 'pending',
  notes: ''
})

const orderFormRef = ref()

const orderRules = {
  customer_name: [
    { required: true, message: '请输入客户姓名', trigger: 'blur' }
  ],
  customer_phone: [
    { required: true, message: '请输入客户电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  customer_email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  product_name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' }
  ],
  quantity: [
    { required: true, message: '请输入数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价不能小于0', trigger: 'blur' }
  ]
}

const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'processing': 'info',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusMap[status] || status
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const calculateTotal = () => {
  orderForm.total_amount = (orderForm.quantity * orderForm.unit_price).toFixed(2)
}

const loadOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') {
        delete params[key]
      }
    })

    const response = await orderApi.getOrderList(params)
    if (response.code === 200) {
      orderList.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载订单列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchOrders = () => {
  pagination.page = 1
  loadOrders()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    order_id: '',
    customer_name: '',
    status: '',
    is_encrypted: null,
    start_date: '',
    end_date: ''
  })
  dateRange.value = []
  pagination.page = 1
  loadOrders()
}

const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadOrders()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadOrders()
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection.filter(order => !order.is_encrypted)
}

const viewOrder = (order) => {
  viewingOrder.value = order
  showViewDialog.value = true
}

const editOrder = (order) => {
  editingOrder.value = order
  Object.assign(orderForm, {
    customer_name: order.customer_name,
    customer_phone: order.customer_phone,
    customer_email: order.customer_email,
    product_name: order.product_name,
    quantity: order.quantity,
    unit_price: order.unit_price,
    total_amount: order.total_amount,
    status: order.status,
    notes: order.notes
  })
  showCreateDialog.value = true
}

const resetForm = () => {
  Object.assign(orderForm, {
    customer_name: '',
    customer_phone: '',
    customer_email: '',
    product_name: '',
    quantity: 1,
    unit_price: 0,
    total_amount: 0,
    status: 'pending',
    notes: ''
  })
  editingOrder.value = null
  orderFormRef.value?.resetFields()
}

const saveOrder = async () => {
  if (!orderFormRef.value) return
  
  const valid = await orderFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingOrder.value) {
      const response = await orderApi.updateOrder(editingOrder.value.id, orderForm)
      if (response.code === 200) {
        ElMessage.success('订单更新成功')
        showCreateDialog.value = false
        resetForm()
        loadOrders()
      }
    } else {
      const response = await orderApi.createOrder(orderForm)
      if (response.code === 200) {
        ElMessage.success('订单创建成功')
        showCreateDialog.value = false
        resetForm()
        loadOrders()
      }
    }
  } catch (error) {
    ElMessage.error(editingOrder.value ? '订单更新失败' : '订单创建失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const encryptOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要加密订单 "${order.id}" 吗？加密后将无法直接查看原始数据。`,
      '确认加密',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await orderApi.encryptOrder(order.id)
    if (response.code === 200) {
      ElMessage.success('订单加密成功')
      loadOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('订单加密失败')
      console.error(error)
    }
  }
}

const batchEncryptOrders = async () => {
  if (selectedOrders.value.length === 0) {
    ElMessage.warning('请选择要加密的订单')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要加密选中的 ${selectedOrders.value.length} 个订单吗？`,
      '确认批量加密',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    saving.value = true
    const orderIds = selectedOrders.value.map(order => order.id)
    const response = await orderApi.batchEncryptOrders({ order_ids: orderIds })
    
    if (response.code === 200) {
      ElMessage.success('批量加密成功')
      showBatchEncryptDialog.value = false
      selectedOrders.value = []
      loadOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量加密失败')
      console.error(error)
    }
  } finally {
    saving.value = false
  }
}

const viewShards = (order) => {
  // 跳转到分片管理页面，显示该订单的分片信息
  // 这里可以使用路由跳转或者弹窗显示
  ElMessage.info('跳转到分片管理页面查看订单分片信息')
}

const deleteOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除订单 "${order.id}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await orderApi.deleteOrder(order.id)
    if (response.code === 200) {
      ElMessage.success('订单删除成功')
      loadOrders()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('订单删除失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.order-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.order-detail {
  padding: 16px 0;
}

.batch-encrypt {
  padding: 16px 0;
}

.selected-count {
  font-weight: 500;
  margin-bottom: 12px;
  color: #303133;
}

.order-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 8px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.order-item:last-child {
  border-bottom: none;
}
</style>
