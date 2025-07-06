<template>
  <div class="blockchain-container">
    <div class="page-header">
      <h1>区块链管理</h1>
      <p>区块链网络状态和交易管理</p>
    </div>

    <div class="blockchain-grid">
      <!-- 网络状态 -->
      <div class="card">
        <div class="card-header">
          <h3>网络状态</h3>
          <div class="status-indicator" :class="networkStatus.class">
            {{ networkStatus.text }}
          </div>
        </div>
        <div class="card-content">
          <div class="metric">
            <span class="label">当前区块高度:</span>
            <span class="value">{{ networkInfo.blockHeight }}</span>
          </div>
          <div class="metric">
            <span class="label">连接节点数:</span>
            <span class="value">{{ networkInfo.connectedNodes }}</span>
          </div>
          <div class="metric">
            <span class="label">网络延迟:</span>
            <span class="value">{{ networkInfo.latency }}ms</span>
          </div>
          <div class="metric">
            <span class="label">TPS:</span>
            <span class="value">{{ networkInfo.tps }}</span>
          </div>
        </div>
      </div>

      <!-- 账户信息 -->
      <div class="card">
        <div class="card-header">
          <h3>账户信息</h3>
        </div>
        <div class="card-content">
          <div class="metric">
            <span class="label">钱包地址:</span>
            <span class="value address">{{ account.address }}</span>
          </div>
          <div class="metric">
            <span class="label">余额:</span>
            <span class="value">{{ account.balance }} ETH</span>
          </div>
          <div class="metric">
            <span class="label">Gas费用:</span>
            <span class="value">{{ account.gasPrice }} Gwei</span>
          </div>
        </div>
      </div>

      <!-- 智能合约状态 -->
      <div class="card">
        <div class="card-header">
          <h3>智能合约</h3>
        </div>
        <div class="card-content">
          <div class="contract-list">
            <div class="contract-item" v-for="contract in contracts" :key="contract.address">
              <div class="contract-info">
                <div class="contract-name">{{ contract.name }}</div>
                <div class="contract-address">{{ contract.address }}</div>
              </div>
              <div class="contract-status" :class="contract.status">
                {{ contract.status === 'deployed' ? '已部署' : '未部署' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 交易历史 -->
      <div class="card transactions-card">
        <div class="card-header">
          <h3>最近交易</h3>
          <button class="btn-primary" @click="refreshTransactions">刷新</button>
        </div>
        <div class="card-content">
          <div class="transaction-list">
            <div class="transaction-item" v-for="tx in transactions" :key="tx.hash">
              <div class="tx-info">
                <div class="tx-hash">{{ tx.hash }}</div>
                <div class="tx-details">
                  <span>{{ tx.type }}</span>
                  <span>{{ tx.timestamp }}</span>
                </div>
              </div>
              <div class="tx-status" :class="tx.status">
                {{ getStatusText(tx.status) }}
              </div>
              <div class="tx-amount">{{ tx.amount }} ETH</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作面板 -->
      <div class="card">
        <div class="card-header">
          <h3>区块链操作</h3>
        </div>
        <div class="card-content">
          <div class="action-buttons">
            <button class="btn-primary" @click="deployContract">部署合约</button>
            <button class="btn-secondary" @click="sendTransaction">发送交易</button>
            <button class="btn-secondary" @click="queryBlock">查询区块</button>
            <button class="btn-secondary" @click="exportData">导出数据</button>
          </div>
        </div>
      </div>

      <!-- 节点管理 -->
      <div class="card">
        <div class="card-header">
          <h3>节点管理</h3>
        </div>
        <div class="card-content">
          <div class="node-list">
            <div class="node-item" v-for="node in nodes" :key="node.id">
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-endpoint">{{ node.endpoint }}</div>
              </div>
              <div class="node-status" :class="node.status">
                {{ node.status === 'active' ? '活跃' : '离线' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'Blockchain',
  setup() {
    const networkStatus = ref({
      text: '正常',
      class: 'status-normal'
    })

    const networkInfo = ref({
      blockHeight: 18450276,
      connectedNodes: 8,
      latency: 45,
      tps: 15
    })

    const account = ref({
      address: '0x1234...abcd',
      balance: 2.547,
      gasPrice: 20
    })

    const contracts = ref([
      {
        name: 'DVSS存储合约',
        address: '0xabcd...1234',
        status: 'deployed'
      },
      {
        name: 'PPA验证合约',
        address: '0xefgh...5678',
        status: 'deployed'
      },
      {
        name: '审计跟踪合约',
        address: '0xijkl...9012',
        status: 'deployed'
      }
    ])

    const transactions = ref([
      {
        hash: '0x1a2b3c...def456',
        type: '数据存储',
        timestamp: '2024-01-27 14:30:25',
        status: 'confirmed',
        amount: 0.001
      },
      {
        hash: '0x2b3c4d...efg567',
        type: 'PPA验证',
        timestamp: '2024-01-27 14:25:18',
        status: 'confirmed',
        amount: 0.002
      },
      {
        hash: '0x3c4d5e...fgh678',
        type: '审计记录',
        timestamp: '2024-01-27 14:20:45',
        status: 'pending',
        amount: 0.001
      },
      {
        hash: '0x4d5e6f...ghi789',
        type: '权限验证',
        timestamp: '2024-01-27 14:15:32',
        status: 'confirmed',
        amount: 0.0005
      }
    ])

    const nodes = ref([
      {
        id: 1,
        name: '主节点',
        endpoint: 'https://mainnet.infura.io',
        status: 'active'
      },
      {
        id: 2,
        name: '备用节点1',
        endpoint: 'https://backup1.node.com',
        status: 'active'
      },
      {
        id: 3,
        name: '备用节点2',
        endpoint: 'https://backup2.node.com',
        status: 'offline'
      }
    ])

    const getStatusText = (status) => {
      const statusMap = {
        'confirmed': '已确认',
        'pending': '待确认',
        'failed': '失败'
      }
      return statusMap[status] || status
    }

    const refreshTransactions = () => {
      console.log('刷新交易记录')
      // 模拟刷新
    }

    const deployContract = () => {
      console.log('部署智能合约')
    }

    const sendTransaction = () => {
      console.log('发送交易')
    }

    const queryBlock = () => {
      console.log('查询区块')
    }

    const exportData = () => {
      console.log('导出区块链数据')
    }

    return {
      networkStatus,
      networkInfo,
      account,
      contracts,
      transactions,
      nodes,
      getStatusText,
      refreshTransactions,
      deployContract,
      sendTransaction,
      queryBlock,
      exportData
    }
  }
}
</script>

<style scoped>
.blockchain-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  margin: 0;
}

.blockchain-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px 20px 10px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #333;
}

.card-content {
  padding: 20px;
}

.status-indicator {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.status-normal {
  background-color: #e8f5e8;
  color: #4caf50;
}

.metric {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.metric:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
}

.value {
  font-weight: bold;
  color: #333;
}

.address {
  font-family: monospace;
  font-size: 12px;
}



.contract-item, .node-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.contract-item:last-child, .node-item:last-child {
  border-bottom: none;
}

.contract-info, .node-info {
  flex: 1;
}

.contract-name, .node-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.contract-address, .node-endpoint {
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.contract-status, .node-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.contract-status.deployed, .node-status.active {
  background-color: #e8f5e8;
  color: #4caf50;
}

.node-status.offline {
  background-color: #ffebee;
  color: #f44336;
}

.transactions-card {
  grid-column: span 2;
}

.transaction-list {
  max-height: 300px;
  overflow-y: auto;
}

.transaction-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.transaction-item:last-child {
  border-bottom: none;
}

.tx-info {
  flex: 1;
}

.tx-hash {
  font-family: monospace;
  font-size: 12px;
  color: #333;
  margin-bottom: 4px;
}

.tx-details {
  font-size: 12px;
  color: #666;
}

.tx-details span {
  margin-right: 10px;
}

.tx-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  min-width: 60px;
  text-align: center;
}

.tx-status.confirmed {
  background-color: #e8f5e8;
  color: #4caf50;
}

.tx-status.pending {
  background-color: #fff3e0;
  color: #f57c00;
}

.tx-status.failed {
  background-color: #ffebee;
  color: #f44336;
}

.tx-amount {
  font-weight: bold;
  color: #333;
  min-width: 80px;
  text-align: right;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.btn-primary, .btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

@media (max-width: 768px) {
  .blockchain-grid {
    grid-template-columns: 1fr;
  }
  
  .transactions-card {
    grid-column: span 1;
  }
}
</style>
