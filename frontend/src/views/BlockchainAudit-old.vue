<template>
  <div class="blockchain-audit">
    <div class="header">
      <h1>区块链审计</h1>
      <p class="subtitle">基于 Hyperledger Fabric 的不可篡改审计日志</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <h3>{{ blockchainStats.totalTransactions }}</h3>
            <p>总交易数</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⛓️</div>
          <div class="stat-info">
            <h3>{{ blockchainStats.currentBlock }}</h3>
            <p>当前区块高度</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔍</div>
          <div class="stat-info">
            <h3>{{ auditLogs.length }}</h3>
            <p>审计记录</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-info">
            <h3>{{ blockchainStats.status }}</h3>
            <p>网络状态</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="search-section">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索用户ID、操作类型或交易ID..."
            @keyup.enter="searchAuditLogs"
          />
          <button @click="searchAuditLogs" class="search-btn">
            <i class="icon">🔍</i>
          </button>
        </div>
        
        <div class="filter-options">
          <select v-model="selectedAction" @change="filterLogs">
            <option value="">所有操作</option>
            <option value="login">用户登录</option>
            <option value="data_access">数据访问</option>
            <option value="data_modification">数据修改</option>
            <option value="permission_change">权限变更</option>
            <option value="sensitive_operation">敏感操作</option>
          </select>
          
          <select v-model="selectedTimeRange" @change="filterLogs">
            <option value="1h">最近1小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
        </div>
      </div>
      
      <div class="action-buttons">
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          <i class="icon">🔄</i>
          {{ loading ? '刷新中...' : '刷新' }}
        </button>
        <button @click="exportLogs" class="export-btn">
          <i class="icon">📥</i>
          导出
        </button>
        <button @click="showCreateLogModal = true" class="create-btn">
          <i class="icon">➕</i>
          记录审计事件
        </button>
      </div>
    </div>

    <!-- 审计日志列表 -->
    <div class="audit-logs">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>正在加载审计记录...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <p>❌ {{ error }}</p>
        <button @click="refreshData" class="retry-btn">重试</button>
      </div>
      
      <div v-else-if="filteredLogs.length === 0" class="empty">
        <p>📋 暂无审计记录</p>
      </div>
      
      <div v-else class="logs-table">
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>用户ID</th>
              <th>操作类型</th>
              <th>资源</th>
              <th>状态</th>
              <th>IP地址</th>
              <th>详情</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in paginatedLogs" :key="log.id" :class="getLogRowClass(log)">
              <td>{{ formatTimestamp(log.timestamp) }}</td>
              <td>
                <span class="user-id">{{ log.user_id }}</span>
              </td>
              <td>
                <span :class="getActionClass(log.action)">
                  {{ getActionLabel(log.action) }}
                </span>
              </td>
              <td>{{ log.resource }}</td>
              <td>
                <span :class="getStatusClass(log.success)">
                  {{ log.success ? '成功' : '失败' }}
                </span>
              </td>
              <td>{{ log.ip_address || '-' }}</td>
              <td>
                <div class="details-preview">
                  {{ getDetailsPreview(log.details) }}
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click="viewLogDetails(log)" class="view-btn">
                    👁️
                  </button>
                  <button @click="verifyLog(log)" class="verify-btn">
                    🔐
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div v-if="filteredLogs.length > 0" class="pagination">
        <button 
          @click="currentPage > 1 && currentPage--" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        <button 
          @click="currentPage < totalPages && currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 日志详情弹窗 -->
    <div v-if="showLogDetails" class="modal-overlay" @click="closeLogDetails">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>审计日志详情</h3>
          <button @click="closeLogDetails" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedLog" class="log-details">
            <div class="detail-row">
              <strong>事件ID:</strong> {{ selectedLog.id }}
            </div>
            <div class="detail-row">
              <strong>用户ID:</strong> {{ selectedLog.user_id }}
            </div>
            <div class="detail-row">
              <strong>操作类型:</strong> {{ getActionLabel(selectedLog.action) }}
            </div>
            <div class="detail-row">
              <strong>资源:</strong> {{ selectedLog.resource }}
            </div>
            <div class="detail-row">
              <strong>时间:</strong> {{ formatTimestamp(selectedLog.timestamp) }}
            </div>
            <div class="detail-row">
              <strong>状态:</strong> 
              <span :class="getStatusClass(selectedLog.success)">
                {{ selectedLog.success ? '成功' : '失败' }}
              </span>
            </div>
            <div class="detail-row">
              <strong>IP地址:</strong> {{ selectedLog.ip_address || '未知' }}
            </div>
            <div class="detail-row">
              <strong>用户代理:</strong> {{ selectedLog.user_agent || '未知' }}
            </div>
            <div v-if="selectedLog.error_msg" class="detail-row">
              <strong>错误信息:</strong> 
              <span class="error-text">{{ selectedLog.error_msg }}</span>
            </div>
            <div class="detail-row">
              <strong>详细信息:</strong>
              <pre class="details-json">{{ formatDetails(selectedLog.details) }}</pre>
            </div>
            <div v-if="selectedLog.verification" class="detail-row">
              <strong>区块链验证:</strong>
              <span :class="selectedLog.verification.valid ? 'status-success' : 'status-error'">
                {{ selectedLog.verification.valid ? '✅ 已验证' : '❌ 验证失败' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建审计日志弹窗 -->
    <div v-if="showCreateLogModal" class="modal-overlay" @click="closeCreateLogModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>记录审计事件</h3>
          <button @click="closeCreateLogModal" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createAuditLog" class="create-form">
            <div class="form-group">
              <label>用户ID:</label>
              <input v-model="newLog.user_id" type="text" required />
            </div>
            <div class="form-group">
              <label>操作类型:</label>
              <select v-model="newLog.action" required>
                <option value="">请选择操作类型</option>
                <option value="login">用户登录</option>
                <option value="data_access">数据访问</option>
                <option value="data_modification">数据修改</option>
                <option value="permission_change">权限变更</option>
                <option value="sensitive_operation">敏感操作</option>
              </select>
            </div>
            <div class="form-group">
              <label>资源:</label>
              <input v-model="newLog.resource" type="text" required />
            </div>
            <div class="form-group">
              <label>详情:</label>
              <textarea v-model="newLog.details" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>
                <input v-model="newLog.success" type="checkbox" />
                操作成功
              </label>
            </div>
            <div v-if="!newLog.success" class="form-group">
              <label>错误信息:</label>
              <input v-model="newLog.error_msg" type="text" />
            </div>
            <div class="form-actions">
              <button type="button" @click="closeCreateLogModal" class="cancel-btn">
                取消
              </button>
              <button type="submit" :disabled="createLoading" class="submit-btn">
                {{ createLoading ? '提交中...' : '提交' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { blockchainAPI } from '@/api'

export default {
  name: 'BlockchainAudit',
  setup() {
    // 响应式数据
    const loading = ref(false)
    const error = ref('')
    const auditLogs = ref([])
    const blockchainStats = reactive({
      totalTransactions: 0,
      currentBlock: 0,
      status: '检查中...'
    })
    
    // 搜索和过滤
    const searchQuery = ref('')
    const selectedAction = ref('')
    const selectedTimeRange = ref('24h')
    
    // 分页
    const currentPage = ref(1)
    const pageSize = 20
    
    // 弹窗状态
    const showLogDetails = ref(false)
    const selectedLog = ref(null)
    const showCreateLogModal = ref(false)
    const createLoading = ref(false)
    
    // 新建日志表单
    const newLog = reactive({
      user_id: '',
      action: '',
      resource: '',
      details: '',
      success: true,
      error_msg: ''
    })
    
    // 计算属性
    const filteredLogs = computed(() => {
      let logs = auditLogs.value
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        logs = logs.filter(log => 
          log.user_id.toLowerCase().includes(query) ||
          log.action.toLowerCase().includes(query) ||
          log.resource.toLowerCase().includes(query) ||
          (log.id && log.id.toLowerCase().includes(query))
        )
      }
      
      // 操作类型过滤
      if (selectedAction.value) {
        logs = logs.filter(log => log.action === selectedAction.value)
      }
      
      // 时间范围过滤
      const now = new Date()
      const timeRanges = {
        '1h': 1 * 60 * 60 * 1000,
        '24h': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000,
        '30d': 30 * 24 * 60 * 60 * 1000
      }
      
      const timeLimit = now.getTime() - timeRanges[selectedTimeRange.value]
      logs = logs.filter(log => new Date(log.timestamp).getTime() > timeLimit)
      
      return logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredLogs.value.length / pageSize)
    })
    
    const paginatedLogs = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return filteredLogs.value.slice(start, end)
    })
    
    // 方法
    const loadAuditLogs = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await blockchainAPI.getAuditHistory()
        auditLogs.value = response.data.events || []
      } catch (err) {
        error.value = err.message || '加载审计日志失败'
        console.error('Load audit logs error:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadBlockchainStats = async () => {
      try {
        const response = await blockchainAPI.getBlockchainStatus()
        if (response.data.blockchain_info) {
          blockchainStats.totalTransactions = response.data.blockchain_info.height || 0
          blockchainStats.currentBlock = response.data.blockchain_info.currentBlockHash ? 
            response.data.blockchain_info.height : 0
        }
        blockchainStats.status = response.data.status === 'active' ? '正常' : '异常'
      } catch (err) {
        blockchainStats.status = '离线'
        console.error('Load blockchain stats error:', err)
      }
    }
    
    const refreshData = async () => {
      await Promise.all([
        loadAuditLogs(),
        loadBlockchainStats()
      ])
    }
    
    const searchAuditLogs = () => {
      currentPage.value = 1
    }
    
    const filterLogs = () => {
      currentPage.value = 1
    }
    
    const viewLogDetails = async (log) => {
      selectedLog.value = log
      
      // 验证区块链记录
      try {
        const verification = await blockchainAPI.verifyTransaction(log.id)
        selectedLog.value.verification = verification.data
      } catch (err) {
        selectedLog.value.verification = { valid: false, error: err.message }
      }
      
      showLogDetails.value = true
    }
    
    const closeLogDetails = () => {
      showLogDetails.value = false
      selectedLog.value = null
    }
    
    const verifyLog = async (log) => {
      try {
        const response = await blockchainAPI.verifyTransaction(log.id)
        if (response.data.valid) {
          alert('✅ 区块链验证通过，记录完整性正常')
        } else {
          alert('❌ 区块链验证失败，记录可能被篡改')
        }
      } catch (err) {
        alert('验证失败: ' + err.message)
      }
    }
    
    const createAuditLog = async () => {
      createLoading.value = true
      
      try {
        await blockchainAPI.logAuditEvent({
          user_id: newLog.user_id,
          action: newLog.action,
          resource: newLog.resource,
          details: newLog.details,
          success: newLog.success,
          error_msg: newLog.error_msg
        })
        
        alert('✅ 审计事件记录成功')
        closeCreateLogModal()
        await loadAuditLogs()
      } catch (err) {
        alert('记录失败: ' + err.message)
      } finally {
        createLoading.value = false
      }
    }
    
    const closeCreateLogModal = () => {
      showCreateLogModal.value = false
      Object.assign(newLog, {
        user_id: '',
        action: '',
        resource: '',
        details: '',
        success: true,
        error_msg: ''
      })
    }
    
    const exportLogs = () => {
      const data = filteredLogs.value.map(log => ({
        时间: formatTimestamp(log.timestamp),
        用户ID: log.user_id,
        操作类型: getActionLabel(log.action),
        资源: log.resource,
        状态: log.success ? '成功' : '失败',
        IP地址: log.ip_address || '',
        详情: log.details
      }))
      
      const csv = convertToCSV(data)
      downloadCSV(csv, 'audit_logs.csv')
    }
    
    // 辅助方法
    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
    
    const getActionLabel = (action) => {
      const labels = {
        'login': '用户登录',
        'data_access': '数据访问',
        'data_modification': '数据修改',
        'permission_change': '权限变更',
        'sensitive_operation': '敏感操作'
      }
      return labels[action] || action
    }
    
    const getActionClass = (action) => {
      const classes = {
        'login': 'action-login',
        'data_access': 'action-access',
        'data_modification': 'action-modify',
        'permission_change': 'action-permission',
        'sensitive_operation': 'action-sensitive'
      }
      return classes[action] || 'action-default'
    }
    
    const getStatusClass = (success) => {
      return success ? 'status-success' : 'status-error'
    }
    
    const getLogRowClass = (log) => {
      if (!log.success) return 'row-error'
      if (log.action === 'sensitive_operation') return 'row-sensitive'
      return ''
    }
    
    const getDetailsPreview = (details) => {
      if (!details) return '-'
      return details.length > 50 ? details.substring(0, 50) + '...' : details
    }
    
    const formatDetails = (details) => {
      try {
        return JSON.stringify(JSON.parse(details), null, 2)
      } catch {
        return details
      }
    }
    
    const convertToCSV = (data) => {
      const headers = Object.keys(data[0])
      const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(h => `"${row[h]}"`).join(','))
      ].join('\n')
      return csvContent
    }
    
    const downloadCSV = (csv, filename) => {
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = filename
      link.click()
    }
    
    // 生命周期
    onMounted(() => {
      refreshData()
    })
    
    return {
      // 数据
      loading,
      error,
      auditLogs,
      blockchainStats,
      searchQuery,
      selectedAction,
      selectedTimeRange,
      currentPage,
      showLogDetails,
      selectedLog,
      showCreateLogModal,
      createLoading,
      newLog,
      
      // 计算属性
      filteredLogs,
      totalPages,
      paginatedLogs,
      
      // 方法
      refreshData,
      searchAuditLogs,
      filterLogs,
      viewLogDetails,
      closeLogDetails,
      verifyLog,
      createAuditLog,
      closeCreateLogModal,
      exportLogs,
      formatTimestamp,
      getActionLabel,
      getActionClass,
      getStatusClass,
      getLogRowClass,
      getDetailsPreview,
      formatDetails
    }
  }
}
</script>

<style scoped>
.blockchain-audit {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #1a1a1a;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.control-panel {
  margin-bottom: 30px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 32px;
}

.stat-info h3 {
  margin: 0;
  font-size: 24px;
  color: #1a1a1a;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 14px;
}

.action-bar {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
}

.search-box input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  width: 300px;
  font-size: 14px;
}

.search-btn {
  padding: 10px 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  margin-left: 10px;
  cursor: pointer;
}

.filter-options {
  display: flex;
  gap: 10px;
}

.filter-options select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.action-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.refresh-btn {
  background: #28a745;
  color: white;
}

.export-btn {
  background: #17a2b8;
  color: white;
}

.create-btn {
  background: #007bff;
  color: white;
}

.audit-logs {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.loading, .error, .empty {
  padding: 40px;
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.logs-table table {
  width: 100%;
  border-collapse: collapse;
}

.logs-table th,
.logs-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.logs-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.logs-table tr:hover {
  background: #f8f9fa;
}

.row-error {
  background: #fff5f5 !important;
}

.row-sensitive {
  background: #fff8e1 !important;
}

.user-id {
  font-family: monospace;
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.action-login { color: #28a745; }
.action-access { color: #17a2b8; }
.action-modify { color: #ffc107; }
.action-permission { color: #dc3545; }
.action-sensitive { color: #6f42c1; }

.status-success { color: #28a745; font-weight: 600; }
.status-error { color: #dc3545; font-weight: 600; }

.details-preview {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.view-btn, .verify-btn {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.view-btn {
  background: #e9ecef;
}

.verify-btn {
  background: #d4edda;
}

.pagination {
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 20px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.log-details .detail-row {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.details-json {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.create-form .form-group {
  margin-bottom: 20px;
}

.create-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
}

.create-form input,
.create-form select,
.create-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-text {
  color: #dc3545;
  font-family: monospace;
  font-size: 12px;
}

@media (max-width: 768px) {
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section {
    justify-content: center;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .logs-table {
    overflow-x: auto;
  }
  
  .modal-content {
    margin: 20px;
    max-width: calc(100vw - 40px);
  }
}
</style>
