/**
 * 用户管理状态
 */
import { defineStore } from 'pinia'
import { userAPI } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('userManagement', {
  state: () => ({
    users: [],
    userDetail: null,
    userStats: null,
    loading: false,
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0
    }
  }),

  getters: {
    // 获取用户列表
    userList: (state) => state.users,
    
    // 获取当前用户详情
    currentUserDetail: (state) => state.userDetail,
    
    // 获取用户统计信息
    statistics: (state) => state.userStats,
    
    // 是否正在加载
    isLoading: (state) => state.loading,
    
    // 分页信息
    paginationInfo: (state) => state.pagination
  },

  actions: {
    // 获取用户列表
    async fetchUsers(params = {}) {
      this.loading = true
      try {
        const { data } = await userAPI.getUsers({
          page: this.pagination.current,
          size: this.pagination.pageSize,
          ...params
        })
        
        this.users = data.items
        this.pagination.total = data.total
        this.pagination.current = data.page
        this.pagination.pageSize = data.size
        
        return data
      } catch (error) {
        ElMessage.error(error.message || '获取用户列表失败')
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建用户
    async createUser(userData) {
      this.loading = true
      try {
        const { data } = await userAPI.createUser(userData)
        this.users.unshift(data)
        ElMessage.success('用户创建成功')
        return data
      } catch (error) {
        ElMessage.error(error.message || '用户创建失败')
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
