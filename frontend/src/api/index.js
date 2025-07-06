import axios from 'axios'

// Python后端API (端口8000)
const pythonAPI = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Go后端API (端口8001) - 专门处理Fabric
const goAPI = axios.create({
  baseURL: '/fabric-api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器 - Python API
pythonAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 请求拦截器 - Go API
goAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - Python API
pythonAPI.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('Python API Error:', error)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

// 响应拦截器 - Go API
goAPI.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('Go API Error:', error)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

// ===========================================
// Python 后端 API (核心业务逻辑)
// ===========================================

// 认证相关
export const authAPI = {
  login: (username, password) => pythonAPI.post('/v1/auth/login', { username, password }),
  register: (userData) => pythonAPI.post('/v1/auth/register', userData),
  logout: () => pythonAPI.post('/v1/auth/logout'),
  getCurrentUser: () => pythonAPI.get('/v1/auth/me'),
  refreshToken: () => pythonAPI.post('/v1/auth/refresh'),
  getRoles: () => pythonAPI.get('/v1/auth/roles'),
  getUsers: () => pythonAPI.get('/v1/auth/users'),
  getUserPermissions: (userId) => pythonAPI.get(`/v1/auth/user/${userId}/permissions`)
}

// DVSS 分析相关
export const dvssAPI = {
  analyzeOrder: (orderData) => pythonAPI.post('/v1/dvss/analyze', orderData),
  batchAnalyzeOrders: (batchData) => pythonAPI.post('/v1/dvss/batch-analyze', batchData),
  getSensitivityTrends: (params) => pythonAPI.get('/v1/dvss/trends', { params }),
  getDashboard: () => pythonAPI.get('/v1/dvss/dashboard'),
  healthCheck: () => pythonAPI.get('/v1/dvss/health'),
}

// 数据管理相关
export const dataAPI = {
  // 订单管理
  getOrders: (params) => pythonAPI.get('/v1/orders', { params }),
  getOrder: (orderId) => pythonAPI.get(`/v1/orders/${orderId}`),
  createOrder: (orderData) => pythonAPI.post('/v1/orders', orderData),
  updateOrder: (orderId, orderData) => pythonAPI.put(`/v1/orders/${orderId}`, orderData),
  deleteOrder: (orderId) => pythonAPI.delete(`/v1/orders/${orderId}`),
  
  // 通用数据查询
  query: (dataId, userId) => pythonAPI.get(`/v1/data/query/${dataId}?user_id=${userId}`),
  getAllData: () => pythonAPI.get('/v1/data/debug/all')
}

// 加密相关
export const encryptionAPI = {
  encrypt: (data) => pythonAPI.post('/v1/encrypt/encrypt', data),
  decrypt: (dataId, userId) => pythonAPI.get(`/v1/encrypt/decrypt/${dataId}?user_id=${userId}`),
  encryptData: (data) => pythonAPI.post('/v1/encryption/encrypt', data),
  decryptData: (encryptedData) => pythonAPI.post('/v1/encryption/decrypt', encryptedData),
  generateKeys: () => pythonAPI.post('/v1/encryption/generate-keys'),
  getEncryptionStatus: () => pythonAPI.get('/v1/encryption/status'),
}

// 权限管理相关
export const rbacAPI = {
  getUserPermissions: (userId) => pythonAPI.get(`/v1/rbac/users/${userId}/permissions`),
  updateUserPermissions: (userId, permissions) => 
    pythonAPI.put(`/v1/rbac/users/${userId}/permissions`, permissions),
  getRoles: () => pythonAPI.get('/v1/rbac/roles'),
  createRole: (roleData) => pythonAPI.post('/v1/rbac/roles', roleData),
  updateRole: (roleId, roleData) => pythonAPI.put(`/v1/rbac/roles/${roleId}`, roleData),
  deleteRole: (roleId) => pythonAPI.delete(`/v1/rbac/roles/${roleId}`),
}

// 监控相关
export const monitoringAPI = {
  getStats: () => pythonAPI.get('/v1/monitor/stats'),
  getPerformance: () => pythonAPI.get('/v1/monitor/performance'),
  getHealth: () => pythonAPI.get('/v1/monitor/health'),
}

// ===========================================
// Go 后端 API (区块链和审计)
// ===========================================

// 审计相关
export const auditAPI = {
  logEvent: (eventData) => goAPI.post('/audit/log', eventData),
  getAuditHistory: (params) => goAPI.get('/audit/history', { params }),
  getAuditLogs: (params) => goAPI.get('/v1/audit/logs', { params }),
  getAuditStats: () => goAPI.get('/v1/audit/stats'),
  exportAuditLogs: (params) => goAPI.get('/v1/audit/export', { params }),
}

// 区块链相关
export const blockchainAPI = {
  // 新版本 API
  getBlockchainStatus: () => goAPI.get('/blockchain/status'),
  verifyTransaction: (txId) => goAPI.get(`/blockchain/verify/${txId}`),
  getBlockInfo: (blockId) => goAPI.get(`/blockchain/blocks/${blockId}`),
  getTransactionHistory: (params) => goAPI.get('/blockchain/transactions', { params }),
  getRawTransactionData: (txHash) => goAPI.get(`/v1/blockchain/tx/${txHash}/raw`),
  verifyTransactionIntegrity: (txHash) => goAPI.get(`/v1/blockchain/tx/${txHash}/verify`),
  
  // 审计日志
  logAuditEvent: (eventData) => goAPI.post('/audit/log', eventData),
  getAuditHistory: (params) => goAPI.get('/audit/history', { params }),
  
  // 兼容旧版本 API
  getRecords: () => goAPI.get('/v1/blockchain/records'),
  verifyRecord: (dataId) => goAPI.get(`/v1/blockchain/verify/${dataId}`),
  submitTransaction: (data) => goAPI.post('/v1/blockchain/submit', data),
  getStatus: () => goAPI.get('/v1/blockchain/status'),
  getNetworkInfo: () => goAPI.get('/v1/network/info'),
  getPeers: () => goAPI.get('/v1/network/peers'),
  getChannels: () => goAPI.get('/v1/network/channels'),
}

// 智能合约相关
export const contractAPI = {
  invokeContract: (contractData) => goAPI.post('/contract/invoke', contractData),
  queryContract: (queryData) => goAPI.post('/contract/query', queryData),
  getContractInfo: (contractId) => goAPI.get(`/contract/info/${contractId}`),
}

// Fabric 健康检查
export const fabricAPI = {
  getHealth: () => goAPI.get('/health'),
  getStats: () => goAPI.get('/stats'),
  getFabricHealth: () => goAPI.get('/v1/health'),
  getFabricStats: () => goAPI.get('/v1/stats')
}

// 健康检查
export const healthAPI = {
  pythonHealth: () => pythonAPI.get('/health'),
  goHealth: () => goAPI.get('/health'),
  systemHealth: () => Promise.all([
    pythonAPI.get('/health').catch(e => ({ error: e.message })),
    goAPI.get('/health').catch(e => ({ error: e.message }))
  ]).then(([python, go]) => ({
    python: python.data || python,
    go: go.data || go,
    timestamp: new Date().toISOString()
  }))
}

// ===========================================
// 组合 API (跨后端调用)
// ===========================================

// 完整的订单分析流程
export const fullAnalysisAPI = {
  async analyzeOrderWithAudit(orderData) {
    try {
      // 1. 进行 DVSS 分析
      const analysisResult = await dvssAPI.analyzeOrder(orderData)
      
      // 2. 记录审计日志
      await auditAPI.logEvent({
        user_id: orderData.order_data?.user_id || orderData.user_id || 'system',
        action: 'dvss_analysis',
        resource: 'order',
        details: JSON.stringify({
          order_id: orderData.order_data?.order_id || orderData.order_id,
          sensitivity_score: analysisResult.data?.data?.sensitivity_score,
          risk_level: analysisResult.data?.data?.risk_level
        }),
        success: true
      })
      
      return analysisResult
    } catch (error) {
      // 记录失败的审计日志
      try {
        await auditAPI.logEvent({
          user_id: orderData.order_data?.user_id || orderData.user_id || 'system',
          action: 'dvss_analysis',
          resource: 'order',
          details: JSON.stringify({
            order_id: orderData.order_data?.order_id || orderData.order_id,
            error: error.message
          }),
          success: false,
          error_msg: error.message
        })
      } catch (auditError) {
        console.error('Failed to log audit event:', auditError)
      }
      
      throw error
    }
  },
  
  async encryptWithAudit(data, userId) {
    try {
      // 1. 执行加密
      const encryptResult = await encryptionAPI.encrypt(data)
      
      // 2. 记录审计日志
      await auditAPI.logEvent({
        user_id: userId,
        action: 'data_encryption',
        resource: 'data',
        details: JSON.stringify({
          data_type: typeof data,
          encryption_method: 'aes-256'
        }),
        success: true
      })
      
      return encryptResult
    } catch (error) {
      await auditAPI.logEvent({
        user_id: userId,
        action: 'data_encryption',
        resource: 'data',
        details: JSON.stringify({ error: error.message }),
        success: false,
        error_msg: error.message
      })
      
      throw error
    }
  }
}

// 订单相关API
export const orderAPI = {
  getOrders: (params) => pythonAPI.get('/v1/dvss/orders', { params }),
  getOrder: (orderId) => pythonAPI.get(`/v1/dvss/orders/${orderId}`),
  getRecentUploads: (params) => pythonAPI.get('/v1/dvss/recent-uploads', { params }),
  uploadOrder: (orderData) => pythonAPI.post('/v1/dvss/upload', orderData),
  batchUpload: (formData) => pythonAPI.post('/v1/dvss/batch-upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  exportOrders: (orderIds) => pythonAPI.post('/v1/dvss/export', { order_ids: orderIds }),
}

// 导出所有 API
export default {
  auth: authAPI,
  dvss: dvssAPI,
  data: dataAPI,
  encryption: encryptionAPI,
  rbac: rbacAPI,
  monitoring: monitoringAPI,
  audit: auditAPI,
  blockchain: blockchainAPI,
  contract: contractAPI,
  fabric: fabricAPI,
  health: healthAPI,
  fullAnalysis: fullAnalysisAPI,
  
  // 原始 axios 实例（如果需要直接使用）
  pythonAPI,
  goAPI
}
