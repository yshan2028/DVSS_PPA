/**
 * 认证相关API
 */
import { api } from './index'

export const authAPI = {
  // 用户登录
  login: (loginData) => {
    return api.post('/auth/login', loginData)
  },

  // 管理员登录
  adminLogin: (loginData) => {
    return api.post('/auth/admin/login', loginData)
  },

  // 用户注册
  register: (registerData) => {
    return api.post('/auth/register', registerData)
  },

  // 用户登出
  logout: () => {
    return api.post('/auth/logout')
  },

  // 刷新Token
  refreshToken: () => {
    return api.post('/auth/refresh')
  },

  // 获取当前用户信息
  getProfile: () => {
    return api.get('/auth/profile')
  },

  // 更新用户信息
  updateProfile: (profileData) => {
    return api.put('/auth/profile', profileData)
  },

  // 修改密码
  changePassword: (passwordData) => {
    return api.post('/auth/change-password', passwordData)
  },

  // 重置密码
  resetPassword: (email) => {
    return api.post('/auth/reset-password', { email })
  },

  // 验证Token
  verifyToken: (token) => {
    return api.post('/auth/verify-token', { token })
  }
}
