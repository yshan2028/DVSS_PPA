<template>
  <div class="system-overview">
    <el-row :gutter="20">
      <!-- 系统状态卡片 -->
      <el-col :span="8">
        <el-card class="status-card" shadow="hover">
          <div class="status-item">
            <el-icon class="status-icon online"><SuccessFilled /></el-icon>
            <div class="status-content">
              <h3>{{ t('overview.systemStatus') }}</h3>
              <p class="status-text online">{{ t('overview.online') }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 当前用户信息 -->
      <el-col :span="8">
        <el-card class="user-card" shadow="hover">
          <div class="user-info">
            <el-avatar :size="40" class="user-avatar">
              {{ authStore.currentUser?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-details">
              <h4>{{ authStore.currentUser?.username }}</h4>
              <el-tag :type="getRoleTagType(authStore.currentUser?.role)">
                {{ getRoleLabel(authStore.currentUser?.role) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 系统统计 -->
      <el-col :span="8">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <h4>{{ t('overview.totalRecords') }}</h4>
            <div class="stats-number">{{ systemStats.totalRecords }}</div>
            <div class="stats-trend">
              <el-icon><TrendCharts /></el-icon>
              <span>+{{ systemStats.todayRecords }} {{ t('overview.today') }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时监控图表 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ t('overview.performanceChart') }}</span>
              <el-button type="text" @click="refreshData">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div ref="performanceChart" style="height: 300px;"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>{{ t('overview.roleDistribution') }}</span>
            </div>
          </template>
          <div ref="roleChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import api from '@/api/index'
import * as echarts from 'echarts'
import { 
  SuccessFilled, 
  TrendCharts, 
  Refresh 
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore

const performanceChart = ref(null)
const roleChart = ref(null)
const systemStats = ref({
  totalRecords: 0,
  todayRecords: 0,
  activeUsers: 0
})

const getRoleTagType = (role) => {
  const types = {
    seller: 'primary',
    payment_provider: 'success',
    logistics: 'warning',
    auditor: 'danger',
    platform: 'info'
  }
  return types[role] || 'default'
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

const initPerformanceChart = () => {
  if (!performanceChart.value) return
  
  const chart = echarts.init(performanceChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [t('overview.cpuUsage'), t('overview.memoryUsage')]
    },
    xAxis: {
      type: 'category',
      data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
    },
    yAxis: {
      type: 'value',
      max: 100
    },
    series: [
      {
        name: t('overview.cpuUsage'),
        type: 'line',
        data: [20, 25, 30, 28, 35, 32, 30],
        smooth: true,
        itemStyle: { color: '#409EFF' }
      },
      {
        name: t('overview.memoryUsage'),
        type: 'line',
        data: [45, 48, 52, 50, 55, 58, 56],
        smooth: true,
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
  chart.setOption(option)
}

const initRoleChart = () => {
  if (!roleChart.value) return
  
  const chart = echarts.init(roleChart.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: [
          { value: 35, name: t('roles.seller') },
          { value: 25, name: t('roles.payment') },
          { value: 20, name: t('roles.logistics') },
          { value: 15, name: t('roles.auditor') },
          { value: 5, name: t('roles.platform') }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

const loadSystemStats = async () => {
  try {
    const response = await api.get('/monitoring/stats')
    systemStats.value = response.data
  } catch (error) {
    console.error('加载系统统计失败:', error)
  }
}

const refreshData = async () => {
  await loadSystemStats()
  // 重新初始化图表数据
  initPerformanceChart()
  initRoleChart()
}

onMounted(async () => {
  await loadSystemStats()
  await nextTick()
  initPerformanceChart()
  initRoleChart()
})
</script>

<style scoped>
.system-overview {
  width: 100%;
}

.status-card, .user-card, .stats-card {
  height: 120px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
  height: 100%;
}

.status-icon {
  font-size: 32px;
}

.status-icon.online {
  color: #67C23A;
}

.status-content h3 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 16px;
}

.status-text.online {
  color: #67C23A;
  font-weight: bold;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  height: 100%;
}

.user-avatar {
  background: linear-gradient(135deg, #409EFF, #36CFC9);
  color: white;
  font-weight: bold;
}

.user-details h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.stats-content {
  text-align: center;
  padding: 10px 0;
}

.stats-content h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stats-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  color: #67C23A;
  font-size: 12px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
