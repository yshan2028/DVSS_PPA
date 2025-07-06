import { defineStore } from 'pinia'
import { roleApi } from '@/api/role'

export const useRoleStore = defineStore('role', {
  state: () => ({
    // 角色列表
    roles: [],
    // 当前角色
    currentRole: null,
    // 权限树
    permissions: [],
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
      name: '',
      is_active: null
    }
  }),

  getters: {
    // 获取活跃角色
    activeRoles: (state) => {
      return state.roles.filter(role => role.is_active)
    },

    // 获取角色选项（用于下拉框）
    roleOptions: (state) => {
      return state.activeRoles.map(role => ({
        label: role.name,
        value: role.id,
        description: role.description
      }))
    },

    // 根据ID获取角色
    getRoleById: (state) => {
      return (id) => state.roles.find(role => role.id === id)
    },

    // 获取角色权限映射
    rolePermissionsMap: (state) => {
      const map = {}
      state.roles.forEach(role => {
        map[role.id] = role.permissions || []
      })
      return map
    }
  },

  actions: {
    // 加载角色列表
    async fetchRoles(params = {}) {
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

        const response = await roleApi.getRoleList(queryParams)
        if (response.code === 200) {
          this.roles = response.data.items || []
          this.pagination.total = response.data.total || 0
          return response.data
        }
        throw new Error(response.message || '获取角色列表失败')
      } catch (error) {
        console.error('获取角色列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建角色
    async createRole(roleData) {
      try {
        const response = await roleApi.createRole(roleData)
        if (response.code === 200) {
          // 重新加载角色列表
          await this.fetchRoles()
          return response.data
        }
        throw new Error(response.message || '创建角色失败')
      } catch (error) {
        console.error('创建角色失败:', error)
        throw error
      }
    },

    // 更新角色
    async updateRole(roleId, roleData) {
      try {
        const response = await roleApi.updateRole(roleId, roleData)
        if (response.code === 200) {
          // 更新本地角色数据
          const index = this.roles.findIndex(role => role.id === roleId)
          if (index !== -1) {
            this.roles[index] = { ...this.roles[index], ...roleData }
          }
          return response.data
        }
        throw new Error(response.message || '更新角色失败')
      } catch (error) {
        console.error('更新角色失败:', error)
        throw error
      }
    },

    // 删除角色
    async deleteRole(roleId) {
      try {
        const response = await roleApi.deleteRole(roleId)
        if (response.code === 200) {
          // 从本地列表中移除
          this.roles = this.roles.filter(role => role.id !== roleId)
          this.pagination.total = Math.max(0, this.pagination.total - 1)
          return response.data
        }
        throw new Error(response.message || '删除角色失败')
      } catch (error) {
        console.error('删除角色失败:', error)
        throw error
      }
    },

    // 获取角色详情
    async fetchRoleDetail(roleId) {
      try {
        const response = await roleApi.getRoleDetail(roleId)
        if (response.code === 200) {
          this.currentRole = response.data
          return response.data
        }
        throw new Error(response.message || '获取角色详情失败')
      } catch (error) {
        console.error('获取角色详情失败:', error)
        throw error
      }
    },

    // 获取角色权限
    async fetchRolePermissions(roleId) {
      try {
        const response = await roleApi.getRolePermissions(roleId)
        if (response.code === 200) {
          return response.data || []
        }
        throw new Error(response.message || '获取角色权限失败')
      } catch (error) {
        console.error('获取角色权限失败:', error)
        throw error
      }
    },

    // 更新角色权限
    async updateRolePermissions(roleId, permissions) {
      try {
        const response = await roleApi.updateRolePermissions(roleId, { permissions })
        if (response.code === 200) {
          // 更新本地角色权限
          const role = this.roles.find(r => r.id === roleId)
          if (role) {
            role.permissions = permissions
          }
          return response.data
        }
        throw new Error(response.message || '更新角色权限失败')
      } catch (error) {
        console.error('更新角色权限失败:', error)
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
        name: '',
        is_active: null
      }
    },

    // 设置分页
    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 清空角色数据
    clearRoles() {
      this.roles = []
      this.currentRole = null
      this.pagination = {
        page: 1,
        page_size: 20,
        total: 0
      }
    },

    // 切换角色状态
    async toggleRoleStatus(roleId) {
      const role = this.roles.find(r => r.id === roleId)
      if (!role) {
        throw new Error('角色不存在')
      }

      try {
        const response = await roleApi.updateRole(roleId, {
          is_active: !role.is_active
        })
        if (response.code === 200) {
          role.is_active = !role.is_active
          return response.data
        }
        throw new Error(response.message || '切换角色状态失败')
      } catch (error) {
        console.error('切换角色状态失败:', error)
        throw error
      }
    },

    // 批量操作
    async batchUpdateRoles(roleIds, updateData) {
      try {
        const promises = roleIds.map(id => this.updateRole(id, updateData))
        await Promise.all(promises)
        return true
      } catch (error) {
        console.error('批量更新角色失败:', error)
        throw error
      }
    },

    // 检查角色权限
    hasRolePermission(roleId, permission) {
      const role = this.getRoleById(roleId)
      if (!role || !role.permissions) {
        return false
      }
      return role.permissions.includes(permission)
    },

    // 获取用户角色权限
    getUserPermissions(userRoles) {
      const permissions = new Set()
      userRoles.forEach(roleId => {
        const role = this.getRoleById(roleId)
        if (role && role.permissions) {
          role.permissions.forEach(permission => {
            permissions.add(permission)
          })
        }
      })
      return Array.from(permissions)
    }
  }
})
