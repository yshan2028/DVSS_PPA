<template>
  <div class="shard-management">
    <div class="page-header">
      <h2>分片管理</h2>
      <el-button type="primary" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="分片ID">
          <el-input v-model="searchForm.shardId" placeholder="请输入分片ID" clearable />
        </el-form-item>
        <el-form-item label="订单ID">
          <el-input v-model="searchForm.orderId" placeholder="请输入订单ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshRight /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分片列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="shardList"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="分片ID" width="100" />
        <el-table-column prop="orderId" label="订单ID" width="120" />
        <el-table-column prop="shardIndex" label="分片序号" width="100" />
        <el-table-column prop="totalShards" label="总分片数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="encryptionAlgorithm" label="加密算法" width="120" />
        <el-table-column prop="hashValue" label="哈希值" min-width="200" show-overflow-tooltip />
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="success"
              size="small"
              @click="handleDownload(row)"
              :disabled="row.status !== 'completed'"
            >
              下载
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :disabled="row.status === 'processing'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :small="false"
          :disabled="loading"
          :background="true"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 查看分片详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="分片详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="2" border v-if="currentShard">
        <el-descriptions-item label="分片ID">{{ currentShard.id }}</el-descriptions-item>
        <el-descriptions-item label="订单ID">{{ currentShard.orderId }}</el-descriptions-item>
        <el-descriptions-item label="分片序号">{{ currentShard.shardIndex }}</el-descriptions-item>
        <el-descriptions-item label="总分片数">{{ currentShard.totalShards }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentShard.status)">
            {{ getStatusText(currentShard.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="加密算法">{{ currentShard.encryptionAlgorithm }}</el-descriptions-item>
        <el-descriptions-item label="哈希值" :span="2">{{ currentShard.hashValue }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatFileSize(currentShard.size) }}</el-descriptions-item>
        <el-descriptions-item label="处理节点">{{ currentShard.processingNode || '未分配' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentShard.createdAt) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(currentShard.updatedAt) }}</el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2" v-if="currentShard.errorMessage">
          <el-text type="danger">{{ currentShard.errorMessage }}</el-text>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button
            type="success"
            @click="handleDownload(currentShard)"
            :disabled="currentShard.status !== 'completed'"
          >
            下载分片
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, RefreshRight } from '@element-plus/icons-vue'
import { useShardStore } from '@/stores/shard'

const shardStore = useShardStore()

// 响应式数据
const loading = ref(false)
const shardList = ref([])
const detailDialogVisible = ref(false)
const currentShard = ref(null)

// 搜索表单
const searchForm = reactive({
  shardId: '',
  orderId: '',
  status: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取分片列表
const fetchShardList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    
    const response = await shardStore.getShardList(params)
    shardList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取分片列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchShardList()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    shardId: '',
    orderId: '',
    status: ''
  })
  pagination.page = 1
  fetchShardList()
}

// 刷新
const handleRefresh = () => {
  fetchShardList()
}

// 查看分片详情
const handleView = (row) => {
  currentShard.value = row
  detailDialogVisible.value = true
}

// 下载分片
const handleDownload = async (row) => {
  try {
    await shardStore.downloadShard(row.id)
    ElMessage.success('分片下载已开始')
  } catch (error) {
    ElMessage.error('下载失败：' + error.message)
  }
}

// 删除分片
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分片 ${row.id} 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await shardStore.deleteShard(row.id)
    ElMessage.success('删除成功')
    fetchShardList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 分页处理
const handleSizeChange = (val) => {
  pagination.size = val
  pagination.page = 1
  fetchShardList()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  fetchShardList()
}

// 工具函数
const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// 生命周期
onMounted(() => {
  fetchShardList()
})
</script>

<style scoped>
.shard-management {
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

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  text-align: right;
}

.dialog-footer .el-button {
  margin-left: 10px;
}
</style>
