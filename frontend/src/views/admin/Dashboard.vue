<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6" v-for="stat in stats" :key="stat.key">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40" :color="stat.color">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 近期订单 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期订单</span>
              <el-button type="primary" text @click="$router.push('/admin/orders')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentOrders" style="width: 100%">
            <el-table-column prop="id" label="订单ID" width="120" />
            <el-table-column prop="customer_name" label="客户名称" />
            <el-table-column prop="total_amount" label="订单金额">
              <template #default="{ row }">
                ¥{{ row.total_amount }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 系统状态 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <div class="system-status">
            <div class="status-item" v-for="item in systemStatus" :key="item.name">
              <div class="status-name">{{ item.name }}</div>
              <div class="status-value">
                <el-tag :type="item.status === 'normal' ? 'success' : 'danger'">
                  {{ item.value }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, ShoppingCart, Document, Setting } from '@element-plus/icons-vue'
import { orderApi } from '@/api/order'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const stats = ref([
  { key: 'users', label: '用户总数', value: 0, icon: User, color: '#409EFF' },
  { key: 'orders', label: '订单总数', value: 0, icon: ShoppingCart, color: '#67C23A' },
  { key: 'encrypted', label: '加密订单', value: 0, icon: Document, color: '#E6A23C' },
  { key: 'shards', label: '分片总数', value: 0, icon: Setting, color: '#F56C6C' }
])

const recentOrders = ref([])
const systemStatus = ref([
  { name: 'Fabric网络', status: 'normal', value: '正常' },
  { name: '加密服务', status: 'normal', value: '正常' },
  { name: '数据库', status: 'normal', value: '正常' },
  { name: 'Redis缓存', status: 'normal', value: '正常' }
])

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

const loadDashboardData = async () => {
  try {
    // 加载统计数据
    const statsResponse = await orderApi.getStats()
    if (statsResponse.code === 200) {
      const data = statsResponse.data
      stats.value.forEach(stat => {
        if (data[stat.key] !== undefined) {
          stat.value = data[stat.key]
        }
      })
    }

    // 加载近期订单
    const ordersResponse = await orderApi.getOrderList({
      page: 1,
      page_size: 5,
      sort: 'created_at',
      order: 'desc'
    })
    if (ordersResponse.code === 200) {
      recentOrders.value = ordersResponse.data.items || []
    }
  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  margin-right: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-name {
  font-weight: 500;
}
</style>
