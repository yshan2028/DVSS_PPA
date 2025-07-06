/**
 * Fabric区块链API (Go后端)
 */
import axios from 'axios'

const fabricAPI = axios.create({
  baseURL: import.meta.env.VITE_GO_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
fabricAPI.interceptors.request.use(
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

// 响应拦截器
fabricAPI.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('Fabric API Error:', error)
    return Promise.reject(error.response?.data || error)
  }
)

export const fabricAPIService = {
  // 加密日志相关
  encryption: {
    // 记录加密日志
    logEncryption: (logData) => {
      return fabricAPI.post('/fabric/encryption/log', logData)
    },

    // 获取加密日志列表
    getEncryptionLogs: (params = {}) => {
      return fabricAPI.get('/fabric/encryption/logs', { params })
    },

    // 获取加密日志详情
    getEncryptionLogById: (id) => {
      return fabricAPI.get(`/fabric/encryption/logs/${id}`)
    },

    // 按订单查询加密日志
    getEncryptionLogsByOrder: (orderId) => {
      return fabricAPI.get(`/fabric/encryption/logs/order/${orderId}`)
    }
  },

  // 解密日志相关
  decryption: {
    // 记录解密日志
    logDecryption: (logData) => {
      return fabricAPI.post('/fabric/decryption/log', logData)
    },

    // 获取解密日志列表
    getDecryptionLogs: (params = {}) => {
      return fabricAPI.get('/fabric/decryption/logs', { params })
    },

    // 获取解密日志详情
    getDecryptionLogById: (id) => {
      return fabricAPI.get(`/fabric/decryption/logs/${id}`)
    },

    // 按订单查询解密日志
    getDecryptionLogsByOrder: (orderId) => {
      return fabricAPI.get(`/fabric/decryption/logs/order/${orderId}`)
    }
  },

  // 查询日志相关
  query: {
    // 记录查询日志
    logQuery: (logData) => {
      return fabricAPI.post('/fabric/query/log', logData)
    },

    // 获取查询日志列表
    getQueryLogs: (params = {}) => {
      return fabricAPI.get('/fabric/query/logs', { params })
    },

    // 获取查询日志详情
    getQueryLogById: (id) => {
      return fabricAPI.get(`/fabric/query/logs/${id}`)
    },

    // 按用户查询日志
    getQueryLogsByUser: (userId) => {
      return fabricAPI.get(`/fabric/query/logs/user/${userId}`)
    }
  },

  // 审计统计相关
  audit: {
    // 获取审计统计
    getAuditStats: (params = {}) => {
      return fabricAPI.get('/fabric/audit/stats', { params })
    },

    // 获取加密操作统计
    getEncryptionStats: (params = {}) => {
      return fabricAPI.get('/fabric/audit/stats/encryption', { params })
    },

    // 获取解密操作统计
    getDecryptionStats: (params = {}) => {
      return fabricAPI.get('/fabric/audit/stats/decryption', { params })
    },

    // 获取查询操作统计
    getQueryStats: (params = {}) => {
      return fabricAPI.get('/fabric/audit/stats/query', { params })
    },

    // 获取操作时间线
    getOperationTimeline: (params = {}) => {
      return fabricAPI.get('/fabric/audit/timeline', { params })
    },

    // 导出审计报告
    exportAuditReport: (params = {}) => {
      return fabricAPI.get('/fabric/audit/export', { params })
    }
  },

  // 区块链网络状态
  network: {
    // 获取网络状态
    getNetworkStatus: () => {
      return fabricAPI.get('/fabric/network/status')
    },

    // 获取节点信息
    getNodeInfo: () => {
      return fabricAPI.get('/fabric/network/nodes')
    },

    // 获取通道信息
    getChannelInfo: () => {
      return fabricAPI.get('/fabric/network/channels')
    },

    // 获取链码信息
    getChaincodeInfo: () => {
      return fabricAPI.get('/fabric/network/chaincode')
    }
  }
}
