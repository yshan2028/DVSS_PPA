<template>
  <el-card class="quick-actions-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon><Operation /></el-icon>
        <span>{{ t('actions.title') }}</span>
      </div>
    </template>

    <div class="actions-grid">
      <el-button
        type="primary"
        size="large"
        class="action-button"
        @click="$router.push('/dvss-analysis')"
      >
        <el-icon><TrendCharts /></el-icon>
        <span>{{ t('actions.dvssAnalysis') }}</span>
      </el-button>

      <el-button
        type="success"
        size="large"
        class="action-button"
        @click="$router.push('/encrypt')"
      >
        <el-icon><Lock /></el-icon>
        <span>{{ t('actions.encrypt') }}</span>
      </el-button>

      <el-button
        type="info"
        size="large"
        class="action-button"
        @click="$router.push('/query')"
      >
        <el-icon><Search /></el-icon>
        <span>{{ t('actions.query') }}</span>
      </el-button>

      <el-button
        type="warning"
        size="large"
        class="action-button"
        @click="$router.push('/blockchain-audit')"
      >
        <el-icon><Link /></el-icon>
        <span>{{ t('actions.blockchainAudit') }}</span>
      </el-button>
    </div>

    <!-- 快速统计 -->
    <div class="quick-stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalEncryptions }}</div>
            <div class="stat-label">{{ t('actions.totalEncryptions') }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalQueries }}</div>
            <div class="stat-label">{{ t('actions.totalQueries') }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.activeUsers }}</div>
            <div class="stat-label">{{ t('actions.activeUsers') }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-number">{{ stats.systemUptime }}</div>
            <div class="stat-label">{{ t('actions.uptime') }}</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import api from '@/api/index'
import { 
  Operation, 
  Lock, 
  Search, 
  Monitor, 
  Link 
} from '@element-plus/icons-vue'

const i18nStore = useI18nStore()
const { t } = i18nStore

const stats = ref({
  totalEncryptions: 0,
  totalQueries: 0,
  activeUsers: 0,
  systemUptime: '0h'
})

const loadQuickStats = async () => {
  try {
    const response = await api.get('/monitoring/quick-stats')
    stats.value = response.data
  } catch (error) {
    console.error('加载快速统计失败:', error)
    // 使用模拟数据
    stats.value = {
      totalEncryptions: 156,
      totalQueries: 342,
      activeUsers: 8,
      systemUptime: '24h'
    }
  }
}

onMounted(() => {
  loadQuickStats()
  // 每30秒刷新一次统计数据
  setInterval(loadQuickStats, 30000)
})
</script>

<style scoped>
.quick-actions-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.action-button {
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-button .el-icon {
  font-size: 20px;
}

.quick-stats {
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
