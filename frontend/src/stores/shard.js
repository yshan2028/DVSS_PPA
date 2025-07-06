import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useShardStore = defineStore('shard', () => {
  // 分片列表
  const shards = ref([])
  
  // 加载状态
  const loading = ref(false)
  
  // 错误信息
  const error = ref(null)
  
  // 获取分片列表
  const fetchShards = async () => {
    loading.value = true
    error.value = null
    
    try {
      // TODO: 实现API调用
      // const response = await api.getShards()
      // shards.value = response.data
      
      // 模拟数据
      await new Promise(resolve => setTimeout(resolve, 1000))
      shards.value = [
        {
          id: 1,
          name: 'Shard 1',
          secret: '******',
          threshold: 3,
          total: 5,
          status: 'active',
          createdAt: '2024-01-01',
          updatedAt: '2024-01-01'
        },
        {
          id: 2,
          name: 'Shard 2',
          secret: '******',
          threshold: 2,
          total: 3,
          status: 'inactive',
          createdAt: '2024-01-02',
          updatedAt: '2024-01-02'
        }
      ]
    } catch (err) {
      error.value = err.message || '获取分片列表失败'
      console.error('Failed to fetch shards:', err)
    } finally {
      loading.value = false
    }
  }
  
  // 创建分片
  const createShard = async (shardData) => {
    loading.value = true
    error.value = null
    
    try {
      // TODO: 实现API调用
      // const response = await api.createShard(shardData)
      // const newShard = response.data
      
      // 模拟创建
      const newShard = {
        id: Date.now(),
        ...shardData,
        status: 'active',
        createdAt: new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0]
      }
      
      shards.value.push(newShard)
      return newShard
    } catch (err) {
      error.value = err.message || '创建分片失败'
      console.error('Failed to create shard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 更新分片
  const updateShard = async (id, shardData) => {
    loading.value = true
    error.value = null
    
    try {
      // TODO: 实现API调用
      // const response = await api.updateShard(id, shardData)
      // const updatedShard = response.data
      
      // 模拟更新
      const index = shards.value.findIndex(shard => shard.id === id)
      if (index !== -1) {
        shards.value[index] = {
          ...shards.value[index],
          ...shardData,
          updatedAt: new Date().toISOString().split('T')[0]
        }
      }
    } catch (err) {
      error.value = err.message || '更新分片失败'
      console.error('Failed to update shard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 删除分片
  const deleteShard = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      // TODO: 实现API调用
      // await api.deleteShard(id)
      
      // 模拟删除
      const index = shards.value.findIndex(shard => shard.id === id)
      if (index !== -1) {
        shards.value.splice(index, 1)
      }
    } catch (err) {
      error.value = err.message || '删除分片失败'
      console.error('Failed to delete shard:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 重构分片
  const reconstructSecret = async (shardIds) => {
    loading.value = true
    error.value = null
    
    try {
      // TODO: 实现API调用
      // const response = await api.reconstructSecret(shardIds)
      // return response.data.secret
      
      // 模拟重构
      await new Promise(resolve => setTimeout(resolve, 2000))
      return 'reconstructed-secret-value'
    } catch (err) {
      error.value = err.message || '重构密钥失败'
      console.error('Failed to reconstruct secret:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    // 状态
    shards,
    loading,
    error,
    
    // 操作
    fetchShards,
    createShard,
    updateShard,
    deleteShard,
    reconstructSecret
  }
})
