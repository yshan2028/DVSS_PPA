/**
 * 用户管理API
 */
import { api } from './index'

export const userAPI = {
  // 获取用户列表
  getUsers: (params = {}) => {
    return api.get('/users', params)
  },

  // 获取用户详情
  getUserById: (id) => {
    return api.get(`/users/${id}`)
  },

  // 创建用户
  createUser: (userData) => {
    return api.post('/users', userData)
  },

  // 更新用户
  updateUser: (id, userData) => {
    return api.put(`/users/${id}`, userData)
  },

  // 删除用户
  deleteUser: (id) => {
    return api.delete(`/users/${id}`)
  },

  // 重置用户密码
  resetUserPassword: (id, passwordData) => {
    return api.post(`/users/${id}/reset-password`, passwordData)
  },

  // 启用/禁用用户
  toggleUserStatus: (id, status) => {
    return api.put(`/users/${id}/status`, { is_active: status })
  },

  // 批量操作用户
  batchOperation: (operation, userIds) => {
    return api.post('/users/batch', {
      operation,
      user_ids: userIds
    })
  },

  // 导出用户数据
  exportUsers: (params = {}) => {
    return api.get('/users/export', params)
  },

  // 获取用户统计信息
  getUserStats: () => {
    return api.get('/users/stats')
  }
}
