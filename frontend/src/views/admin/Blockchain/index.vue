<template>
  <div class="blockchain-admin">
    <div class="page-header">
      <el-page-header>
        <template #content>
          <span class="text-large font-600 mr-3">区块链管理</span>
        </template>
      </el-page-header>
    </div>

    <el-card class="main-card">
      <el-tabs v-model="activeTab" class="demo-tabs">
        <el-tab-pane label="网络状态" name="network">
          <div class="network-status">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="status-card">
                  <el-statistic title="网络节点数" :value="networkInfo.nodeCount" />
                  <div class="status-indicator">
                    <el-tag :type="networkInfo.status === 'active' ? 'success' : 'danger'">
                      {{ networkInfo.status === 'active' ? '正常' : '异常' }}
                    </el-tag>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="status-card">
                  <el-statistic title="区块高度" :value="networkInfo.blockHeight" />
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="status-card">
                  <el-statistic title="交易总数" :value="networkInfo.totalTransactions" />
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="智能合约" name="contract">
          <div class="contract-management">
            <div class="toolbar">
              <el-button type="primary" @click="deployContract">
                <el-icon><Plus /></el-icon>
                部署合约
              </el-button>
              <el-button @click="refreshContracts">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>

            <el-table :data="contracts" style="width: 100%" v-loading="contractLoading">
              <el-table-column prop="name" label="合约名称" />
              <el-table-column prop="address" label="合约地址" />
              <el-table-column prop="version" label="版本" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                    {{ row.status === 'active' ? '激活' : '停用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="deployTime" label="部署时间" />
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button type="primary" text @click="viewContract(row)">
                    查看
                  </el-button>
                  <el-button type="warning" text @click="upgradeContract(row)">
                    升级
                  </el-button>
                  <el-button type="danger" text @click="disableContract(row)">
                    停用
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="交易监控" name="transactions">
          <div class="transaction-monitor">
            <div class="search-bar">
              <el-input
                v-model="searchQuery"
                placeholder="搜索交易ID或地址"
                style="width: 300px; margin-right: 10px;"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button type="primary" @click="searchTransactions">搜索</el-button>
            </div>

            <el-table :data="transactions" style="width: 100%" v-loading="transactionLoading">
              <el-table-column prop="txHash" label="交易哈希" width="200" />
              <el-table-column prop="blockNumber" label="区块号" />
              <el-table-column prop="from" label="发送方" />
              <el-table-column prop="to" label="接收方" />
              <el-table-column prop="value" label="金额" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="getTransactionStatusType(row.status)">
                    {{ getTransactionStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="timestamp" label="时间" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button type="primary" text @click="viewTransaction(row)">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination">
              <el-pagination
                :current-page="currentPage"
                :page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 部署合约对话框 -->
    <el-dialog v-model="deployDialogVisible" title="部署智能合约" width="600px">
      <el-form :model="deployForm" label-width="100px">
        <el-form-item label="合约名称">
          <el-input v-model="deployForm.name" placeholder="请输入合约名称" />
        </el-form-item>
        <el-form-item label="合约代码">
          <el-input
            v-model="deployForm.code"
            type="textarea"
            :rows="8"
            placeholder="请输入智能合约代码"
          />
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="deployForm.version" placeholder="如: v1.0.0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deployDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDeploy" :loading="deploying">
            部署
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'

// 响应式数据
const activeTab = ref('network')
const searchQuery = ref('')
const contractLoading = ref(false)
const transactionLoading = ref(false)
const deployDialogVisible = ref(false)
const deploying = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 网络信息
const networkInfo = reactive({
  nodeCount: 4,
  blockHeight: 12580,
  totalTransactions: 45621,
  status: 'active'
})

// 合约列表
const contracts = ref([
  {
    id: 1,
    name: 'DVSS-Core',
    address: '0x742d35Cc6734C0532925a3b8D8d7CC8D7a7d8B8F',
    version: 'v1.2.0',
    status: 'active',
    deployTime: '2024-01-15 10:30:00'
  },
  {
    id: 2,
    name: 'Privacy-Shield',
    address: '0x3C44CdDdB6a900fa2b585dd299e03d12FA429XYZ',
    version: 'v1.0.5',
    status: 'active',
    deployTime: '2024-01-10 14:22:00'
  }
])

// 交易列表
const transactions = ref([
  {
    txHash: '0xabc123...',
    blockNumber: 12580,
    from: '0x742d35Cc...',
    to: '0x3C44CdDd...',
    value: '0.5 ETH',
    status: 'success',
    timestamp: '2024-01-20 15:30:00'
  }
])

// 部署表单
const deployForm = reactive({
  name: '',
  code: '',
  version: ''
})

// 方法
const deployContract = () => {
  deployDialogVisible.value = true
  Object.assign(deployForm, { name: '', code: '', version: '' })
}

const confirmDeploy = async () => {
  if (!deployForm.name || !deployForm.code || !deployForm.version) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  deploying.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('合约部署成功')
    deployDialogVisible.value = false
    refreshContracts()
  } catch (error) {
    ElMessage.error('合约部署失败')
  } finally {
    deploying.value = false
  }
}

const refreshContracts = async () => {
  contractLoading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    // contracts.value = ... // 更新数据
  } finally {
    contractLoading.value = false
  }
}

const viewContract = (contract) => {
  ElMessage.info(`查看合约: ${contract.name}`)
}

const upgradeContract = (contract) => {
  ElMessageBox.confirm(`确定要升级合约 ${contract.name} 吗？`, '确认', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('合约升级成功')
  })
}

const disableContract = (contract) => {
  ElMessageBox.confirm(`确定要停用合约 ${contract.name} 吗？`, '确认', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('合约已停用')
  })
}

const searchTransactions = async () => {
  transactionLoading.value = true
  try {
    // 模拟搜索API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('搜索完成')
  } finally {
    transactionLoading.value = false
  }
}

const viewTransaction = (transaction) => {
  ElMessage.info(`查看交易详情: ${transaction.txHash}`)
}

const getTransactionStatusType = (status) => {
  const statusMap = {
    success: 'success',
    pending: 'warning',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

const getTransactionStatusText = (status) => {
  const statusMap = {
    success: '成功',
    pending: '待确认',
    failed: '失败'
  }
  return statusMap[status] || '未知'
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadTransactions()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadTransactions()
}

const loadTransactions = async () => {
  transactionLoading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
  } finally {
    transactionLoading.value = false
  }
}

onMounted(() => {
  // 初始化数据
  loadTransactions()
})
</script>

<style scoped>
.blockchain-admin {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.main-card {
  min-height: 600px;
}

.network-status {
  padding: 20px 0;
}

.status-card {
  text-align: center;
}

.status-indicator {
  margin-top: 10px;
}

.contract-management {
  padding: 20px 0;
}

.toolbar {
  margin-bottom: 20px;
}

.transaction-monitor {
  padding: 20px 0;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
