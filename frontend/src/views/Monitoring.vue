<template>
  <div class="monitoring-container">
    <div class="page-header">
      <h1>系统监控</h1>
      <p>实时监控DVSS-PPA系统状态和性能指标</p>
    </div>

    <div class="monitoring-grid">
      <!-- 系统状态卡片 -->
      <div class="card">
        <div class="card-header">
          <h3>系统状态</h3>
          <div class="status-indicator" :class="systemStatus.class">
            {{ systemStatus.text }}
          </div>
        </div>
        <div class="card-content">
          <div class="metric">
            <span class="label">运行时间:</span>
            <span class="value">{{ uptime }}</span>
          </div>
          <div class="metric">
            <span class="label">CPU使用率:</span>
            <span class="value">{{ metrics.cpu }}%</span>
          </div>
          <div class="metric">
            <span class="label">内存使用:</span>
            <span class="value">{{ metrics.memory }}%</span>
          </div>
        </div>
      </div>

      <!-- 服务状态 -->
      <div class="card">
        <div class="card-header">
          <h3>服务状态</h3>
        </div>
        <div class="card-content">
          <div class="service-list">
            <div class="service-item" v-for="service in services" :key="service.name">
              <div class="service-name">{{ service.name }}</div>
              <div class="service-status" :class="service.status">
                {{ service.status === 'running' ? '运行中' : '停止' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据库状态 -->
      <div class="card">
        <div class="card-header">
          <h3>数据库状态</h3>
        </div>
        <div class="card-content">
          <div class="metric">
            <span class="label">连接数:</span>
            <span class="value">{{ database.connections }}</span>
          </div>
          <div class="metric">
            <span class="label">查询延迟:</span>
            <span class="value">{{ database.latency }}ms</span>
          </div>
          <div class="metric">
            <span class="label">存储空间:</span>
            <span class="value">{{ database.storage }}GB</span>
          </div>
        </div>
      </div>

      <!-- 区块链状态 -->
      <div class="card">
        <div class="card-header">
          <h3>区块链状态</h3>
        </div>
        <div class="card-content">
          <div class="metric">
            <span class="label">当前区块:</span>
            <span class="value">{{ blockchain.currentBlock }}</span>
          </div>
          <div class="metric">
            <span class="label">节点数量:</span>
            <span class="value">{{ blockchain.nodes }}</span>
          </div>
          <div class="metric">
            <span class="label">同步状态:</span>
            <span class="value">{{ blockchain.syncStatus }}</span>
          </div>
        </div>
      </div>

      <!-- 性能图表 -->
      <div class="card chart-card">
        <div class="card-header">
          <h3>性能趋势</h3>
        </div>
        <div class="card-content">
          <div class="chart-placeholder">
            <p>性能图表区域</p>
            <small>CPU、内存、网络使用率历史趋势</small>
          </div>
        </div>
      </div>

      <!-- 最近日志 -->
      <div class="card">
        <div class="card-header">
          <h3>最近日志</h3>
        </div>
        <div class="card-content">
          <div class="log-list">
            <div class="log-item" v-for="log in recentLogs" :key="log.id">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-level" :class="log.level">{{ log.level }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'Monitoring',
  setup() {
    const uptime = ref('00:00:00')
    const metrics = ref({
      cpu: 0,
      memory: 0
    })
    
    const systemStatus = ref({
      text: '正常',
      class: 'status-normal'
    })

    const services = ref([
      { name: 'Backend Python', status: 'running' },
      { name: 'Backend Go', status: 'running' },
      { name: 'Redis', status: 'running' },
      { name: 'PostgreSQL', status: 'running' },
      { name: 'Blockchain Node', status: 'running' }
    ])

    const database = ref({
      connections: 25,
      latency: 12,
      storage: 2.5
    })

    const blockchain = ref({
      currentBlock: 1024,
      nodes: 5,
      syncStatus: '已同步'
    })

    const recentLogs = ref([
      { id: 1, time: '14:30:25', level: 'INFO', message: '用户登录成功' },
      { id: 2, time: '14:29:12', level: 'INFO', message: '数据加密完成' },
      { id: 3, time: '14:28:45', level: 'WARN', message: 'CPU使用率较高' },
      { id: 4, time: '14:27:30', level: 'INFO', message: '区块链同步完成' },
      { id: 5, time: '14:26:15', level: 'INFO', message: '查询请求处理完成' }
    ])

    let intervalId = null

    const updateMetrics = () => {
      // 模拟实时数据更新
      metrics.value.cpu = Math.floor(Math.random() * 100)
      metrics.value.memory = Math.floor(Math.random() * 100)
      
      // 更新运行时间
      const now = new Date()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      uptime.value = `${hours}:${minutes}:${seconds}`
    }

    onMounted(() => {
      updateMetrics()
      intervalId = setInterval(updateMetrics, 5000) // 每5秒更新一次
    })

    onUnmounted(() => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    })

    return {
      uptime,
      metrics,
      systemStatus,
      services,
      database,
      blockchain,
      recentLogs
    }
  }
}
</script>

<style scoped>
.monitoring-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  margin: 0;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px 20px 10px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #333;
}

.card-content {
  padding: 20px;
}

.status-indicator {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-normal {
  background-color: #e8f5e8;
  color: #4caf50;
}

.metric {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.metric:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
}

.value {
  font-weight: bold;
  color: #333;
}


.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.service-item:last-child {
  border-bottom: none;
}

.service-name {
  font-weight: 500;
  color: #333;
}

.service-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.service-status.running {
  background-color: #e8f5e8;
  color: #4caf50;
}

.service-status.stopped {
  background-color: #ffebee;
  color: #f44336;
}

.chart-card {
  grid-column: span 2;
}

.chart-placeholder {
  height: 200px;
  background-color: #f9f9f9;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #666;
}

.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #666;
  font-family: monospace;
  min-width: 70px;
}

.log-level {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  min-width: 45px;
  text-align: center;
}

.log-level.INFO {
  background-color: #e3f2fd;
  color: #1976d2;
}

.log-level.WARN {
  background-color: #fff3e0;
  color: #f57c00;
}

.log-level.ERROR {
  background-color: #ffebee;
  color: #d32f2f;
}

.log-message {
  color: #333;
  flex: 1;
}

@media (max-width: 768px) {
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card {
    grid-column: span 1;
  }
}
</style>
