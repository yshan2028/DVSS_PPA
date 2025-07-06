<template>
  <MainLayout>
    <div class="dashboard-container">
    <!-- 用户欢迎区域 -->
    <div class="welcome-section">
      <el-card shadow="never" class="welcome-card">
        <div class="user-welcome">
          <div class="user-info">
            <el-avatar :size="50" :src="currentUser?.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="user-details">
              <h2>欢迎回来，{{ currentUser?.username || currentUser?.role_name }}</h2>
              <p class="user-role">{{ currentUser?.role_name }} · 权限等级 {{ currentUser?.access_level }}</p>
            </div>
          </div>
          <div class="welcome-actions">
            <el-button type="primary" @click="$router.push('/query')">
              <el-icon><Search /></el-icon>
              数据查询
            </el-button>
            <el-button @click="$router.push('/encrypt')">
              <el-icon><Lock /></el-icon>
              数据加密
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 统计概览 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon order-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.totalOrders }}</h3>
                <p>总订单数</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon sensitivity-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.sensitiveData }}</h3>
                <p>敏感数据</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon blockchain-icon">
                <el-icon><Link /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.blockchainRecords }}</h3>
                <p>区块链记录</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-icon access-icon">
                <el-icon><View /></el-icon>
              </div>
              <div class="stat-content">
                <h3>{{ stats.todayAccess }}</h3>
                <p>今日访问</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要功能区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：敏感度分析图表 -->
        <el-col :span="16">
          <el-card shadow="never" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>敏感度分析趋势</span>
                <el-button type="text" @click="refreshTrends">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </template>
            <div ref="sensitivityChart" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 右侧：快速操作和最近活动 -->
        <el-col :span="8">
          <!-- 快速操作 -->
          <el-card shadow="never" class="action-card" style="margin-bottom: 20px;">
            <template #header>
              <span>快速操作</span>
            </template>
            <div class="quick-actions">
              <el-button 
                type="primary" 
                class="action-btn" 
                @click="$router.push('/encrypt')"
              >
                <el-icon><Upload /></el-icon>
                数据上传加密
              </el-button>
              <el-button 
                class="action-btn" 
                @click="$router.push('/query')"
              >
                <el-icon><Search /></el-icon>
                数据查询分析
              </el-button>
              <el-button 
                class="action-btn" 
                @click="$router.push('/blockchain-audit')"
              >
                <el-icon><Document /></el-icon>
                审计日志
              </el-button>
              <el-button 
                class="action-btn" 
                @click="$router.push('/monitoring')"
              >
                <el-icon><Monitor /></el-icon>
                系统监控
              </el-button>
            </div>
          </el-card>

          <!-- 最近活动 -->
          <el-card shadow="never" class="activity-card">
            <template #header>
              <span>最近活动</span>
            </template>
            <div class="activity-list">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon">
                  <el-icon><component :is="activity.icon" /></el-icon>
                </div>
                <div class="activity-content">
                  <p class="activity-text">{{ activity.text }}</p>
                  <span class="activity-time">{{ formatTime(activity.time) }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 权限可见的高级功能 -->
    <div v-if="hasAdvancedPermissions" class="advanced-section">
      <el-card shadow="never">
        <template #header>
          <span>高级管理功能</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="advanced-item" @click="$router.push('/analytics')">
              <el-icon><DataAnalysis /></el-icon>
              <h4>数据分析</h4>
              <p>深度分析和统计报告</p>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="advanced-item" @click="$router.push('/blockchain')">
              <el-icon><Link /></el-icon>
              <h4>区块链管理</h4>
              <p>Fabric网络状态和配置</p>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="advanced-item" @click="openUserManagement">
              <el-icon><UserFilled /></el-icon>
              <h4>用户管理</h4>
              <p>角色权限和用户配置</p>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { dvssAPI } from '@/api/index'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import MainLayout from '@/components/MainLayout.vue'

const authStore = useAuthStore()

// 响应式数据
const stats = ref({
  totalOrders: 0,
  sensitiveData: 0,
  blockchainRecords: 0,
  todayAccess: 0
})

const recentActivities = ref([])
const sensitivityChart = ref(null)
let chartInstance = null

// 计算属性
const currentUser = computed(() => authStore.currentUser)

const hasAdvancedPermissions = computed(() => {
  const user = authStore.currentUser
  return user && (user.access_level >= 4 || user.permissions?.includes('manage'))
})

// 方法
const loadDashboardData = async () => {
  try {
    const response = await dvssAPI.getDashboard()
    if (response.data.success) {
      const data = response.data.data
      stats.value = {
        totalOrders: data.total_orders || 0,
        sensitiveData: data.sensitive_count || 0,
        blockchainRecords: data.blockchain_records || 0,
        todayAccess: data.today_access || 0
      }
      recentActivities.value = data.recent_activities || []
    }
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    ElMessage.warning('加载仪表盘数据失败，显示模拟数据')
    // 模拟数据
    stats.value = {
      totalOrders: 1248,
      sensitiveData: 89,
      blockchainRecords: 567,
      todayAccess: 156
    }
    recentActivities.value = [
      {
        id: 1,
        icon: 'Upload',
        text: '新订单数据上传',
        time: new Date(Date.now() - 1000 * 60 * 5)
      },
      {
        id: 2,
        icon: 'View',
        text: '敏感数据查询',
        time: new Date(Date.now() - 1000 * 60 * 15)
      },
      {
        id: 3,
        icon: 'Document',
        text: '审计日志生成',
        time: new Date(Date.now() - 1000 * 60 * 30)
      }
    ]
  }
}

const initSensitivityChart = async () => {
  if (!sensitivityChart.value) return
  
  chartInstance = echarts.init(sensitivityChart.value)
  
  const option = {
    title: {
      text: '敏感度分析趋势',
      textStyle: {
        fontSize: 14,
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['高敏感', '中敏感', '低敏感']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '高敏感',
        type: 'line',
        data: [12, 15, 18, 20, 25, 22, 28],
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '中敏感',
        type: 'line',
        data: [25, 30, 35, 32, 38, 40, 45],
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '低敏感',
        type: 'line',
        data: [120, 125, 130, 135, 140, 138, 145],
        itemStyle: { color: '#67c23a' }
      }
    ]
  }
  
  chartInstance.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

const refreshTrends = async () => {
  try {
    await loadDashboardData()
    await initSensitivityChart()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

const formatTime = (time) => {
  const now = new Date()
  const diff = now - new Date(time)
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}小时前`
  return `${Math.floor(minutes / 1440)}天前`
}

const openUserManagement = () => {
  ElMessage.info('用户管理功能开发中...')
}

// 生命周期
onMounted(async () => {
  await loadDashboardData()
  await nextTick()
  await initSensitivityChart()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.welcome-card :deep(.el-card__body) {
  padding: 20px;
}

.user-welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-details h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.user-role {
  margin: 5px 0 0;
  opacity: 0.9;
  font-size: 14px;
}

.welcome-actions {
  display: flex;
  gap: 10px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
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
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.order-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.sensitivity-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.blockchain-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.access-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-content h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-content p {
  margin: 5px 0 0;
  color: #909399;
  font-size: 14px;
}

/* 主要内容区域 */
.main-content {
  margin-bottom: 20px;
}

.chart-card, .action-card, .activity-card {
  border: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 350px;
  width: 100%;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  height: 45px;
  justify-content: flex-start;
  border-radius: 8px;
}

/* 活动列表 */
.activity-list {
  max-height: 200px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f9ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0;
  font-size: 14px;
  color: #303133;
}

.activity-time {
  font-size: 12px;
  color: #909399;
}

/* 高级功能区域 */
.advanced-section {
  margin-top: 20px;
}

.advanced-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s;
}

.advanced-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.advanced-item .el-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 10px;
}

.advanced-item h4 {
  margin: 10px 0 5px;
  color: #303133;
}

.advanced-item p {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
  }
  
  .user-welcome {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .welcome-actions {
    justify-content: center;
  }
  
  .stats-section .el-col {
    margin-bottom: 10px;
  }
}
</style>
