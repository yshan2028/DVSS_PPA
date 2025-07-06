import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api/index'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(null)
  const isLoggedIn = ref(false)

  const users = ref({
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
    },
    auditor: { 
      username: '审计', 
      role: 'auditor', 
      roleName: '审计',
      access_level: 5,
      permissions: ['read_all', 'audit']
    },
    platform: { 
      username: '平台', 
      role: 'platform', 
      roleName: '平台',
      access_level: 5,
      permissions: ['read_all', 'manage']
    }
  })

  const login = async (userId) => {
    try {
      // 使用新的authAPI
      const result = await authAPI.login(userId, '123456')
      
      if (result.data.success) {
        const userData = result.data.data
        // 设置token
        if (userData.access_token) {
          localStorage.setItem('token', userData.access_token)
        }
        
        // 设置用户信息，合并预设的角色信息
        const userInfo = users.value[userId] || {}
        currentUser.value = {
          ...userInfo,
          ...userData,
          id: userId,
          username: userInfo.username || userData.username,
          role: userInfo.role || userData.role,
          role_name: userInfo.roleName || userData.role_name,
          access_level: userInfo.access_level || userData.access_level,
          permissions: userInfo.permissions || userData.permissions || []
        }
        isLoggedIn.value = true
        return { success: true }
      } else {
        throw new Error(result.data.message || 'Login failed')
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: error.message }
    }
  }

  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
    localStorage.removeItem('token')
  }

  const getUserList = () => {
    return Object.entries(users.value).map(([id, user]) => ({
      id,
      ...user
    }))
  }

  return {
    currentUser,
    isLoggedIn,
    users,
    login,
    logout,
    getUserList
  }
})
