<template>
  <div class="blockchain-management">
    <div class="page-header">
      <h2>区块链管理</h2>
      <el-button type="primary" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </div>

    <!-- 网络状态卡片 -->
    <el-row :gutter="20" class="status-cards">
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon network">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="status-content">
              <div class="status-title">网络状态</div>
              <div class="status-value" :class="networkStatus.status">
                {{ networkStatus.text }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon peers">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="status-content">
              <div class="status-title">活跃节点</div>
              <div class="status-value">{{ peerCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon blocks">
              <el-icon><Box /></el-icon>
            </div>
            <div class="status-content">
              <div class="status-title">区块高度</div>
              <div class="status-value">{{ blockHeight }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="status-card">
          <div class="status-item">
            <div class="status-icon transactions">
              <el-icon><Document /></el-icon>
            </div>
            <div class="status-content">
              <div class="status-title">总交易数</div>
              <div class="status-value">{{ transactionCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 节点管理 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>节点管理</span>
          <el-button type="primary" size="small" @click="handleAddPeer">
            <el-icon><Plus /></el-icon>
            添加节点
          </el-button>
        </div>
      </template>
      
      <el-table :data="peerList" stripe border>
        <el-table-column prop="name" label="节点名称" width="150" />
        <el-table-column prop="endpoint" label="节点地址" width="200" />
        <el-table-column prop="organization" label="组织" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="blockHeight" label="区块高度" width="120" />
        <el-table-column prop="lastSeen" label="最后活跃" width="160">
          <template #default="{ row }">
            {{ formatDate(row.lastSeen) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewPeer(row)">
              查看
            </el-button>
            <el-button 
              type="warning" 
              size="small" 
              @click="handleRestartPeer(row)"
              :disabled="row.status === 'offline'"
            >
              重启
            </el-button>
            <el-button type="danger" size="small" @click="handleRemovePeer(row)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 链码管理 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>链码管理</span>
          <el-button type="primary" size="small" @click="handleDeployChaincode">
            <el-icon><Upload /></el-icon>
            部署链码
          </el-button>
        </div>
      </template>
      
      <el-table :data="chaincodeList" stripe border>
        <el-table-column prop="name" label="链码名称" width="150" />
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="channel" label="通道" width="120" />
        <el-table-column prop="language" label="语言" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getChaincodeStatusType(row.status)" size="small">
              {{ getChaincodeStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deployedAt" label="部署时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.deployedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleInvokeChaincode(row)">
              调用
            </el-button>
            <el-button type="warning" size="small" @click="handleUpgradeChaincode(row)">
              升级
            </el-button>
            <el-button type="danger" size="small" @click="handleUninstallChaincode(row)">
              卸载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 区块浏览器 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <span>区块浏览器</span>
          <el-input
            v-model="searchHash"
            placeholder="输入区块哈希或交易ID"
            style="width: 300px"
            @keyup.enter="handleSearchBlock"
          >
            <template #append>
              <el-button @click="handleSearchBlock">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </template>
      
      <el-table :data="blockList" stripe border>
        <el-table-column prop="number" label="区块号" width="100" />
        <el-table-column prop="hash" label="区块哈希" width="200" show-overflow-tooltip />
        <el-table-column prop="previousHash" label="前一区块哈希" width="200" show-overflow-tooltip />
        <el-table-column prop="transactionCount" label="交易数" width="100" />
        <el-table-column prop="timestamp" label="时间戳" width="160">
          <template #default="{ row }">
            {{ formatDate(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewBlock(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="blockPagination.page"
          :page-size="blockPagination.size"
          :page-sizes="[10, 20, 50]"
          :small="false"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="blockPagination.total"
          @size-change="handleBlockSizeChange"
          @current-change="handleBlockCurrentChange"
        />
      </div>
    </el-card>

    <!-- 区块详情对话框 -->
    <el-dialog
      v-model="blockDetailVisible"
      title="区块详情"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentBlock">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="区块号">{{ currentBlock.number }}</el-descriptions-item>
          <el-descriptions-item label="交易数">{{ currentBlock.transactionCount }}</el-descriptions-item>
          <el-descriptions-item label="区块哈希" :span="2">{{ currentBlock.hash }}</el-descriptions-item>
          <el-descriptions-item label="前一区块哈希" :span="2">{{ currentBlock.previousHash }}</el-descriptions-item>
          <el-descriptions-item label="默克尔根" :span="2">{{ currentBlock.merkleRoot }}</el-descriptions-item>
          <el-descriptions-item label="时间戳">{{ formatDate(currentBlock.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="大小">{{ currentBlock.size }} bytes</el-descriptions-item>
        </el-descriptions>

        <div class="transactions-section" v-if="currentBlock.transactions">
          <h4>交易列表</h4>
          <el-table :data="currentBlock.transactions" stripe border max-height="300">
            <el-table-column prop="txId" label="交易ID" width="200" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="chaincode" label="链码" width="120" />
            <el-table-column prop="function" label="函数" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'VALID' ? 'success' : 'danger'" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="blockDetailVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, Connection, UserFilled, Box, Document, 
  Plus, Upload, Search 
} from '@element-plus/icons-vue'
import { useFabricStore } from '@/stores/fabric'

const fabricStore = useFabricStore()

// 响应式数据
const loading = ref(false)
const searchHash = ref('')
const blockDetailVisible = ref(false)
const currentBlock = ref(null)

// 网络状态
const networkStatus = ref({
  status: 'online',
  text: '正常'
})
const peerCount = ref(0)
const blockHeight = ref(0)
const transactionCount = ref(0)

// 节点列表
const peerList = ref([])

// 链码列表
const chaincodeList = ref([])

// 区块列表
const blockList = ref([])
const blockPagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取网络状态
const fetchNetworkStatus = async () => {
  try {
    const response = await fabricStore.getNetworkStatus()
    const data = response.data
    
    networkStatus.value = {
      status: data.status === 'active' ? 'online' : 'offline',
      text: data.status === 'active' ? '正常' : '异常'
    }
    peerCount.value = data.peerCount
    blockHeight.value = data.blockHeight
    transactionCount.value = data.transactionCount
  } catch (error) {
    console.error('获取网络状态失败:', error)
  }
}

// 获取节点列表
const fetchPeerList = async () => {
  try {
    const response = await fabricStore.getPeerList()
    peerList.value = response.data
  } catch (error) {
    ElMessage.error('获取节点列表失败：' + error.message)
  }
}

// 获取链码列表
const fetchChaincodeList = async () => {
  try {
    const response = await fabricStore.getChaincodeList()
    chaincodeList.value = response.data
  } catch (error) {
    ElMessage.error('获取链码列表失败：' + error.message)
  }
}

// 获取区块列表
const fetchBlockList = async () => {
  try {
    const params = {
      page: blockPagination.page,
      size: blockPagination.size
    }
    const response = await fabricStore.getBlockList(params)
    blockList.value = response.data.items
    blockPagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取区块列表失败：' + error.message)
  }
}

// 刷新所有数据
const handleRefresh = async () => {
  loading.value = true
  try {
    await Promise.all([
      fetchNetworkStatus(),
      fetchPeerList(),
      fetchChaincodeList(),
      fetchBlockList()
    ])
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 节点管理操作
const handleAddPeer = () => {
  ElMessage.info('添加节点功能开发中')
}

const handleViewPeer = (row) => {
  ElMessage.info(`查看节点 ${row.name} 详情`)
}

const handleRestartPeer = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重启节点 ${row.name} 吗？`,
      '确认重启',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await fabricStore.restartPeer(row.name)
    ElMessage.success('节点重启命令已发送')
    fetchPeerList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重启失败：' + error.message)
    }
  }
}

const handleRemovePeer = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除节点 ${row.name} 吗？此操作不可撤销。`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await fabricStore.removePeer(row.name)
    ElMessage.success('节点移除成功')
    fetchPeerList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败：' + error.message)
    }
  }
}

// 链码管理操作
const handleDeployChaincode = () => {
  ElMessage.info('部署链码功能开发中')
}

const handleInvokeChaincode = (row) => {
  ElMessage.info(`调用链码 ${row.name} 功能开发中`)
}

const handleUpgradeChaincode = (row) => {
  ElMessage.info(`升级链码 ${row.name} 功能开发中`)
}

const handleUninstallChaincode = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要卸载链码 ${row.name} 吗？`,
      '确认卸载',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await fabricStore.uninstallChaincode(row.name)
    ElMessage.success('链码卸载成功')
    fetchChaincodeList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('卸载失败：' + error.message)
    }
  }
}

// 区块浏览器操作
const handleSearchBlock = async () => {
  if (!searchHash.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  try {
    const response = await fabricStore.searchBlock(searchHash.value.trim())
    if (response.data) {
      currentBlock.value = response.data
      blockDetailVisible.value = true
    } else {
      ElMessage.warning('未找到相关区块或交易')
    }
  } catch (error) {
    ElMessage.error('搜索失败：' + error.message)
  }
}

const handleViewBlock = async (row) => {
  try {
    const response = await fabricStore.getBlockDetail(row.number)
    currentBlock.value = response.data
    blockDetailVisible.value = true
  } catch (error) {
    ElMessage.error('获取区块详情失败：' + error.message)
  }
}

// 区块分页处理
const handleBlockSizeChange = (val) => {
  blockPagination.size = val
  blockPagination.page = 1
  fetchBlockList()
}

const handleBlockCurrentChange = (val) => {
  blockPagination.page = val
  fetchBlockList()
}

// 工具函数
const getChaincodeStatusType = (status) => {
  const typeMap = {
    installed: 'success',
    instantiated: 'primary',
    upgrading: 'warning',
    error: 'danger'
  }
  return typeMap[status] || 'info'
}

const getChaincodeStatusText = (status) => {
  const textMap = {
    installed: '已安装',
    instantiated: '已实例化',
    upgrading: '升级中',
    error: '错误'
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  handleRefresh()
})
</script>

<style scoped>
.blockchain-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.status-cards {
  margin-bottom: 20px;
}

.status-card {
  height: 100px;
}

.status-item {
  display: flex;
  align-items: center;
  height: 100%;
}

.status-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.status-icon.network {
  background: #e3f2fd;
  color: #1976d2;
}

.status-icon.peers {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-icon.blocks {
  background: #e8f5e8;
  color: #388e3c;
}

.status-icon.transactions {
  background: #fff3e0;
  color: #f57c00;
}

.status-content {
  flex: 1;
}

.status-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.status-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.status-value.online {
  color: #67c23a;
}

.status-value.offline {
  color: #f56c6c;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.transactions-section {
  margin-top: 20px;
}

.transactions-section h4 {
  margin-bottom: 10px;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}
</style>
