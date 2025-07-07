import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useLogStore = defineStore('log', () => {
  // 状态
  const logs = ref([])
  const loading = ref(false)
  const pagination = ref({
    current: 1,
    pageSize: 20,
    total: 0
  })
  const filters = ref({
    level: '',
    module: '',
    startTime: '',
    endTime: '',
    keyword: ''
  })

  // 计算属性
  const filteredLogs = computed(() => {
    return logs.value.filter(log => {
      if (filters.value.level && log.level !== filters.value.level) return false
      if (filters.value.module && log.module !== filters.value.module) return false
      if (filters.value.keyword && !log.message.includes(filters.value.keyword)) return false
      return true
    })
  })

  const logLevels = computed(() => {
    const levels = [...new Set(logs.value.map(log => log.level))]
    return levels.sort()
  })

  const logModules = computed(() => {
    const modules = [...new Set(logs.value.map(log => log.module))]
    return modules.sort()
  })

  // 操作
  const fetchLogs = async (params = {}) => {
    loading.value = true
    try {
      const response = await api.get('/admin/logs', {
        params: {
          page: pagination.value.current,
          size: pagination.value.pageSize,
          ...filters.value,
          ...params
        }
      })
      logs.value = response.data.data || []
      pagination.value.total = response.data.total || 0
    } catch (error) {
      console.error('获取日志失败:', error)
      logs.value = []
    } finally {
      loading.value = false
    }
  }

  const clearLogs = async () => {
    try {
      await api.delete('/admin/logs')
      await fetchLogs()
    } catch (error) {
      console.error('清空日志失败:', error)
      throw error
    }
  }

  const exportLogs = async () => {
    try {
      const response = await api.get('/admin/logs/export', {
        params: filters.value,
        responseType: 'blob'
      })
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `logs_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('导出日志失败:', error)
      throw error
    }
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const setPagination = (newPagination) => {
    pagination.value = { ...pagination.value, ...newPagination }
  }

  const resetFilters = () => {
    filters.value = {
      level: '',
      module: '',
      startTime: '',
      endTime: '',
      keyword: ''
    }
  }

  // 初始化
  const init = async () => {
    await fetchLogs()
  }

  return {
    // 状态
    logs,
    loading,
    pagination,
    filters,
    
    // 计算属性
    filteredLogs,
    logLevels,
    logModules,
    
    // 操作
    fetchLogs,
    clearLogs,
    exportLogs,
    setFilters,
    setPagination,
    resetFilters,
    init
  }
})
