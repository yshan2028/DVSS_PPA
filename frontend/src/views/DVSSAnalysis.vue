<template>
  <div class="dvss-analysis">
    <div class="header">
      <h1>DVSS 动态价值敏感数据分析</h1>
      <p class="subtitle">基于人工智能的订单敏感度分析与风险评估</p>
    </div>

    <!-- 仪表板概览 -->
    <div class="dashboard-overview">
      <div class="stats-grid">
        <div class="stat-card primary">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>{{ dashboardData.sensitivity_overview?.analysis_count || 0 }}</h3>
            <p>分析次数</p>
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <h3>{{ formatScore(dashboardData.sensitivity_overview?.recent_average) }}</h3>
            <p>近期平均敏感度</p>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <h3>{{ getTrendLabel(dashboardData.sensitivity_overview?.trend_direction) }}</h3>
            <p>趋势方向</p>
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-icon">🛡️</div>
          <div class="stat-content">
            <h3>{{ dashboardData.system_status?.dvss_engine || '未知' }}</h3>
            <p>系统状态</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析操作面板 -->
    <div class="analysis-panel">
      <div class="panel-header">
        <h2>订单敏感度分析</h2>
        <div class="analysis-actions">
          <button @click="showSingleAnalysis = true" class="analysis-btn primary">
            <i class="icon">🔍</i>
            单个分析
          </button>
          <button @click="showBatchAnalysis = true" class="analysis-btn secondary">
            <i class="icon">📊</i>
            批量分析
          </button>
          <button @click="loadDashboard" class="refresh-btn" :disabled="dashboardLoading">
            <i class="icon">🔄</i>
            {{ dashboardLoading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>

      <!-- 敏感度趋势图 -->
      <div class="trends-section">
        <div class="trends-header">
          <h3>敏感度趋势</h3>
          <div class="time-range-selector">
            <button 
              v-for="range in timeRanges" 
              :key="range.value"
              @click="selectedTimeRange = range.value; loadTrends()"
              :class="{ active: selectedTimeRange === range.value }"
              class="time-btn"
            >
              {{ range.label }}
            </button>
          </div>
        </div>
        <div class="trends-chart">
          <div v-if="trendsLoading" class="loading-chart">
            <div class="spinner"></div>
            <p>加载趋势数据中...</p>
          </div>
          <div v-else-if="trendsError" class="error-chart">
            <p>❌ {{ trendsError }}</p>
            <button @click="loadTrends" class="retry-btn">重试</button>
          </div>
          <div v-else-if="trendsData.scores?.length > 0" class="chart-container">
            <canvas ref="trendsCanvas" width="800" height="300"></canvas>
          </div>
          <div v-else class="empty-chart">
            <p>📈 暂无趋势数据</p>
          </div>
        </div>
      </div>

      <!-- 最近分析结果 -->
      <div class="recent-results">
        <h3>最近分析结果</h3>
        <div v-if="recentResults.length === 0" class="empty-results">
          <p>📋 暂无分析结果</p>
          <p>点击上方按钮开始分析</p>
        </div>
        <div v-else class="results-grid">
          <div 
            v-for="result in recentResults" 
            :key="result.order_id"
            :class="getResultCardClass(result)"
            class="result-card"
          >
            <div class="result-header">
              <span class="order-id">{{ result.order_id }}</span>
              <span :class="getRiskLevelClass(result.risk_level)" class="risk-level">
                {{ getRiskLevelLabel(result.risk_level) }}
              </span>
            </div>
            <div class="result-content">
              <div class="score-display">
                <div class="score-circle" :style="getScoreCircleStyle(result.sensitivity_score)">
                  <span class="score-value">{{ formatScore(result.sensitivity_score) }}</span>
                </div>
                <div class="score-info">
                  <p>敏感度分数</p>
                  <small>{{ formatTimestamp(result.timestamp) }}</small>
                </div>
              </div>
              <div class="protection-strategy">
                <h4>保护策略</h4>
                <div class="strategy-tags">
                  <span 
                    v-for="control in result.protection_strategy?.access_controls || []"
                    :key="control"
                    class="strategy-tag"
                  >
                    {{ getControlLabel(control) }}
                  </span>
                </div>
              </div>
            </div>
            <div class="result-actions">
              <button @click="viewResultDetails(result)" class="view-details-btn">
                查看详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 单个分析弹窗 -->
    <div v-if="showSingleAnalysis" class="modal-overlay" @click="closeSingleAnalysis">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>单个订单敏感度分析</h3>
          <button @click="closeSingleAnalysis" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="performSingleAnalysis" class="analysis-form">
            <div class="form-grid">
              <div class="form-section">
                <h4>订单基本信息</h4>
                <div class="form-group">
                  <label>订单ID:</label>
                  <input v-model="singleAnalysisForm.order_data.order_id" type="text" required />
                </div>
                <div class="form-group">
                  <label>用户ID:</label>
                  <input v-model="singleAnalysisForm.order_data.user_id" type="text" required />
                </div>
                <div class="form-group">
                  <label>订单金额:</label>
                  <input v-model.number="singleAnalysisForm.order_data.amount" type="number" step="0.01" required />
                </div>
                <div class="form-group">
                  <label>支付方式:</label>
                  <select v-model="singleAnalysisForm.order_data.payment_method" required>
                    <option value="">请选择支付方式</option>
                    <option value="credit_card">信用卡</option>
                    <option value="debit_card">借记卡</option>
                    <option value="paypal">PayPal</option>
                    <option value="bank_transfer">银行转账</option>
                    <option value="cryptocurrency">加密货币</option>
                  </select>
                </div>
              </div>
              
              <div class="form-section">
                <h4>订单商品</h4>
                <div class="items-section">
                  <div 
                    v-for="(item, index) in singleAnalysisForm.order_data.items" 
                    :key="index"
                    class="item-row"
                  >
                    <input v-model="item.name" type="text" placeholder="商品名称" required />
                    <input v-model.number="item.price" type="number" step="0.01" placeholder="价格" required />
                    <input v-model.number="item.quantity" type="number" placeholder="数量" required />
                    <select v-model="item.category" required>
                      <option value="">分类</option>
                      <option value="electronics">电子产品</option>
                      <option value="clothing">服装</option>
                      <option value="luxury">奢侈品</option>
                      <option value="food">食品</option>
                      <option value="books">图书</option>
                      <option value="other">其他</option>
                    </select>
                    <button type="button" @click="removeItem(index)" class="remove-item-btn">🗑️</button>
                  </div>
                  <button type="button" @click="addItem" class="add-item-btn">➕ 添加商品</button>
                </div>
              </div>
              
              <div class="form-section">
                <h4>分析上下文 (可选)</h4>
                <div class="form-group">
                  <label>会话时长 (分钟):</label>
                  <input v-model.number="singleAnalysisForm.context.session_duration" type="number" />
                </div>
                <div class="form-group">
                  <label>历史订单数:</label>
                  <input v-model.number="singleAnalysisForm.context.previous_orders_count" type="number" />
                </div>
                <div class="form-group">
                  <label>用户风险分数 (0-1):</label>
                  <input v-model.number="singleAnalysisForm.context.user_risk_score" type="number" step="0.01" min="0" max="1" />
                </div>
                <div class="form-group">
                  <label>位置风险分数 (0-1):</label>
                  <input v-model.number="singleAnalysisForm.context.location_risk" type="number" step="0.01" min="0" max="1" />
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeSingleAnalysis" class="cancel-btn">取消</button>
              <button type="submit" :disabled="singleAnalysisLoading" class="submit-btn">
                {{ singleAnalysisLoading ? '分析中...' : '开始分析' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 批量分析弹窗 -->
    <div v-if="showBatchAnalysis" class="modal-overlay" @click="closeBatchAnalysis">
      <div class="modal-content medium" @click.stop>
        <div class="modal-header">
          <h3>批量订单敏感度分析</h3>
          <button @click="closeBatchAnalysis" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="batch-upload-section">
            <div class="upload-area">
              <input 
                ref="fileInput"
                type="file" 
                accept=".json,.csv"
                @change="handleFileUpload"
                style="display: none"
              />
              <div class="upload-content" @click="$refs.fileInput.click()">
                <div class="upload-icon">📁</div>
                <h4>上传订单数据文件</h4>
                <p>支持 JSON 或 CSV 格式，最多100个订单</p>
                <button class="upload-btn">选择文件</button>
              </div>
            </div>
            
            <div v-if="batchData.length > 0" class="batch-preview">
              <h4>数据预览 ({{ batchData.length }} 个订单)</h4>
              <div class="preview-table">
                <table>
                  <thead>
                    <tr>
                      <th>订单ID</th>
                      <th>用户ID</th>
                      <th>金额</th>
                      <th>商品数</th>
                      <th>支付方式</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="order in batchData.slice(0, 5)" :key="order.order_id">
                      <td>{{ order.order_id }}</td>
                      <td>{{ order.user_id }}</td>
                      <td>${{ order.amount }}</td>
                      <td>{{ order.items?.length || 0 }}</td>
                      <td>{{ order.payment_method }}</td>
                    </tr>
                  </tbody>
                </table>
                <p v-if="batchData.length > 5" class="more-data">...还有 {{ batchData.length - 5 }} 个订单</p>
              </div>
            </div>
          </div>
          
          <div class="batch-actions">
            <button @click="closeBatchAnalysis" class="cancel-btn">取消</button>
            <button 
              @click="performBatchAnalysis" 
              :disabled="batchData.length === 0 || batchAnalysisLoading"
              class="submit-btn"
            >
              {{ batchAnalysisLoading ? '分析中...' : `分析 ${batchData.length} 个订单` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果详情弹窗 -->
    <div v-if="showResultDetails" class="modal-overlay" @click="closeResultDetails">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>分析结果详情</h3>
          <button @click="closeResultDetails" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedResult" class="result-details">
            <div class="details-grid">
              <div class="detail-section">
                <h4>基本信息</h4>
                <div class="detail-item">
                  <label>订单ID:</label>
                  <span>{{ selectedResult.order_id }}</span>
                </div>
                <div class="detail-item">
                  <label>用户ID:</label>
                  <span>{{ selectedResult.user_id }}</span>
                </div>
                <div class="detail-item">
                  <label>分析时间:</label>
                  <span>{{ formatTimestamp(selectedResult.timestamp) }}</span>
                </div>
                <div class="detail-item">
                  <label>敏感度分数:</label>
                  <span class="score-highlight">{{ formatScore(selectedResult.sensitivity_score) }}</span>
                </div>
                <div class="detail-item">
                  <label>风险等级:</label>
                  <span :class="getRiskLevelClass(selectedResult.risk_level)">
                    {{ getRiskLevelLabel(selectedResult.risk_level) }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>动态阈值:</label>
                  <span>{{ formatScore(selectedResult.adjusted_threshold) }}</span>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>保护策略</h4>
                <div class="strategy-details">
                  <div class="strategy-item">
                    <label>加密级别:</label>
                    <span>{{ getEncryptionLabel(selectedResult.protection_strategy?.encryption_level) }}</span>
                  </div>
                  <div class="strategy-item">
                    <label>访问控制:</label>
                    <div class="controls-list">
                      <span 
                        v-for="control in selectedResult.protection_strategy?.access_controls || []"
                        :key="control"
                        class="control-tag"
                      >
                        {{ getControlLabel(control) }}
                      </span>
                    </div>
                  </div>
                  <div class="strategy-item">
                    <label>监控级别:</label>
                    <span>{{ getMonitoringLabel(selectedResult.protection_strategy?.monitoring_level) }}</span>
                  </div>
                  <div class="strategy-item">
                    <label>数据保留:</label>
                    <span>{{ getRetentionLabel(selectedResult.protection_strategy?.retention_policy) }}</span>
                  </div>
                  <div v-if="selectedResult.protection_strategy?.additional_verifications?.length > 0" class="strategy-item">
                    <label>额外验证:</label>
                    <div class="verifications-list">
                      <span 
                        v-for="verification in selectedResult.protection_strategy.additional_verifications"
                        :key="verification"
                        class="verification-tag"
                      >
                        {{ getVerificationLabel(verification) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="detail-section full-width">
                <h4>特征分析</h4>
                <div class="features-grid">
                  <div 
                    v-for="(value, key) in selectedResult.features" 
                    :key="key"
                    class="feature-item"
                  >
                    <label>{{ getFeatureLabel(key) }}:</label>
                    <span>{{ formatFeatureValue(key, value) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { dvssAPI } from '@/api'

export default {
  name: 'DVSSAnalysis',
  setup() {
    // 响应式数据
    const dashboardLoading = ref(false)
    const dashboardData = ref({})
    const trendsLoading = ref(false)
    const trendsError = ref('')
    const trendsData = ref({})
    const selectedTimeRange = ref(24)
    const recentResults = ref([])
    
    // 弹窗状态
    const showSingleAnalysis = ref(false)
    const showBatchAnalysis = ref(false)
    const showResultDetails = ref(false)
    const selectedResult = ref(null)
    
    // 分析状态
    const singleAnalysisLoading = ref(false)
    const batchAnalysisLoading = ref(false)
    
    // 表单数据
    const singleAnalysisForm = reactive({
      order_data: {
        order_id: '',
        user_id: '',
        amount: 0,
        currency: 'USD',
        payment_method: '',
        items: [
          { name: '', price: 0, quantity: 1, category: '', item_id: '1' }
        ]
      },
      context: {
        session_duration: null,
        previous_orders_count: null,
        user_risk_score: null,
        location_risk: null
      }
    })
    
    const batchData = ref([])
    const trendsCanvas = ref(null)
    
    // 常量
    const timeRanges = [
      { label: '1小时', value: 1 },
      { label: '24小时', value: 24 },
      { label: '7天', value: 168 },
      { label: '30天', value: 720 }
    ]
    
    // 方法
    const loadDashboard = async () => {
      dashboardLoading.value = true
      try {
        const response = await dvssAPI.getDashboard()
        dashboardData.value = response.data.data
      } catch (error) {
        console.error('Load dashboard error:', error)
      } finally {
        dashboardLoading.value = false
      }
    }
    
    const loadTrends = async () => {
      trendsLoading.value = true
      trendsError.value = ''
      try {
        const response = await dvssAPI.getSensitivityTrends({
          time_range_hours: selectedTimeRange.value
        })
        trendsData.value = response.data.data
        await nextTick()
        drawTrendsChart()
      } catch (error) {
        trendsError.value = error.message || '加载趋势数据失败'
        console.error('Load trends error:', error)
      } finally {
        trendsLoading.value = false
      }
    }
    
    const drawTrendsChart = () => {
      if (!trendsCanvas.value || !trendsData.value.scores) return
      
      const canvas = trendsCanvas.value
      const ctx = canvas.getContext('2d')
      const { width, height } = canvas
      
      // 清空画布
      ctx.clearRect(0, 0, width, height)
      
      const scores = trendsData.value.scores.slice(0, 50) // 最近50个数据点
      if (scores.length === 0) return
      
      // 设置样式
      ctx.strokeStyle = '#007bff'
      ctx.fillStyle = 'rgba(0, 123, 255, 0.1)'
      ctx.lineWidth = 2
      
      // 计算坐标
      const padding = 40
      const chartWidth = width - 2 * padding
      const chartHeight = height - 2 * padding
      
      const maxScore = Math.max(...scores, 1)
      const minScore = Math.min(...scores, 0)
      const scoreRange = maxScore - minScore || 1
      
      // 绘制背景网格
      ctx.strokeStyle = '#e9ecef'
      ctx.lineWidth = 1
      for (let i = 0; i <= 5; i++) {
        const y = padding + (chartHeight / 5) * i
        ctx.beginPath()
        ctx.moveTo(padding, y)
        ctx.lineTo(width - padding, y)
        ctx.stroke()
      }
      
      // 绘制趋势线
      ctx.strokeStyle = '#007bff'
      ctx.lineWidth = 2
      ctx.beginPath()
      
      scores.forEach((score, index) => {
        const x = padding + (chartWidth / (scores.length - 1)) * index
        const y = padding + chartHeight - ((score - minScore) / scoreRange) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      
      ctx.stroke()
      
      // 绘制填充区域
      ctx.fillStyle = 'rgba(0, 123, 255, 0.1)'
      ctx.beginPath()
      scores.forEach((score, index) => {
        const x = padding + (chartWidth / (scores.length - 1)) * index
        const y = padding + chartHeight - ((score - minScore) / scoreRange) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.lineTo(width - padding, padding + chartHeight)
      ctx.lineTo(padding, padding + chartHeight)
      ctx.closePath()
      ctx.fill()
      
      // 绘制数据点
      ctx.fillStyle = '#007bff'
      scores.forEach((score, index) => {
        const x = padding + (chartWidth / (scores.length - 1)) * index
        const y = padding + chartHeight - ((score - minScore) / scoreRange) * chartHeight
        
        ctx.beginPath()
        ctx.arc(x, y, 3, 0, 2 * Math.PI)
        ctx.fill()
      })
    }
    
    const performSingleAnalysis = async () => {
      singleAnalysisLoading.value = true
      try {
        // 生成唯一的 item_id
        singleAnalysisForm.order_data.items.forEach((item, index) => {
          item.item_id = `item_${index + 1}`
        })
        
        const response = await dvssAPI.analyzeOrder(singleAnalysisForm)
        
        if (response.data.success) {
          recentResults.value.unshift(response.data.data)
          if (recentResults.value.length > 10) {
            recentResults.value = recentResults.value.slice(0, 10)
          }
          
          alert('✅ 分析完成！')
          closeSingleAnalysis()
          await loadDashboard()
        } else {
          throw new Error(response.data.message || '分析失败')
        }
      } catch (error) {
        alert('分析失败: ' + error.message)
        console.error('Single analysis error:', error)
      } finally {
        singleAnalysisLoading.value = false
      }
    }
    
    const performBatchAnalysis = async () => {
      batchAnalysisLoading.value = true
      try {
        const response = await dvssAPI.batchAnalyzeOrders({
          orders: batchData.value,
          context: {}
        })
        
        if (response.data.success) {
          const results = response.data.data.results
          recentResults.value = [...results.slice(0, 10), ...recentResults.value.slice(0, 10 - results.length)]
          
          const stats = response.data.data.statistics
          alert(`✅ 批量分析完成！\n成功: ${stats.successful_analyses}\n失败: ${stats.failed_analyses}`)
          
          closeBatchAnalysis()
          await loadDashboard()
        } else {
          throw new Error(response.data.message || '批量分析失败')
        }
      } catch (error) {
        alert('批量分析失败: ' + error.message)
        console.error('Batch analysis error:', error)
      } finally {
        batchAnalysisLoading.value = false
      }
    }
    
    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target.result
          
          if (file.name.endsWith('.json')) {
            const data = JSON.parse(content)
            batchData.value = Array.isArray(data) ? data : [data]
          } else if (file.name.endsWith('.csv')) {
            // 简单的CSV解析（实际项目中应使用专门的CSV解析库）
            const lines = content.split('\n')
            const headers = lines[0].split(',')
            const orders = []
            
            for (let i = 1; i < lines.length; i++) {
              if (lines[i].trim()) {
                const values = lines[i].split(',')
                const order = {}
                headers.forEach((header, index) => {
                  order[header.trim()] = values[index]?.trim()
                })
                orders.push(order)
              }
            }
            batchData.value = orders
          }
          
          // 限制最多100个订单
          if (batchData.value.length > 100) {
            batchData.value = batchData.value.slice(0, 100)
            alert('⚠️ 文件包含超过100个订单，已截取前100个')
          }
        } catch (error) {
          alert('文件解析失败: ' + error.message)
          console.error('File parsing error:', error)
        }
      }
      reader.readAsText(file)
    }
    
    const addItem = () => {
      const newItemId = `item_${singleAnalysisForm.order_data.items.length + 1}`
      singleAnalysisForm.order_data.items.push({
        name: '',
        price: 0,
        quantity: 1,
        category: '',
        item_id: newItemId
      })
    }
    
    const removeItem = (index) => {
      if (singleAnalysisForm.order_data.items.length > 1) {
        singleAnalysisForm.order_data.items.splice(index, 1)
      }
    }
    
    const viewResultDetails = (result) => {
      selectedResult.value = result
      showResultDetails.value = true
    }
    
    const closeSingleAnalysis = () => {
      showSingleAnalysis.value = false
      // 重置表单
      Object.assign(singleAnalysisForm.order_data, {
        order_id: '',
        user_id: '',
        amount: 0,
        payment_method: '',
        items: [{ name: '', price: 0, quantity: 1, category: '', item_id: '1' }]
      })
      Object.assign(singleAnalysisForm.context, {
        session_duration: null,
        previous_orders_count: null,
        user_risk_score: null,
        location_risk: null
      })
    }
    
    const closeBatchAnalysis = () => {
      showBatchAnalysis.value = false
      batchData.value = []
    }
    
    const closeResultDetails = () => {
      showResultDetails.value = false
      selectedResult.value = null
    }
    
    // 辅助方法
    const formatScore = (score) => {
      return score ? (score * 100).toFixed(1) + '%' : '0.0%'
    }
    
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
    
    const getTrendLabel = (trend) => {
      const labels = {
        'increasing': '↗️ 上升',
        'decreasing': '↘️ 下降',
        'stable': '➡️ 稳定',
        'no_data': '📊 无数据'
      }
      return labels[trend] || '➡️ 稳定'
    }
    
    const getRiskLevelLabel = (level) => {
      const labels = {
        'CRITICAL': '🔴 极高',
        'HIGH': '🟠 高',
        'MEDIUM': '🟡 中',
        'LOW': '🟢 低',
        'MINIMAL': '⚪ 极低'
      }
      return labels[level] || level
    }
    
    const getRiskLevelClass = (level) => {
      const classes = {
        'CRITICAL': 'risk-critical',
        'HIGH': 'risk-high',
        'MEDIUM': 'risk-medium',
        'LOW': 'risk-low',
        'MINIMAL': 'risk-minimal'
      }
      return classes[level] || 'risk-unknown'
    }
    
    const getResultCardClass = (result) => {
      return `result-card-${result.risk_level?.toLowerCase() || 'unknown'}`
    }
    
    const getScoreCircleStyle = (score) => {
      const percentage = score * 100
      let color = '#28a745'
      
      if (percentage >= 80) color = '#dc3545'
      else if (percentage >= 60) color = '#fd7e14'
      else if (percentage >= 40) color = '#ffc107'
      else if (percentage >= 20) color = '#20c997'
      
      return {
        background: `conic-gradient(${color} ${percentage}%, #e9ecef ${percentage}%)`
      }
    }
    
    const getControlLabel = (control) => {
      const labels = {
        'mfa_required': '多因子认证',
        'admin_approval': '管理员审批',
        'time_limited': '时间限制',
        'authentication_required': '身份认证',
        'phone_verify': '手机验证',
        'email_verify': '邮箱验证',
        'manager_approval': '经理审批'
      }
      return labels[control] || control
    }
    
    const getEncryptionLabel = (level) => {
      const labels = {
        'maximum': '最高级别',
        'enhanced': '增强级别',
        'standard': '标准级别',
        'basic': '基础级别'
      }
      return labels[level] || level
    }
    
    const getMonitoringLabel = (level) => {
      const labels = {
        'real_time': '实时监控',
        'enhanced': '增强监控',
        'standard': '标准监控',
        'basic': '基础监控'
      }
      return labels[level] || level
    }
    
    const getRetentionLabel = (policy) => {
      const labels = {
        'minimal': '最短保留',
        'limited': '限制保留',
        'standard': '标准保留',
        'extended': '延长保留'
      }
      return labels[policy] || policy
    }
    
    const getVerificationLabel = (verification) => {
      return getControlLabel(verification)
    }
    
    const getFeatureLabel = (key) => {
      const labels = {
        'order_amount': '订单金额',
        'item_count': '商品数量',
        'payment_method': '支付方式',
        'hour_of_day': '下单时间',
        'day_of_week': '星期',
        'is_weekend': '周末订单',
        'user_session_duration': '会话时长',
        'previous_orders_count': '历史订单',
        'user_risk_score': '用户风险',
        'location_risk': '位置风险',
        'avg_item_price': '平均单价',
        'price_variance': '价格方差',
        'has_luxury_items': '奢侈品',
        'category_diversity': '品类多样性'
      }
      return labels[key] || key
    }
    
    const formatFeatureValue = (key, value) => {
      if (typeof value !== 'number') return value
      
      const formatters = {
        'order_amount': (v) => `$${v.toFixed(2)}`,
        'payment_method': (v) => v.toFixed(2),
        'hour_of_day': (v) => `${Math.floor(v)}:00`,
        'day_of_week': (v) => ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][Math.floor(v)] || v,
        'is_weekend': (v) => v > 0.5 ? '是' : '否',
        'has_luxury_items': (v) => v > 0.5 ? '是' : '否'
      }
      
      return formatters[key] ? formatters[key](value) : value.toFixed(2)
    }
    
    // 生命周期
    onMounted(async () => {
      await Promise.all([
        loadDashboard(),
        loadTrends()
      ])
    })
    
    return {
      // 数据
      dashboardLoading,
      dashboardData,
      trendsLoading,
      trendsError,
      trendsData,
      selectedTimeRange,
      recentResults,
      showSingleAnalysis,
      showBatchAnalysis,
      showResultDetails,
      selectedResult,
      singleAnalysisLoading,
      batchAnalysisLoading,
      singleAnalysisForm,
      batchData,
      timeRanges,
      trendsCanvas,
      
      // 方法
      loadDashboard,
      loadTrends,
      performSingleAnalysis,
      performBatchAnalysis,
      handleFileUpload,
      addItem,
      removeItem,
      viewResultDetails,
      closeSingleAnalysis,
      closeBatchAnalysis,
      closeResultDetails,
      formatScore,
      formatTimestamp,
      getTrendLabel,
      getRiskLevelLabel,
      getRiskLevelClass,
      getResultCardClass,
      getScoreCircleStyle,
      getControlLabel,
      getEncryptionLabel,
      getMonitoringLabel,
      getRetentionLabel,
      getVerificationLabel,
      getFeatureLabel,
      formatFeatureValue
    }
  }
}
</script>

<style scoped>
/* 这里是样式代码，由于内容很长，我会在下一个文件中提供完整的样式 */
</style>
