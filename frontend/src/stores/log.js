import { defineStore } from 'pinia'
import { logAPI } from '@/api/log'

export const useLogStore = defineStore('log', {
  state: () => ({
    logList: [],
    currentLog: null,
    pagination: {
      page: 1,
      size: 20,
      total: 0
    },
    loading: false,
    searchParams: {},
    logStats: {
      todayCount: 0,
      weekCount: 0,
      monthCount: 0,
      totalCount: 0
    }
  }),

  getters: {
    // 获取日志总数
    totalLogs: (state) => state.pagination.total,
    
    // 获取当前页日志列表
    currentPageLogs: (state) => state.logList,
    
    // 根据操作类型过滤日志
    logsByAction: (state) => (action) => {
      return state.logList.filter(log => log.action === action)
    },
    
    // 根据用户过滤日志
    logsByUser: (state) => (username) => {
      return state.logList.filter(log => log.username === username)
    },
    
    // 获取成功的日志数量
    successLogsCount: (state) => {
      return state.logList.filter(log => log.status === 'success').length
    },
    
    // 获取失败的日志数量
    failedLogsCount: (state) => {
      return state.logList.filter(log => log.status === 'failed').length
    },
    
    // 获取今天的日志数量
    todayLogsCount: (state) => {
      const today = new Date().toDateString()
      return state.logList.filter(log => 
        new Date(log.createdAt).toDateString() === today
      ).length
    }
  },

  actions: {
    // 获取日志列表
    async getLogList(params = {}) {
      this.loading = true
      try {
        const response = await logAPI.getLogList(params)
        this.logList = response.data.items || []
        this.pagination = {
          page: response.data.page || 1,
          size: response.data.size || 20,
          total: response.data.total || 0
        }
        this.searchParams = params
        return response
      } catch (error) {
        console.error('获取日志列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取日志详情
    async getLogDetail(logId) {
      try {
        const response = await logAPI.getLogDetail(logId)
        this.currentLog = response.data
        return response
      } catch (error) {
        console.error('获取日志详情失败:', error)
        throw error
      }
    },

    // 创建日志记录
    async createLog(logData) {
      try {
        const response = await logAPI.createLog(logData)
        return response
      } catch (error) {
        console.error('创建日志失败:', error)
        throw error
      }
    },

    // 批量删除日志
    async batchDeleteLogs(logIds) {
      try {
        const response = await logAPI.batchDeleteLogs(logIds)
        // 删除成功后刷新列表
        await this.getLogList(this.searchParams)
        return response
      } catch (error) {
        console.error('批量删除日志失败:', error)
        throw error
      }
    },

    // 清空日志
    async clearLogs(beforeDate = null) {
      try {
        const response = await logAPI.clearLogs(beforeDate)
        // 清空成功后刷新列表
        await this.getLogList(this.searchParams)
        return response
      } catch (error) {
        console.error('清空日志失败:', error)
        throw error
      }
    },

    // 导出日志
    async exportLogs(params = {}) {
      try {
        const response = await logAPI.exportLogs(params)
        
        // 处理文件下载
        if (response.data instanceof Blob) {
          const url = window.URL.createObjectURL(response.data)
          const link = document.createElement('a')
          link.href = url
          
          // 生成文件名
          const date = new Date().toISOString().slice(0, 10)
          link.download = `operation_logs_${date}.xlsx`
          
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        return response
      } catch (error) {
        console.error('导出日志失败:', error)
        throw error
      }
    },

    // 获取日志统计信息
    async getLogStats() {
      try {
        const response = await logAPI.getLogStats()
        this.logStats = response.data
        return response
      } catch (error) {
        console.error('获取日志统计失败:', error)
        throw error
      }
    },

    // 获取用户操作统计
    async getUserActionStats(timeRange = 'week') {
      try {
        const response = await logAPI.getUserActionStats(timeRange)
        return response
      } catch (error) {
        console.error('获取用户操作统计失败:', error)
        throw error
      }
    },

    // 获取系统访问统计
    async getSystemAccessStats(timeRange = 'week') {
      try {
        const response = await logAPI.getSystemAccessStats(timeRange)
        return response
      } catch (error) {
        console.error('获取系统访问统计失败:', error)
        throw error
      }
    },

    // 获取错误日志统计
    async getErrorLogStats(timeRange = 'week') {
      try {
        const response = await logAPI.getErrorLogStats(timeRange)
        return response
      } catch (error) {
        console.error('获取错误日志统计失败:', error)
        throw error
      }
    },

    // 搜索日志
    async searchLogs(searchParams) {
      return await this.getLogList(searchParams)
    },

    // 记录用户操作
    async logUserAction(actionData) {
      try {
        const logData = {
          username: actionData.username,
          action: actionData.action,
          resource: actionData.resource,
          description: actionData.description,
          ipAddress: actionData.ipAddress,
          userAgent: actionData.userAgent,
          method: actionData.method || 'GET',
          path: actionData.path || '',
          requestData: actionData.requestData ? JSON.stringify(actionData.requestData) : null,
          responseData: actionData.responseData ? JSON.stringify(actionData.responseData) : null,
          status: actionData.status || 'success',
          responseTime: actionData.responseTime || 0,
          errorMessage: actionData.errorMessage || null
        }
        
        return await this.createLog(logData)
      } catch (error) {
        console.error('记录用户操作失败:', error)
        // 日志记录失败不应该影响正常业务流程
      }
    },

    // 记录系统事件
    async logSystemEvent(eventData) {
      try {
        const logData = {
          username: 'system',
          action: eventData.action,
          resource: eventData.resource || 'system',
          description: eventData.description,
          status: eventData.status || 'success',
          errorMessage: eventData.errorMessage || null
        }
        
        return await this.createLog(logData)
      } catch (error) {
        console.error('记录系统事件失败:', error)
      }
    },

    // 重置状态
    resetState() {
      this.logList = []
      this.currentLog = null
      this.pagination = {
        page: 1,
        size: 20,
        total: 0
      }
      this.loading = false
      this.searchParams = {}
      this.logStats = {
        todayCount: 0,
        weekCount: 0,
        monthCount: 0,
        totalCount: 0
      }
    },

    // 设置当前日志
    setCurrentLog(log) {
      this.currentLog = log
    },

    // 刷新当前列表
    async refresh() {
      return await this.getLogList(this.searchParams)
    },

    // 实时添加新日志（用于实时更新）
    addNewLog(log) {
      this.logList.unshift(log)
      this.pagination.total += 1
      
      // 保持列表大小不超过当前页大小
      if (this.logList.length > this.pagination.size) {
        this.logList.pop()
      }
    },

    // 格式化日志信息用于显示
    formatLogForDisplay(log) {
      return {
        ...log,
        actionText: this.getActionText(log.action),
        statusText: log.status === 'success' ? '成功' : '失败',
        formattedTime: new Date(log.createdAt).toLocaleString('zh-CN')
      }
    },

    // 获取操作类型文本
    getActionText(action) {
      const actionMap = {
        login: '登录',
        logout: '登出',
        create: '创建',
        update: '更新',
        delete: '删除',
        query: '查询',
        encrypt: '加密',
        decrypt: '解密',
        upload: '上传',
        download: '下载',
        export: '导出',
        import: '导入'
      }
      return actionMap[action] || action
    }
  }
})
