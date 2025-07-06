import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api/index'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const isLoggedIn = ref(false)
  const token = ref(localStorage.getItem('token') || null)

  // 预定义的用户角色映射
  const roleMapping = {
    platform: { 
      username: '平台管理', 
      role: 'platform', 
      roleName: '平台管理',
      access_level: 5,
      permissions: ['read_all', 'manage', 'admin']
    },
    auditor: { 
      username: '审计人员', 
      role: 'auditor', 
      roleName: '审计人员',
      access_level: 5,
      permissions: ['read_all', 'audit']
    },
    seller: { 
      username: '卖家', 
      role: 'seller', 
      roleName: '卖家',
      access_level: 3,
      permissions: ['read_order', 'read_customer', 'read_shipping']
    },
    payment_provider: { 
      username: '支付服务商', 
      role: 'payment_provider', 
      roleName: '支付服务商',
      access_level: 4,
      permissions: ['read_payment', 'write_payment']
    },
    logistics: { 
      username: '物流', 
      role: 'logistics', 
      roleName: '物流',
      access_level: 2,
      permissions: ['read_shipping', 'write_shipping']
    }
  }

  // 登录方法，接受 { username, password } 对象
  const login = async (loginForm) => {
    try {
      const { username, password } = loginForm
      
      // 使用 authAPI 进行登录
      const result = await authAPI.login(username, password)
      
      if (result.data.success) {
        const userData = result.data.data
        
        // 设置token
        if (userData.access_token) {
          token.value = userData.access_token
          localStorage.setItem('token', userData.access_token)
        }
        
        // 设置用户信息，合并预设的角色信息
        const roleInfo = roleMapping[username] || {}
        currentUser.value = {
          ...roleInfo,
          ...userData,
          id: username,
          username: roleInfo.username || userData.username || username,
          role: roleInfo.role || userData.role,
          role_name: roleInfo.roleName || userData.role_name,
          access_level: roleInfo.access_level || userData.access_level,
          permissions: roleInfo.permissions || userData.permissions || []
        }
        
        isLoggedIn.value = true
        return { success: true }
      } else {
        throw new Error(result.data.message || '登录失败')
      }
    } catch (error) {
      console.error('Login error:', error)
      throw new Error(error.message || '登录失败，请检查用户名和密码')
    }
  }

  // 登出方法
  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
    token.value = null
    localStorage.removeItem('token')
  }

  // 获取当前用户信息
  const getCurrentUser = () => {
    return currentUser.value
  }

  // 检查是否有特定权限
  const hasPermission = (permission) => {
    if (!currentUser.value || !currentUser.value.permissions) {
      return false
    }
    return currentUser.value.permissions.includes(permission) || 
           currentUser.value.permissions.includes('read_all')
  }

  // 初始化时检查本地存储的token
  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      token.value = storedToken
      // 这里可以添加验证token有效性的逻辑
    }
  }

  // 获取用户列表（用于角色选择等）
  const getUserList = () => {
    return Object.entries(roleMapping).map(([id, user]) => ({
      id,
      ...user
    }))
  }

  return {
    currentUser,
    isLoggedIn,
    token,
    login,
    logout,
    getCurrentUser,
    hasPermission,
    initAuth,
    getUserList
  }
})
