import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const isAuthenticated = ref(!!token.value)
  const isAdmin = ref(false)

  // 登录
  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      const { token: newToken, user: userData } = response.data
      
      // 设置token和用户信息
      token.value = newToken
      user.value = userData
      isAuthenticated.value = true
      
      // 检查是否为管理员（后台登录）
      isAdmin.value = userData.role === 'admin'
      
      // 存储到localStorage
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(userData))
      
      ElMessage.success('登录成功')
      
      // 根据角色跳转到不同页面
      if (isAdmin.value) {
        // 管理员跳转到后台
        router.push('/admin/dashboard')
      } else {
        // 普通用户跳转到前台
        router.push('/')
      }
      
      return response
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '登录失败')
      throw error
    }
  }

  // 管理员登录（专门的后台登录）
  const adminLogin = async (credentials) => {
    // 验证管理员账号
    if (credentials.username !== 'admin') {
      throw new Error('无效的管理员账号')
    }
    
    try {
      const response = await authAPI.adminLogin(credentials)
      const { token: newToken, user: userData } = response.data
      
      // 确保是管理员角色
      if (userData.role !== 'admin') {
        throw new Error('该账号不是管理员')
      }
      
      token.value = newToken
      user.value = userData
      isAuthenticated.value = true
      isAdmin.value = true
      
      localStorage.setItem('token', newToken)
      localStorage.setItem('user', JSON.stringify(userData))
      
      ElMessage.success('管理员登录成功')
      router.push('/admin/dashboard')
      
      return response
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '管理员登录失败')
      throw error
    }
  }

  // 注册（仅前台用户）
  const register = async (userData) => {
    try {
      // 前台注册的用户默认角色不能是admin
      if (userData.role === 'admin') {
        throw new Error('不能注册管理员账号')
      }
      
      const response = await authAPI.register(userData)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
      return response
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败')
      throw error
    }
  }

  // 登出
  const logout = () => {
    try {
      // 清除状态
      token.value = ''
      user.value = null
      isAuthenticated.value = false
      isAdmin.value = false
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      ElMessage.success('已退出登录')
      router.push('/')
    } catch (error) {
      ElMessage.error('退出登录失败')
    }
  }

  // 初始化用户信息
  const initUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser && token.value) {
      try {
        user.value = JSON.parse(storedUser)
        isAuthenticated.value = true
        isAdmin.value = user.value?.role === 'admin'
      } catch (error) {
        // 清除无效数据
        logout()
      }
    }
  }

  // 检查权限
  const hasPermission = (requiredRole) => {
    if (!user.value) return false
    
    // 管理员拥有所有权限
    if (user.value.role === 'admin') return true
    
    // 检查特定角色权限
    return user.value.role === requiredRole
  }

  // 获取用户可见字段
  const getVisibleFields = () => {
    if (!user.value) return []
    
    // 根据用户角色返回可见字段
    const roleFieldMap = {
      admin: ['*'], // 管理员可见所有字段
      merchant: ['order_id', 'customer_name', 'customer_phone', 'customer_email', 'product_name', 'product_price', 'product_quantity', 'payment_method', 'payment_amount', 'payment_status', 'created_at'],
      logistics: ['order_id', 'customer_name', 'customer_phone', 'shipping_address', 'shipping_method', 'shipping_status', 'product_name', 'product_quantity', 'created_at'],
      user: ['order_id', 'product_name', 'product_price', 'product_quantity', 'payment_status', 'shipping_status', 'created_at', 'updated_at'],
      platform: ['order_id', 'customer_name', 'product_name', 'product_price', 'product_quantity', 'payment_amount', 'payment_status', 'shipping_status', 'created_at'],
      auditor: ['*'] // 审计方可见所有字段
    }
    
    return roleFieldMap[user.value.role] || []
  }

  // 过滤数据字段（根据用户角色）
  const filterDataFields = (data) => {
    const visibleFields = getVisibleFields()
    
    // 如果可见所有字段
    if (visibleFields.includes('*')) {
      return data
    }
    
    // 过滤字段
    if (Array.isArray(data)) {
      return data.map(item => {
        const filtered = {}
        visibleFields.forEach(field => {
          if (item.hasOwnProperty(field)) {
            filtered[field] = item[field]
          }
        })
        return filtered
      })
    } else if (typeof data === 'object' && data !== null) {
      const filtered = {}
      visibleFields.forEach(field => {
        if (data.hasOwnProperty(field)) {
          filtered[field] = data[field]
        }
      })
      return filtered
    }
    
    return data
  }

  return {
    // 状态
    user,
    token,
    isAuthenticated,
    isAdmin,
    
    // 方法
    login,
    adminLogin,
    register,
    logout,
    initUser,
    hasPermission,
    getVisibleFields,
    filterDataFields
  }
})
