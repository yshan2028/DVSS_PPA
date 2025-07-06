/**
 * 角色管理API
 */
import { api } from './index'

export const roleAPI = {
  // 获取角色列表
  getRoles: (params = {}) => {
    return api.get('/roles', params)
  },

  // 获取角色详情
  getRoleById: (id) => {
    return api.get(`/roles/${id}`)
  },

  // 创建角色
  createRole: (roleData) => {
    return api.post('/roles', roleData)
  },

  // 更新角色
  updateRole: (id, roleData) => {
    return api.put(`/roles/${id}`, roleData)
  },

  // 删除角色
  deleteRole: (id) => {
    return api.delete(`/roles/${id}`)
  },

  // 获取角色权限
  getRolePermissions: (id) => {
    return api.get(`/roles/${id}/permissions`)
  },

  // 设置角色权限
  setRolePermissions: (id, permissions) => {
    return api.post(`/roles/${id}/permissions`, { permissions })
  },

  // 获取所有可用权限
  getAvailablePermissions: () => {
    return api.get('/roles/permissions/available')
  },

  // 复制角色权限
  copyRolePermissions: (fromRoleId, toRoleId) => {
    return api.post('/roles/copy-permissions', {
      from_role_id: fromRoleId,
      to_role_id: toRoleId
    })
  },

  // 获取角色用户列表
  getRoleUsers: (id) => {
    return api.get(`/roles/${id}/users`)
  },

  // 获取角色统计信息
  getRoleStats: () => {
    return api.get('/roles/stats')
  }
}
