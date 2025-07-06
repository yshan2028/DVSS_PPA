import { defineStore } from 'pinia'
import { fieldApi } from '@/api/field'

export const useFieldStore = defineStore('field', {
  state: () => ({
    // 字段列表
    fields: [],
    // 当前字段
    currentField: null,
    // 加载状态
    loading: false,
    // 分页信息
    pagination: {
      page: 1,
      page_size: 20,
      total: 0
    },
    // 搜索条件
    searchFilters: {
      field_name: '',
      field_type: '',
      sensitivity_level: '',
      is_active: null
    },
    // 字段使用统计
    fieldUsageStats: {}
  }),

  getters: {
    // 获取活跃字段
    activeFields: (state) => {
      return state.fields.filter(field => field.is_active)
    },

    // 获取可搜索字段
    searchableFields: (state) => {
      return state.activeFields.filter(field => field.is_searchable)
    },

    // 获取字段选项（用于下拉框）
    fieldOptions: (state) => {
      return state.activeFields.map(field => ({
        label: field.field_name,
        value: field.id,
        type: field.field_type,
        sensitivity: field.sensitivity_level
      }))
    },

    // 按类型分组的字段
    fieldsByType: (state) => {
      const grouped = {}
      state.fields.forEach(field => {
        if (!grouped[field.field_type]) {
          grouped[field.field_type] = []
        }
        grouped[field.field_type].push(field)
      })
      return grouped
    },

    // 按敏感度分组的字段
    fieldsBySensitivity: (state) => {
      const grouped = {}
      state.fields.forEach(field => {
        if (!grouped[field.sensitivity_level]) {
          grouped[field.sensitivity_level] = []
        }
        grouped[field.sensitivity_level].push(field)
      })
      return grouped
    },

    // 根据ID获取字段
    getFieldById: (state) => {
      return (id) => state.fields.find(field => field.id === id)
    },

    // 获取高敏感度字段
    highSensitivityFields: (state) => {
      return state.fields.filter(field => 
        field.sensitivity_level === 'high' || field.sensitivity_level === 'critical'
      )
    },

    // 获取必填字段
    requiredFields: (state) => {
      return state.fields.filter(field => field.is_required)
    }
  },

  actions: {
    // 加载字段列表
    async fetchFields(params = {}) {
      this.loading = true
      try {
        const queryParams = {
          page: this.pagination.page,
          page_size: this.pagination.page_size,
          ...this.searchFilters,
          ...params
        }

        // 过滤空值
        Object.keys(queryParams).forEach(key => {
          if (queryParams[key] === null || queryParams[key] === '') {
            delete queryParams[key]
          }
        })

        const response = await fieldApi.getFieldList(queryParams)
        if (response.code === 200) {
          this.fields = response.data.items || []
          this.pagination.total = response.data.total || 0
          return response.data
        }
        throw new Error(response.message || '获取字段列表失败')
      } catch (error) {
        console.error('获取字段列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建字段
    async createField(fieldData) {
      try {
        const response = await fieldApi.createField(fieldData)
        if (response.code === 200) {
          // 重新加载字段列表
          await this.fetchFields()
          return response.data
        }
        throw new Error(response.message || '创建字段失败')
      } catch (error) {
        console.error('创建字段失败:', error)
        throw error
      }
    },

    // 更新字段
    async updateField(fieldId, fieldData) {
      try {
        const response = await fieldApi.updateField(fieldId, fieldData)
        if (response.code === 200) {
          // 更新本地字段数据
          const index = this.fields.findIndex(field => field.id === fieldId)
          if (index !== -1) {
            this.fields[index] = { ...this.fields[index], ...fieldData }
          }
          return response.data
        }
        throw new Error(response.message || '更新字段失败')
      } catch (error) {
        console.error('更新字段失败:', error)
        throw error
      }
    },

    // 删除字段
    async deleteField(fieldId) {
      try {
        const response = await fieldApi.deleteField(fieldId)
        if (response.code === 200) {
          // 从本地列表中移除
          this.fields = this.fields.filter(field => field.id !== fieldId)
          this.pagination.total = Math.max(0, this.pagination.total - 1)
          return response.data
        }
        throw new Error(response.message || '删除字段失败')
      } catch (error) {
        console.error('删除字段失败:', error)
        throw error
      }
    },

    // 获取字段详情
    async fetchFieldDetail(fieldId) {
      try {
        const response = await fieldApi.getFieldDetail(fieldId)
        if (response.code === 200) {
          this.currentField = response.data
          return response.data
        }
        throw new Error(response.message || '获取字段详情失败')
      } catch (error) {
        console.error('获取字段详情失败:', error)
        throw error
      }
    },

    // 获取字段使用情况
    async fetchFieldUsage(fieldId) {
      try {
        const response = await fieldApi.getFieldUsage(fieldId)
        if (response.code === 200) {
          this.fieldUsageStats[fieldId] = response.data
          return response.data
        }
        throw new Error(response.message || '获取字段使用情况失败')
      } catch (error) {
        console.error('获取字段使用情况失败:', error)
        throw error
      }
    },

    // 批量更新字段
    async batchUpdateFields(fieldIds, updateData) {
      try {
        const response = await fieldApi.batchUpdateFields({ 
          field_ids: fieldIds, 
          update_data: updateData 
        })
        if (response.code === 200) {
          // 更新本地数据
          fieldIds.forEach(fieldId => {
            const index = this.fields.findIndex(field => field.id === fieldId)
            if (index !== -1) {
              this.fields[index] = { ...this.fields[index], ...updateData }
            }
          })
          return response.data
        }
        throw new Error(response.message || '批量更新字段失败')
      } catch (error) {
        console.error('批量更新字段失败:', error)
        throw error
      }
    },

    // 验证字段配置
    async validateFieldConfig(fieldConfig) {
      try {
        const response = await fieldApi.validateFieldConfig(fieldConfig)
        if (response.code === 200) {
          return response.data
        }
        throw new Error(response.message || '字段配置验证失败')
      } catch (error) {
        console.error('字段配置验证失败:', error)
        throw error
      }
    },

    // 设置搜索条件
    setSearchFilters(filters) {
      this.searchFilters = { ...this.searchFilters, ...filters }
    },

    // 重置搜索条件
    resetSearchFilters() {
      this.searchFilters = {
        field_name: '',
        field_type: '',
        sensitivity_level: '',
        is_active: null
      }
    },

    // 设置分页
    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 清空字段数据
    clearFields() {
      this.fields = []
      this.currentField = null
      this.fieldUsageStats = {}
      this.pagination = {
        page: 1,
        page_size: 20,
        total: 0
      }
    },

    // 切换字段状态
    async toggleFieldStatus(fieldId) {
      const field = this.fields.find(f => f.id === fieldId)
      if (!field) {
        throw new Error('字段不存在')
      }

      try {
        const response = await fieldApi.updateField(fieldId, {
          is_active: !field.is_active
        })
        if (response.code === 200) {
          field.is_active = !field.is_active
          return response.data
        }
        throw new Error(response.message || '切换字段状态失败')
      } catch (error) {
        console.error('切换字段状态失败:', error)
        throw error
      }
    },

    // 复制字段配置
    async duplicateField(fieldId, newFieldName) {
      const field = this.getFieldById(fieldId)
      if (!field) {
        throw new Error('字段不存在')
      }

      const duplicateData = {
        ...field,
        field_name: newFieldName,
        id: undefined, // 移除ID让后端生成新的
        created_at: undefined,
        updated_at: undefined
      }

      return await this.createField(duplicateData)
    },

    // 获取字段统计信息
    getFieldStatistics() {
      const stats = {
        total: this.fields.length,
        active: this.activeFields.length,
        byType: {},
        bySensitivity: {},
        searchable: this.searchableFields.length,
        required: this.requiredFields.length
      }

      // 按类型统计
      this.fields.forEach(field => {
        stats.byType[field.field_type] = (stats.byType[field.field_type] || 0) + 1
      })

      // 按敏感度统计
      this.fields.forEach(field => {
        stats.bySensitivity[field.sensitivity_level] = (stats.bySensitivity[field.sensitivity_level] || 0) + 1
      })

      return stats
    },

    // 检查字段名是否已存在
    isFieldNameExists(fieldName, excludeId = null) {
      return this.fields.some(field => 
        field.field_name === fieldName && field.id !== excludeId
      )
    },

    // 获取推荐的加密算法
    getRecommendedEncryption(sensitivityLevel) {
      const recommendations = {
        'low': 'AES256',
        'medium': 'AES256',
        'high': 'RSA2048',
        'critical': 'ChaCha20'
      }
      return recommendations[sensitivityLevel] || 'AES256'
    }
  }
})
