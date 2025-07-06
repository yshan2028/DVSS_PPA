/**
 * 日志管理API
 */
import { api } from './index'

export const logAPI = {
  // 获取操作日志
  getOperationLogs: (params = {}) => {
    return api.get('/logs/operations', params)
  },

  // 获取操作日志详情
  getOperationLogById: (id) => {
    return api.get(`/logs/operations/${id}`)
  },

  // 导出操作日志
  exportOperationLogs: (params = {}) => {
    return api.get('/logs/operations/export', params)
  },

  // 获取操作统计
  getOperationStats: (params = {}) => {
    return api.get('/logs/operations/stats', params)
  },

  // 获取用户操作日志
  getUserOperationLogs: (userId, params = {}) => {
    return api.get(`/logs/operations/user/${userId}`, params)
  },

  // 获取资源操作日志
  getResourceOperationLogs: (resourceType, resourceId, params = {}) => {
    return api.get(`/logs/operations/resource/${resourceType}/${resourceId}`, params)
  },

  // 清理过期日志
  cleanupExpiredLogs: (days) => {
    return api.post('/logs/operations/cleanup', { days })
  },

  // 获取日志摘要
  getLogSummary: (timeRange) => {
    return api.get('/logs/operations/summary', { time_range: timeRange })
  },

  // 搜索日志
  searchLogs: (searchParams) => {
    return api.post('/logs/operations/search', searchParams)
  },

  // 获取异常日志
  getErrorLogs: (params = {}) => {
    return api.get('/logs/operations/errors', params)
  }
}
