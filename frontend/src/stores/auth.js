/**
 * 认证状态管理
 */
import { defineStore } from 'pinia'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    isLoggedIn: false,
    permissions: [],
    roles: []
  }),

  getters: {
    // 是否已登录
    isAuthenticated: (state) => !!state.token && !!state.user,
    
    // 获取用户角色
    userRoles: (state) => state.roles,
    
    // 获取用户权限
    userPermissions: (state) => state.permissions,
    
    // 检查是否有特定权限
    hasPermission: (state) => (permission) => {
      return state.permissions.includes(permission)
    },
    
    // 检查是否有特定角色
    hasRole: (state) => (role) => {
      return state.roles.some(r => r.name === role)
    },
    
    // 是否为管理员
    isAdmin: (state) => state.user?.is_superuser || false,
    
    // 获取用户信息
    userInfo: (state) => state.user
  },

  actions: {
    // 登录
    async login(loginData) {
      try {
        const { data } = await authAPI.login(loginData)
        
        this.token = data.access_token
        this.user = data.user
        this.permissions = data.permissions || []
        this.roles = data.roles || []
        this.isLoggedIn = true
        
        // 保存到本地存储
        localStorage.setItem('token', this.token)
        localStorage.setItem('user', JSON.stringify(this.user))
        
        ElMessage.success('登录成功')
        return { success: true, data }
      } catch (error) {
        ElMessage.error(error.message || '登录失败')
        return { success: false, error }
      }
    },

    // 登出
    async logout() {
      try {
        if (this.token) {
          await authAPI.logout()
        }
      } catch (error) {
        console.warn('登出请求失败:', error)
      } finally {
        this.clearAuth()
        ElMessage.success('已安全登出')
      }
    },

    // 清除认证信息
    clearAuth() {
      this.token = null
      this.user = null
      this.permissions = []
      this.roles = []
      this.isLoggedIn = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    // 刷新Token
    async refreshToken() {
      try {
        const { data } = await authAPI.refreshToken()
        this.token = data.access_token
        localStorage.setItem('token', this.token)
        return true
      } catch (error) {
        console.error('刷新Token失败:', error)
        this.clearAuth()
        return false
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        const { data } = await authAPI.getProfile()
        this.user = data
        localStorage.setItem('user', JSON.stringify(this.user))
        return data
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },

    // 初始化认证状态
    initAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')
      
      if (token && user) {
        try {
          this.token = token
          this.user = JSON.parse(user)
          this.isLoggedIn = true
        } catch (error) {
          console.error('初始化认证状态失败:', error)
          this.clearAuth()
        }
      }
    }
  }
})
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
  })

  const login = async (userId) => {
    try {
      // 使用新的authAPI，密码与后端一致
      const result = await authAPI.login(userId, 'admin')
      
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
