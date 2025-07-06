import { defineStore } from 'pinia'
import { fabricAPI } from '@/api/fabric'

export const useFabricStore = defineStore('fabric', {
  state: () => ({
    networkStatus: {
      status: 'unknown',
      peerCount: 0,
      blockHeight: 0,
      transactionCount: 0
    },
    peerList: [],
    chaincodeList: [],
    blockList: [],
    currentBlock: null,
    channelList: [],
    loading: false,
    connectionStatus: false
  }),

  getters: {
    // 网络是否在线
    isNetworkOnline: (state) => state.networkStatus.status === 'active',
    
    // 获取在线节点数量
    onlinePeerCount: (state) => {
      return state.peerList.filter(peer => peer.status === 'online').length
    },
    
    // 获取离线节点数量
    offlinePeerCount: (state) => {
      return state.peerList.filter(peer => peer.status === 'offline').length
    },
    
    // 获取已实例化的链码数量
    instantiatedChaincodeCount: (state) => {
      return state.chaincodeList.filter(cc => cc.status === 'instantiated').length
    },
    
    // 获取错误状态的链码数量
    errorChaincodeCount: (state) => {
      return state.chaincodeList.filter(cc => cc.status === 'error').length
    },
    
    // 获取最新区块
    latestBlock: (state) => {
      return state.blockList.length > 0 ? state.blockList[0] : null
    }
  },

  actions: {
    // 获取网络状态
    async getNetworkStatus() {
      try {
        const response = await fabricAPI.getNetworkStatus()
        this.networkStatus = response.data
        this.connectionStatus = response.data.status === 'active'
        return response
      } catch (error) {
        console.error('获取网络状态失败:', error)
        this.connectionStatus = false
        throw error
      }
    },

    // 获取节点列表
    async getPeerList() {
      try {
        const response = await fabricAPI.getPeerList()
        this.peerList = response.data || []
        return response
      } catch (error) {
        console.error('获取节点列表失败:', error)
        throw error
      }
    },

    // 获取节点详情
    async getPeerDetail(peerName) {
      try {
        const response = await fabricAPI.getPeerDetail(peerName)
        return response
      } catch (error) {
        console.error('获取节点详情失败:', error)
        throw error
      }
    },

    // 重启节点
    async restartPeer(peerName) {
      try {
        const response = await fabricAPI.restartPeer(peerName)
        // 重启后刷新节点列表
        await this.getPeerList()
        return response
      } catch (error) {
        console.error('重启节点失败:', error)
        throw error
      }
    },

    // 移除节点
    async removePeer(peerName) {
      try {
        const response = await fabricAPI.removePeer(peerName)
        // 移除后刷新节点列表
        await this.getPeerList()
        return response
      } catch (error) {
        console.error('移除节点失败:', error)
        throw error
      }
    },

    // 添加节点
    async addPeer(peerConfig) {
      try {
        const response = await fabricAPI.addPeer(peerConfig)
        // 添加后刷新节点列表
        await this.getPeerList()
        return response
      } catch (error) {
        console.error('添加节点失败:', error)
        throw error
      }
    },

    // 获取链码列表
    async getChaincodeList() {
      try {
        const response = await fabricAPI.getChaincodeList()
        this.chaincodeList = response.data || []
        return response
      } catch (error) {
        console.error('获取链码列表失败:', error)
        throw error
      }
    },

    // 部署链码
    async deployChaincode(chaincodeData) {
      try {
        const response = await fabricAPI.deployChaincode(chaincodeData)
        // 部署后刷新链码列表
        await this.getChaincodeList()
        return response
      } catch (error) {
        console.error('部署链码失败:', error)
        throw error
      }
    },

    // 调用链码
    async invokeChaincode(chaincodeName, functionName, args = []) {
      try {
        const response = await fabricAPI.invokeChaincode(chaincodeName, functionName, args)
        return response
      } catch (error) {
        console.error('调用链码失败:', error)
        throw error
      }
    },

    // 查询链码
    async queryChaincode(chaincodeName, functionName, args = []) {
      try {
        const response = await fabricAPI.queryChaincode(chaincodeName, functionName, args)
        return response
      } catch (error) {
        console.error('查询链码失败:', error)
        throw error
      }
    },

    // 升级链码
    async upgradeChaincode(chaincodeName, newVersion, upgradeData) {
      try {
        const response = await fabricAPI.upgradeChaincode(chaincodeName, newVersion, upgradeData)
        // 升级后刷新链码列表
        await this.getChaincodeList()
        return response
      } catch (error) {
        console.error('升级链码失败:', error)
        throw error
      }
    },

    // 卸载链码
    async uninstallChaincode(chaincodeName) {
      try {
        const response = await fabricAPI.uninstallChaincode(chaincodeName)
        // 卸载后刷新链码列表
        await this.getChaincodeList()
        return response
      } catch (error) {
        console.error('卸载链码失败:', error)
        throw error
      }
    },

    // 获取区块列表
    async getBlockList(params = {}) {
      this.loading = true
      try {
        const response = await fabricAPI.getBlockList(params)
        this.blockList = response.data.items || []
        return response
      } catch (error) {
        console.error('获取区块列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取区块详情
    async getBlockDetail(blockNumber) {
      try {
        const response = await fabricAPI.getBlockDetail(blockNumber)
        this.currentBlock = response.data
        return response
      } catch (error) {
        console.error('获取区块详情失败:', error)
        throw error
      }
    },

    // 根据哈希搜索区块
    async searchBlock(hash) {
      try {
        const response = await fabricAPI.searchBlock(hash)
        return response
      } catch (error) {
        console.error('搜索区块失败:', error)
        throw error
      }
    },

    // 获取交易详情
    async getTransactionDetail(txId) {
      try {
        const response = await fabricAPI.getTransactionDetail(txId)
        return response
      } catch (error) {
        console.error('获取交易详情失败:', error)
        throw error
      }
    },

    // 获取通道列表
    async getChannelList() {
      try {
        const response = await fabricAPI.getChannelList()
        this.channelList = response.data || []
        return response
      } catch (error) {
        console.error('获取通道列表失败:', error)
        throw error
      }
    },

    // 创建通道
    async createChannel(channelConfig) {
      try {
        const response = await fabricAPI.createChannel(channelConfig)
        // 创建后刷新通道列表
        await this.getChannelList()
        return response
      } catch (error) {
        console.error('创建通道失败:', error)
        throw error
      }
    },

    // 加入通道
    async joinChannel(channelName, peerName) {
      try {
        const response = await fabricAPI.joinChannel(channelName, peerName)
        return response
      } catch (error) {
        console.error('加入通道失败:', error)
        throw error
      }
    },

    // 获取通道信息
    async getChannelInfo(channelName) {
      try {
        const response = await fabricAPI.getChannelInfo(channelName)
        return response
      } catch (error) {
        console.error('获取通道信息失败:', error)
        throw error
      }
    },

    // 重启网络
    async restartNetwork() {
      try {
        const response = await fabricAPI.restartNetwork()
        // 重启后重新获取状态
        setTimeout(() => {
          this.getNetworkStatus()
        }, 5000)
        return response
      } catch (error) {
        console.error('重启网络失败:', error)
        throw error
      }
    },

    // 停止网络
    async stopNetwork() {
      try {
        const response = await fabricAPI.stopNetwork()
        this.connectionStatus = false
        return response
      } catch (error) {
        console.error('停止网络失败:', error)
        throw error
      }
    },

    // 启动网络
    async startNetwork() {
      try {
        const response = await fabricAPI.startNetwork()
        // 启动后重新获取状态
        setTimeout(() => {
          this.getNetworkStatus()
        }, 3000)
        return response
      } catch (error) {
        console.error('启动网络失败:', error)
        throw error
      }
    },

    // 获取网络配置
    async getNetworkConfig() {
      try {
        const response = await fabricAPI.getNetworkConfig()
        return response
      } catch (error) {
        console.error('获取网络配置失败:', error)
        throw error
      }
    },

    // 更新网络配置
    async updateNetworkConfig(config) {
      try {
        const response = await fabricAPI.updateNetworkConfig(config)
        return response
      } catch (error) {
        console.error('更新网络配置失败:', error)
        throw error
      }
    },

    // 获取证书信息
    async getCertificateInfo() {
      try {
        const response = await fabricAPI.getCertificateInfo()
        return response
      } catch (error) {
        console.error('获取证书信息失败:', error)
        throw error
      }
    },

    // 更新证书
    async updateCertificate(certificateData) {
      try {
        const response = await fabricAPI.updateCertificate(certificateData)
        return response
      } catch (error) {
        console.error('更新证书失败:', error)
        throw error
      }
    },

    // 备份区块链数据
    async backupBlockchainData() {
      try {
        const response = await fabricAPI.backupBlockchainData()
        
        // 处理文件下载
        if (response.data instanceof Blob) {
          const url = window.URL.createObjectURL(response.data)
          const link = document.createElement('a')
          link.href = url
          
          const date = new Date().toISOString().slice(0, 10)
          link.download = `blockchain_backup_${date}.tar.gz`
          
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        }
        
        return response
      } catch (error) {
        console.error('备份区块链数据失败:', error)
        throw error
      }
    },

    // 恢复区块链数据
    async restoreBlockchainData(backupFile) {
      try {
        const formData = new FormData()
        formData.append('backup', backupFile)
        
        const response = await fabricAPI.restoreBlockchainData(formData)
        return response
      } catch (error) {
        console.error('恢复区块链数据失败:', error)
        throw error
      }
    },

    // 重置状态
    resetState() {
      this.networkStatus = {
        status: 'unknown',
        peerCount: 0,
        blockHeight: 0,
        transactionCount: 0
      }
      this.peerList = []
      this.chaincodeList = []
      this.blockList = []
      this.currentBlock = null
      this.channelList = []
      this.loading = false
      this.connectionStatus = false
    },

    // 刷新所有数据
    async refreshAll() {
      try {
        await Promise.all([
          this.getNetworkStatus(),
          this.getPeerList(),
          this.getChaincodeList(),
          this.getChannelList()
        ])
      } catch (error) {
        console.error('刷新数据失败:', error)
        throw error
      }
    },

    // 设置当前区块
    setCurrentBlock(block) {
      this.currentBlock = block
    },

    // 更新节点状态
    updatePeerStatus(peerName, status) {
      const peer = this.peerList.find(p => p.name === peerName)
      if (peer) {
        peer.status = status
      }
    },

    // 更新链码状态
    updateChaincodeStatus(chaincodeName, status) {
      const chaincode = this.chaincodeList.find(cc => cc.name === chaincodeName)
      if (chaincode) {
        chaincode.status = status
      }
    }
  }
})
