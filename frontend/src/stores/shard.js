import { defineStore } from 'pinia'
import { shardAPI } from '@/api/shard'

export const useShardStore = defineStore('shard', {
  state: () => ({
    shardList: [],
    currentShard: null,
    pagination: {
      page: 1,
      size: 20,
      total: 0
    },
    loading: false,
    searchParams: {}
  }),

  getters: {
    // 获取分片总数
    totalShards: (state) => state.pagination.total,
    
    // 获取当前页分片列表
    currentPageShards: (state) => state.shardList,
    
    // 根据状态过滤分片
    shardsByStatus: (state) => (status) => {
      return state.shardList.filter(shard => shard.status === status)
    },
    
    // 获取完成的分片数量
    completedShardsCount: (state) => {
      return state.shardList.filter(shard => shard.status === 'completed').length
    },
    
    // 获取处理中的分片数量
    processingShardsCount: (state) => {
      return state.shardList.filter(shard => shard.status === 'processing').length
    }
  },

  actions: {
    // 获取分片列表
    async getShardList(params = {}) {
      this.loading = true
      try {
        const response = await shardAPI.getShardList(params)
        this.shardList = response.data.items || []
        this.pagination = {
          page: response.data.page || 1,
          size: response.data.size || 20,
          total: response.data.total || 0
        }
        this.searchParams = params
        return response
      } catch (error) {
        console.error('获取分片列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取分片详情
    async getShardDetail(shardId) {
      try {
        const response = await shardAPI.getShardDetail(shardId)
        this.currentShard = response.data
        return response
      } catch (error) {
        console.error('获取分片详情失败:', error)
        throw error
      }
    },

    // 创建分片
    async createShard(shardData) {
      try {
        const response = await shardAPI.createShard(shardData)
        // 创建成功后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('创建分片失败:', error)
        throw error
      }
    },

    // 更新分片
    async updateShard(shardId, shardData) {
      try {
        const response = await shardAPI.updateShard(shardId, shardData)
        // 更新成功后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('更新分片失败:', error)
        throw error
      }
    },

    // 删除分片
    async deleteShard(shardId) {
      try {
        const response = await shardAPI.deleteShard(shardId)
        // 删除成功后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('删除分片失败:', error)
        throw error
      }
    },

    // 批量删除分片
    async batchDeleteShards(shardIds) {
      try {
        const response = await shardAPI.batchDeleteShards(shardIds)
        // 删除成功后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('批量删除分片失败:', error)
        throw error
      }
    },

    // 下载分片
    async downloadShard(shardId) {
      try {
        const response = await shardAPI.downloadShard(shardId)
        
        // 处理文件下载
        if (response.data instanceof Blob) {
          const url = window.URL.createObjectURL(response.data)
          const link = document.createElement('a')
          link.href = url
          link.download = `shard_${shardId}.zip`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        return response
      } catch (error) {
        console.error('下载分片失败:', error)
        throw error
      }
    },

    // 批量下载分片
    async batchDownloadShards(shardIds) {
      try {
        const response = await shardAPI.batchDownloadShards(shardIds)
        
        // 处理文件下载
        if (response.data instanceof Blob) {
          const url = window.URL.createObjectURL(response.data)
          const link = document.createElement('a')
          link.href = url
          link.download = `shards_batch.zip`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        return response
      } catch (error) {
        console.error('批量下载分片失败:', error)
        throw error
      }
    },

    // 验证分片
    async validateShard(shardId) {
      try {
        const response = await shardAPI.validateShard(shardId)
        // 验证成功后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('验证分片失败:', error)
        throw error
      }
    },

    // 重新处理分片
    async reprocessShard(shardId) {
      try {
        const response = await shardAPI.reprocessShard(shardId)
        // 重新处理后刷新列表
        await this.getShardList(this.searchParams)
        return response
      } catch (error) {
        console.error('重新处理分片失败:', error)
        throw error
      }
    },

    // 获取分片统计信息
    async getShardStats() {
      try {
        const response = await shardAPI.getShardStats()
        return response
      } catch (error) {
        console.error('获取分片统计失败:', error)
        throw error
      }
    },

    // 搜索分片
    async searchShards(searchParams) {
      return await this.getShardList(searchParams)
    },

    // 重置状态
    resetState() {
      this.shardList = []
      this.currentShard = null
      this.pagination = {
        page: 1,
        size: 20,
        total: 0
      }
      this.loading = false
      this.searchParams = {}
    },

    // 设置当前分片
    setCurrentShard(shard) {
      this.currentShard = shard
    },

    // 更新分片状态
    updateShardStatus(shardId, status) {
      const shard = this.shardList.find(s => s.id === shardId)
      if (shard) {
        shard.status = status
      }
      if (this.currentShard && this.currentShard.id === shardId) {
        this.currentShard.status = status
      }
    },

    // 刷新当前列表
    async refresh() {
      return await this.getShardList(this.searchParams)
    }
  }
})
