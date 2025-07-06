/**
 * 分片管理API
 */
import { api } from './index'

export const shardAPI = {
  // 获取分片列表
  getShards: (params = {}) => {
    return api.get('/shards', params)
  },

  // 获取分片详情
  getShardById: (id) => {
    return api.get(`/shards/${id}`)
  },

  // 验证分片完整性
  verifyShardIntegrity: (id) => {
    return api.post(`/shards/${id}/verify`)
  },

  // 重构数据
  reconstructData: (reconstructionData) => {
    return api.post('/shards/reconstruct', reconstructionData)
  },

  // 获取存储节点列表
  getStorageNodes: (params = {}) => {
    return api.get('/storage-nodes', params)
  },

  // 添加存储节点
  addStorageNode: (nodeData) => {
    return api.post('/storage-nodes', nodeData)
  },

  // 更新存储节点
  updateStorageNode: (id, nodeData) => {
    return api.put(`/storage-nodes/${id}`, nodeData)
  },

  // 删除存储节点
  deleteStorageNode: (id) => {
    return api.delete(`/storage-nodes/${id}`)
  },

  // 检查节点健康状态
  checkNodeHealth: (id) => {
    return api.post(`/storage-nodes/${id}/health-check`)
  },

  // 获取节点统计信息
  getNodeStats: (id) => {
    return api.get(`/storage-nodes/${id}/stats`)
  },

  // 获取分片分布统计
  getShardDistribution: () => {
    return api.get('/shards/distribution')
  },

  // 迁移分片
  migrateShard: (shardId, targetNodeId) => {
    return api.post(`/shards/${shardId}/migrate`, {
      target_node_id: targetNodeId
    })
  },

  // 备份分片
  backupShard: (shardId) => {
    return api.post(`/shards/${shardId}/backup`)
  },

  // 恢复分片
  restoreShard: (shardId, backupData) => {
    return api.post(`/shards/${shardId}/restore`, backupData)
  },

  // 获取分片访问日志
  getShardAccessLogs: (shardId, params = {}) => {
    return api.get(`/shards/${shardId}/access-logs`, params)
  }
}
