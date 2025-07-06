<template>
  <div class="analytics-container">
    <div class="page-header">
      <h1>数据分析</h1>
      <p>DVSS-PPA系统数据统计与分析</p>
    </div>

    <div class="analytics-grid">
      <!-- 概览统计 -->
      <div class="card overview-card">
        <div class="card-header">
          <h3>系统概览</h3>
          <select v-model="timeRange" class="time-selector">
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
            <option value="90d">最近90天</option>
          </select>
        </div>
        <div class="card-content">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ overview.totalTransactions }}</div>
              <div class="stat-label">总交易数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ overview.totalUsers }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ overview.dataEncrypted }}GB</div>
              <div class="stat-label">加密数据量</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ overview.successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 使用趋势图表 -->
      <div class="card chart-card">
        <div class="card-header">
          <h3>使用趋势</h3>
        </div>
        <div class="card-content">
          <div class="chart-placeholder">
            <div class="chart-title">交易量趋势</div>
            <div class="trend-chart">
              <div class="chart-bar" 
                   v-for="(day, index) in trendData" 
                   :key="index"
                   :style="{ height: (day.value / maxTrendValue * 100) + '%' }"
                   :title="`${day.date}: ${day.value}笔交易`">
              </div>
            </div>
            <div class="chart-labels">
              <span v-for="(day, index) in trendData" :key="index">
                {{ day.label }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能使用分布 -->
      <div class="card">
        <div class="card-header">
          <h3>功能使用分布</h3>
        </div>
        <div class="card-content">
          <div class="usage-list">
            <div class="usage-item" v-for="item in usageData" :key="item.feature">
              <div class="usage-info">
                <span class="feature-name">{{ item.feature }}</span>
                <span class="usage-count">{{ item.count }}次</span>
              </div>
              <div class="usage-bar">
                <div class="usage-progress" 
                     :style="{ width: (item.count / maxUsageCount * 100) + '%' }">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 性能指标 -->
      <div class="card">
        <div class="card-header">
          <h3>性能指标</h3>
        </div>
        <div class="card-content">
          <div class="performance-metrics">
            <div class="metric-item">
              <div class="metric-name">平均响应时间</div>
              <div class="metric-value">{{ performance.avgResponseTime }}ms</div>
              <div class="metric-trend positive">↗ +5.2%</div>
            </div>
            <div class="metric-item">
              <div class="metric-name">加密速度</div>
              <div class="metric-value">{{ performance.encryptionSpeed }}MB/s</div>
              <div class="metric-trend positive">↗ +12.8%</div>
            </div>
            <div class="metric-item">
              <div class="metric-name">查询效率</div>
              <div class="metric-value">{{ performance.queryEfficiency }}ms</div>
              <div class="metric-trend negative">↘ -3.1%</div>
            </div>
            <div class="metric-item">
              <div class="metric-name">存储利用率</div>
              <div class="metric-value">{{ performance.storageUtilization }}%</div>
              <div class="metric-trend positive">↗ +7.4%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误统计 -->
      <div class="card">
        <div class="card-header">
          <h3>错误统计</h3>
        </div>
        <div class="card-content">
          <div class="error-list">
            <div class="error-item" v-for="error in errorStats" :key="error.type">
              <div class="error-info">
                <span class="error-type">{{ error.type }}</span>
                <span class="error-count">{{ error.count }}次</span>
              </div>
              <div class="error-severity" :class="error.severity">
                {{ getSeverityText(error.severity) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 地理分布 -->
      <div class="card">
        <div class="card-header">
          <h3>用户地理分布</h3>
        </div>
        <div class="card-content">
          <div class="geo-stats">
            <div class="geo-item" v-for="location in geoData" :key="location.region">
              <div class="geo-info">
                <span class="region-name">{{ location.region }}</span>
                <span class="user-count">{{ location.users }}用户</span>
              </div>
              <div class="geo-percentage">{{ location.percentage }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据导出 -->
      <div class="card">
        <div class="card-header">
          <h3>数据导出</h3>
        </div>
        <div class="card-content">
          <div class="export-options">
            <button class="btn-primary" @click="exportReport">生成报告</button>
            <button class="btn-secondary" @click="exportCSV">导出CSV</button>
            <button class="btn-secondary" @click="exportJSON">导出JSON</button>
            <button class="btn-secondary" @click="exportChart">导出图表</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'Analytics',
  setup() {
    const timeRange = ref('7d')

    const overview = ref({
      totalTransactions: 1247,
      totalUsers: 156,
      dataEncrypted: 245.8,
      successRate: 98.7
    })

    const trendData = ref([
      { date: '2024-01-21', value: 45, label: '21日' },
      { date: '2024-01-22', value: 52, label: '22日' },
      { date: '2024-01-23', value: 38, label: '23日' },
      { date: '2024-01-24', value: 67, label: '24日' },
      { date: '2024-01-25', value: 71, label: '25日' },
      { date: '2024-01-26', value: 58, label: '26日' },
      { date: '2024-01-27', value: 82, label: '27日' }
    ])

    const maxTrendValue = computed(() => {
      return Math.max(...trendData.value.map(d => d.value))
    })

    const usageData = ref([
      { feature: '数据加密', count: 456 },
      { feature: 'PPA验证', count: 342 },
      { feature: '隐私查询', count: 289 },
      { feature: '区块链审计', count: 178 },
      { feature: '系统监控', count: 123 }
    ])

    const maxUsageCount = computed(() => {
      return Math.max(...usageData.value.map(u => u.count))
    })

    const performance = ref({
      avgResponseTime: 145,
      encryptionSpeed: 58.3,
      queryEfficiency: 89,
      storageUtilization: 76.5
    })

    const errorStats = ref([
      { type: '网络超时', count: 12, severity: 'medium' },
      { type: '加密失败', count: 5, severity: 'high' },
      { type: '权限错误', count: 8, severity: 'medium' },
      { type: '数据格式错误', count: 3, severity: 'low' }
    ])

    const geoData = ref([
      { region: '北京', users: 45, percentage: 28.8 },
      { region: '上海', users: 38, percentage: 24.4 },
      { region: '广州', users: 29, percentage: 18.6 },
      { region: '深圳', users: 22, percentage: 14.1 },
      { region: '其他', users: 22, percentage: 14.1 }
    ])

    const getSeverityText = (severity) => {
      const severityMap = {
        'low': '低级',
        'medium': '中级',
        'high': '高级'
      }
      return severityMap[severity] || severity
    }

    const exportReport = () => {
      console.log('生成分析报告')
    }

    const exportCSV = () => {
      console.log('导出CSV格式数据')
    }

    const exportJSON = () => {
      console.log('导出JSON格式数据')
    }

    const exportChart = () => {
      console.log('导出图表')
    }

    return {
      timeRange,
      overview,
      trendData,
      maxTrendValue,
      usageData,
      maxUsageCount,
      performance,
      errorStats,
      geoData,
      getSeverityText,
      exportReport,
      exportCSV,
      exportJSON,
      exportChart
    }
  }
}
</script>

<style scoped>
.analytics-container {
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

.analytics-grid {
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

.time-selector {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.overview-card {
  grid-column: span 2;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.chart-card {
  grid-column: span 2;
}

.chart-placeholder {
  text-align: center;
}

.chart-title {
  margin-bottom: 20px;
  color: #333;
  font-weight: 500;
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  height: 150px;
  gap: 8px;
  margin-bottom: 10px;
  padding: 0 20px;
}

.chart-bar {
  flex: 1;
  background: linear-gradient(to top, #007bff, #66b3ff);
  border-radius: 2px 2px 0 0;
  min-height: 10px;
  transition: all 0.3s ease;
}

.chart-bar:hover {
  opacity: 0.8;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  font-size: 12px;
  color: #666;
}


.usage-item {
  margin-bottom: 15px;
}

.usage-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.feature-name {
  color: #333;
  font-weight: 500;
}

.usage-count {
  color: #666;
  font-size: 14px;
}

.usage-bar {
  width: 100%;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.usage-progress {
  height: 100%;
  background: linear-gradient(to right, #007bff, #66b3ff);
  transition: width 0.3s ease;
}



.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 15px;
}

.metric-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.metric-name {
  color: #666;
  flex: 1;
}

.metric-value {
  font-weight: bold;
  color: #333;
  margin-right: 15px;
}

.metric-trend {
  font-size: 12px;
  font-weight: bold;
}

.metric-trend.positive {
  color: #4caf50;
}

.metric-trend.negative {
  color: #f44336;
}



.error-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 10px;
}

.error-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.error-info {
  flex: 1;
}

.error-type {
  color: #333;
  font-weight: 500;
  margin-right: 10px;
}

.error-count {
  color: #666;
  font-size: 14px;
}

.error-severity {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
}

.error-severity.low {
  background-color: #e8f5e8;
  color: #4caf50;
}

.error-severity.medium {
  background-color: #fff3e0;
  color: #f57c00;
}

.error-severity.high {
  background-color: #ffebee;
  color: #f44336;
}



.geo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 10px;
}

.geo-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.geo-info {
  flex: 1;
}

.region-name {
  color: #333;
  font-weight: 500;
  margin-right: 10px;
}

.user-count {
  color: #666;
  font-size: 14px;
}

.geo-percentage {
  font-weight: bold;
  color: #007bff;
}

.export-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

@media (max-width: 768px) {
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-card, .chart-card {
    grid-column: span 1;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
