import { defineStore } from 'pinia'
import { orderApi } from '@/api/order'

export const useOrderStore = defineStore('order', {
  state: () => ({
    // 订单列表
    orders: [],
    // 当前订单
    currentOrder: null,
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
      order_id: '',
      customer_name: '',
      status: '',
      is_encrypted: null,
      start_date: '',
      end_date: ''
    },
    // 统计数据
    statistics: {
      total: 0,
      encrypted: 0,
      pending: 0,
      completed: 0
    },
    // 选中的订单（用于批量操作）
    selectedOrders: []
  }),

  getters: {
    // 获取未加密订单
    unencryptedOrders: (state) => {
      return state.orders.filter(order => !order.is_encrypted)
    },

    // 获取已加密订单
    encryptedOrders: (state) => {
      return state.orders.filter(order => order.is_encrypted)
    },

    // 按状态分组的订单
    ordersByStatus: (state) => {
      const grouped = {}
      state.orders.forEach(order => {
        if (!grouped[order.status]) {
          grouped[order.status] = []
        }
        grouped[order.status].push(order)
      })
      return grouped
    },

    // 根据ID获取订单
    getOrderById: (state) => {
      return (id) => state.orders.find(order => order.id === id)
    },

    // 获取订单状态统计
    statusStatistics: (state) => {
      const stats = {
        pending: 0,
        processing: 0,
        completed: 0,
        cancelled: 0
      }
      state.orders.forEach(order => {
        if (stats[order.status] !== undefined) {
          stats[order.status]++
        }
      })
      return stats
    },

    // 获取选中订单的总金额
    selectedOrdersTotal: (state) => {
      return state.selectedOrders.reduce((total, order) => {
        return total + parseFloat(order.total_amount || 0)
      }, 0)
    },

    // 获取今日订单
    todayOrders: (state) => {
      const today = new Date().toDateString()
      return state.orders.filter(order => {
        const orderDate = new Date(order.created_at).toDateString()
        return orderDate === today
      })
    }
  },

  actions: {
    // 加载订单列表
    async fetchOrders(params = {}) {
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

        const response = await orderApi.getOrderList(queryParams)
        if (response.code === 200) {
          this.orders = response.data.items || []
          this.pagination.total = response.data.total || 0
          
          // 更新统计数据
          if (response.data.statistics) {
            this.statistics = response.data.statistics
          }
          
          return response.data
        }
        throw new Error(response.message || '获取订单列表失败')
      } catch (error) {
        console.error('获取订单列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建订单
    async createOrder(orderData) {
      try {
        const response = await orderApi.createOrder(orderData)
        if (response.code === 200) {
          // 重新加载订单列表
          await this.fetchOrders()
          return response.data
        }
        throw new Error(response.message || '创建订单失败')
      } catch (error) {
        console.error('创建订单失败:', error)
        throw error
      }
    },

    // 更新订单
    async updateOrder(orderId, orderData) {
      try {
        const response = await orderApi.updateOrder(orderId, orderData)
        if (response.code === 200) {
          // 更新本地订单数据
          const index = this.orders.findIndex(order => order.id === orderId)
          if (index !== -1) {
            this.orders[index] = { ...this.orders[index], ...orderData }
          }
          return response.data
        }
        throw new Error(response.message || '更新订单失败')
      } catch (error) {
        console.error('更新订单失败:', error)
        throw error
      }
    },

    // 删除订单
    async deleteOrder(orderId) {
      try {
        const response = await orderApi.deleteOrder(orderId)
        if (response.code === 200) {
          // 从本地列表中移除
          this.orders = this.orders.filter(order => order.id !== orderId)
          this.pagination.total = Math.max(0, this.pagination.total - 1)
          return response.data
        }
        throw new Error(response.message || '删除订单失败')
      } catch (error) {
        console.error('删除订单失败:', error)
        throw error
      }
    },

    // 获取订单详情
    async fetchOrderDetail(orderId) {
      try {
        const response = await orderApi.getOrderDetail(orderId)
        if (response.code === 200) {
          this.currentOrder = response.data
          return response.data
        }
        throw new Error(response.message || '获取订单详情失败')
      } catch (error) {
        console.error('获取订单详情失败:', error)
        throw error
      }
    },

    // 加密订单
    async encryptOrder(orderId) {
      try {
        const response = await orderApi.encryptOrder(orderId)
        if (response.code === 200) {
          // 更新本地订单状态
          const order = this.orders.find(o => o.id === orderId)
          if (order) {
            order.is_encrypted = true
            order.encrypted_at = new Date().toISOString()
          }
          return response.data
        }
        throw new Error(response.message || '订单加密失败')
      } catch (error) {
        console.error('订单加密失败:', error)
        throw error
      }
    },

    // 批量加密订单
    async batchEncryptOrders(orderIds) {
      try {
        const response = await orderApi.batchEncryptOrders({ order_ids: orderIds })
        if (response.code === 200) {
          // 更新本地订单状态
          orderIds.forEach(orderId => {
            const order = this.orders.find(o => o.id === orderId)
            if (order) {
              order.is_encrypted = true
              order.encrypted_at = new Date().toISOString()
            }
          })
          return response.data
        }
        throw new Error(response.message || '批量加密失败')
      } catch (error) {
        console.error('批量加密失败:', error)
        throw error
      }
    },

    // 解密订单
    async decryptOrder(orderId) {
      try {
        const response = await orderApi.decryptOrder(orderId)
        if (response.code === 200) {
          return response.data
        }
        throw new Error(response.message || '订单解密失败')
      } catch (error) {
        console.error('订单解密失败:', error)
        throw error
      }
    },

    // 查询数据
    async queryData(queryParams) {
      try {
        const response = await orderApi.queryData(queryParams)
        if (response.code === 200) {
          return response.data
        }
        throw new Error(response.message || '数据查询失败')
      } catch (error) {
        console.error('数据查询失败:', error)
        throw error
      }
    },

    // 获取统计数据
    async fetchStatistics() {
      try {
        const response = await orderApi.getStats()
        if (response.code === 200) {
          this.statistics = response.data
          return response.data
        }
        throw new Error(response.message || '获取统计数据失败')
      } catch (error) {
        console.error('获取统计数据失败:', error)
        throw error
      }
    },

    // 导出订单数据
    async exportOrders(params = {}) {
      try {
        const response = await orderApi.exportOrders(params)
        if (response.code === 200) {
          return response.data
        }
        throw new Error(response.message || '导出订单失败')
      } catch (error) {
        console.error('导出订单失败:', error)
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
        order_id: '',
        customer_name: '',
        status: '',
        is_encrypted: null,
        start_date: '',
        end_date: ''
      }
    },

    // 设置分页
    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 清空订单数据
    clearOrders() {
      this.orders = []
      this.currentOrder = null
      this.selectedOrders = []
      this.pagination = {
        page: 1,
        page_size: 20,
        total: 0
      }
    },

    // 设置选中订单
    setSelectedOrders(orders) {
      this.selectedOrders = orders
    },

    // 添加选中订单
    addSelectedOrder(order) {
      if (!this.selectedOrders.find(o => o.id === order.id)) {
        this.selectedOrders.push(order)
      }
    },

    // 移除选中订单
    removeSelectedOrder(orderId) {
      this.selectedOrders = this.selectedOrders.filter(order => order.id !== orderId)
    },

    // 清空选中订单
    clearSelectedOrders() {
      this.selectedOrders = []
    },

    // 更新订单状态
    async updateOrderStatus(orderId, status) {
      try {
        const response = await orderApi.updateOrder(orderId, { status })
        if (response.code === 200) {
          const order = this.orders.find(o => o.id === orderId)
          if (order) {
            order.status = status
            order.updated_at = new Date().toISOString()
          }
          return response.data
        }
        throw new Error(response.message || '更新订单状态失败')
      } catch (error) {
        console.error('更新订单状态失败:', error)
        throw error
      }
    },

    // 批量更新订单状态
    async batchUpdateOrderStatus(orderIds, status) {
      try {
        const promises = orderIds.map(id => this.updateOrderStatus(id, status))
        await Promise.all(promises)
        return true
      } catch (error) {
        console.error('批量更新订单状态失败:', error)
        throw error
      }
    },

    // 获取订单趋势数据
    async fetchOrderTrends(params = {}) {
      try {
        const response = await orderApi.getOrderTrends(params)
        if (response.code === 200) {
          return response.data
        }
        throw new Error(response.message || '获取订单趋势失败')
      } catch (error) {
        console.error('获取订单趋势失败:', error)
        throw error
      }
    },

    // 验证订单数据
    validateOrderData(orderData) {
      const errors = []

      if (!orderData.customer_name) {
        errors.push('客户姓名不能为空')
      }

      if (!orderData.customer_phone) {
        errors.push('客户电话不能为空')
      } else if (!/^1[3-9]\d{9}$/.test(orderData.customer_phone)) {
        errors.push('客户电话格式不正确')
      }

      if (orderData.customer_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(orderData.customer_email)) {
        errors.push('客户邮箱格式不正确')
      }

      if (!orderData.product_name) {
        errors.push('产品名称不能为空')
      }

      if (!orderData.quantity || orderData.quantity <= 0) {
        errors.push('数量必须大于0')
      }

      if (!orderData.unit_price || orderData.unit_price < 0) {
        errors.push('单价不能小于0')
      }

      return errors
    }
  }
})
