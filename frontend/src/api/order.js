/**
 * 订单管理API
 */
import { api } from './index'

export const orderAPI = {
  // 获取订单列表
  getOrders: (params = {}) => {
    return api.get('/orders', params)
  },

  // 获取订单详情
  getOrderById: (id) => {
    return api.get(`/orders/${id}`)
  },

  // 创建订单
  createOrder: (orderData) => {
    return api.post('/orders', orderData)
  },

  // 更新订单
  updateOrder: (id, orderData) => {
    return api.put(`/orders/${id}`, orderData)
  },

  // 删除订单
  deleteOrder: (id) => {
    return api.delete(`/orders/${id}`)
  },

  // 上传订单文件
  uploadOrders: (fileData) => {
    return api.upload('/orders/upload', fileData)
  },

  // 加密订单
  encryptOrder: (id, encryptionConfig) => {
    return api.post(`/orders/${id}/encrypt`, encryptionConfig)
  },

  // 批量加密订单
  batchEncryptOrders: (encryptionData) => {
    return api.post('/orders/batch-encrypt', encryptionData)
  },

  // 获取订单敏感度分析
  getOrderSensitivity: (id) => {
    return api.get(`/orders/${id}/sensitivity`)
  },

  // 导出订单数据
  exportOrders: (params = {}) => {
    return api.get('/orders/export', params)
  },

  // 获取订单统计信息
  getOrderStats: () => {
    return api.get('/orders/stats')
  },

  // 获取加密订单列表
  getEncryptedOrders: (params = {}) => {
    return api.get('/encrypted-orders', params)
  },

  // 获取加密订单详情
  getEncryptedOrderById: (id) => {
    return api.get(`/encrypted-orders/${id}`)
  },

  // 解密订单
  decryptOrder: (id, decryptionData) => {
    return api.post(`/encrypted-orders/${id}/decrypt`, decryptionData)
  },

  // 删除加密订单
  deleteEncryptedOrder: (id) => {
    return api.delete(`/encrypted-orders/${id}`)
  },

  // 验证订单完整性
  verifyOrderIntegrity: (id) => {
    return api.post(`/encrypted-orders/${id}/verify`)
  }
}
