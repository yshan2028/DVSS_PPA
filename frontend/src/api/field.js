/**
 * 字段管理API
 */
import { api } from './index'

export const fieldAPI = {
  // 获取字段列表
  getFields: (params = {}) => {
    return api.get('/fields', params)
  },

  // 获取字段详情
  getFieldById: (id) => {
    return api.get(`/fields/${id}`)
  },

  // 创建字段
  createField: (fieldData) => {
    return api.post('/fields', fieldData)
  },

  // 更新字段
  updateField: (id, fieldData) => {
    return api.put(`/fields/${id}`, fieldData)
  },

  // 删除字段
  deleteField: (id) => {
    return api.delete(`/fields/${id}`)
  },

  // 批量更新字段
  batchUpdateFields: (batchData) => {
    return api.post('/fields/batch-update', batchData)
  },

  // 获取敏感度分析
  getSensitivityAnalysis: () => {
    return api.get('/fields/analysis/sensitivity')
  },

  // 根据分类获取字段
  getFieldsByCategory: (category) => {
    return api.get(`/fields/category/${category}`)
  },

  // 获取所有激活字段
  getActiveFields: () => {
    return api.get('/fields/active/all')
  },

  // 获取角色字段权限
  getRoleFieldPermissions: (roleId) => {
    return api.get(`/fields/permissions/role/${roleId}`)
  },

  // 设置角色字段权限
  setRoleFieldPermissions: (roleId, permissions) => {
    return api.post(`/fields/permissions/role/${roleId}`, permissions)
  },

  // 导入字段配置
  importFields: (fileData) => {
    return api.upload('/fields/import', fileData)
  },

  // 导出字段配置
  exportFields: (params = {}) => {
    return api.get('/fields/export', params)
  },

  // 验证字段配置
  validateFieldConfig: (configData) => {
    return api.post('/fields/validate', configData)
  }
}
