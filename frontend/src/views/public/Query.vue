<template>
  <div class="query-page">
    <div class="page-header">
      <h1>数据查询</h1>
      <p>在保护隐私的前提下查询和分析数据</p>
    </div>

    <el-row :gutter="20">
      <!-- 查询条件 -->
      <el-col :span="8">
        <el-card class="query-form-card">
          <template #header>
            <div class="card-header">
              <span>查询条件</span>
              <el-button type="text" @click="resetQuery">重置</el-button>
            </div>
          </template>
          
          <el-form :model="queryForm" ref="queryFormRef" label-width="100px">
            <el-form-item label="查询类型">
              <el-select v-model="queryForm.query_type" placeholder="请选择查询类型" style="width: 100%">
                <el-option label="订单查询" value="order" />
                <el-option label="统计分析" value="statistics" />
                <el-option label="趋势分析" value="trend" />
                <el-option label="自定义查询" value="custom" />
              </el-select>
            </el-form-item>

            <el-form-item label="数据范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="查询字段">
              <el-select 
                v-model="queryForm.fields" 
                multiple 
                placeholder="请选择要查询的字段"
                style="width: 100%"
              >
                <el-option 
                  v-for="field in availableFields" 
                  :key="field.id" 
                  :label="field.field_name" 
                  :value="field.id"
                  :disabled="field.sensitivity_level === 'critical'"
                >
                  <span>{{ field.field_name }}</span>
                  <el-tag 
                    :type="getSensitivityColor(field.sensitivity_level)" 
                    size="small" 
                    style="margin-left: 8px"
                  >
                    {{ getSensitivityText(field.sensitivity_level) }}
                  </el-tag>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="聚合方式" v-if="queryForm.query_type === 'statistics'">
              <el-select v-model="queryForm.aggregation" placeholder="请选择聚合方式" style="width: 100%">
                <el-option label="计数" value="count" />
                <el-option label="求和" value="sum" />
                <el-option label="平均值" value="avg" />
                <el-option label="最大值" value="max" />
                <el-option label="最小值" value="min" />
              </el-select>
            </el-form-item>

            <el-form-item label="过滤条件">
              <div class="filter-conditions">
                <div 
                  v-for="(condition, index) in queryForm.conditions" 
                  :key="index"
                  class="condition-item"
                >
                  <el-select 
                    v-model="condition.field" 
                    placeholder="字段"
                    style="width: 100px"
                  >
                    <el-option 
                      v-for="field in searchableFields" 
                      :key="field.id" 
                      :label="field.field_name" 
                      :value="field.id" 
                    />
                  </el-select>
                  <el-select 
                    v-model="condition.operator" 
                    placeholder="操作符"
                    style="width: 80px; margin: 0 8px"
                  >
                    <el-option label="=" value="eq" />
                    <el-option label=">" value="gt" />
                    <el-option label="<" value="lt" />
                    <el-option label="包含" value="contains" />
                  </el-select>
                  <el-input 
                    v-model="condition.value" 
                    placeholder="值"
                    style="width: 100px"
                  />
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeCondition(index)"
                    style="margin-left: 8px"
                  >
                    删除
                  </el-button>
                </div>
                <el-button type="text" @click="addCondition">
                  <el-icon><Plus /></el-icon>
                  添加条件
                </el-button>
              </div>
            </el-form-item>

            <el-form-item label="隐私等级">
              <el-slider
                v-model="queryForm.privacy_level"
                :min="1"
                :max="5"
                :marks="privacyMarks"
                show-tooltip
              />
              <div class="privacy-description">
                <small>{{ getPrivacyDescription(queryForm.privacy_level) }}</small>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="executeQuery" 
                :loading="querying"
                style="width: 100%"
              >
                <el-icon><Search /></el-icon>
                执行查询
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 查询历史 -->
        <el-card class="query-history-card" style="margin-top: 20px">
          <template #header>
            <span>查询历史</span>
          </template>
          <div class="query-history">
            <div 
              v-for="(query, index) in queryHistory" 
              :key="index"
              class="history-item"
              @click="loadHistoryQuery(query)"
            >
              <div class="history-title">{{ query.title }}</div>
              <div class="history-time">{{ formatDate(query.created_at) }}</div>
            </div>
            <div v-if="queryHistory.length === 0" class="no-history">
              暂无查询历史
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 查询结果 -->
      <el-col :span="16">
        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>查询结果</span>
              <div class="result-actions" v-if="queryResult.data && queryResult.data.length > 0">
                <el-button type="text" @click="exportResult">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
                <el-button type="text" @click="shareResult">
                  <el-icon><Share /></el-icon>
                  分享
                </el-button>
              </div>
            </div>
          </template>

          <div v-loading="querying" class="result-content">
            <!-- 空状态 -->
            <div v-if="!queryResult.data" class="empty-result">
              <el-empty description="请设置查询条件并执行查询" />
            </div>

            <!-- 查询结果 -->
            <div v-else-if="queryResult.data.length > 0">
              <!-- 结果统计 -->
              <div class="result-stats">
                <el-row :gutter="20">
                  <el-col :span="6" v-for="stat in queryResult.stats" :key="stat.label">
                    <div class="stat-item">
                      <div class="stat-value">{{ stat.value }}</div>
                      <div class="stat-label">{{ stat.label }}</div>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <!-- 数据表格 -->
              <el-table 
                :data="queryResult.data" 
                style="width: 100%; margin-top: 20px"
                max-height="400"
              >
                <el-table-column 
                  v-for="column in queryResult.columns" 
                  :key="column.key"
                  :prop="column.key" 
                  :label="column.label"
                  :width="column.width"
                >
                  <template #default="{ row }">
                    <span v-if="column.type === 'privacy'">
                      {{ maskPrivacyData(row[column.key], column.privacy_level) }}
                    </span>
                    <span v-else>
                      {{ row[column.key] }}
                    </span>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 图表展示 -->
              <div v-if="queryForm.query_type === 'statistics'" class="chart-container">
                <div ref="chartRef" style="width: 100%; height: 300px; margin-top: 20px"></div>
              </div>

              <!-- 分页 -->
              <div class="pagination-container" v-if="queryResult.total > queryResult.data.length">
                <el-pagination
                  :current-page="resultPagination.page"
                  :page-size="resultPagination.page_size"
                  :total="queryResult.total"
                  layout="total, prev, pager, next"
                  @current-change="handleResultPageChange"
                />
              </div>
            </div>

            <!-- 无结果 -->
            <div v-else class="no-result">
              <el-empty description="查询无结果，请调整查询条件" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Download, Share } from '@element-plus/icons-vue'
import { orderApi } from '@/api/order'
import { fieldApi } from '@/api/field'

const querying = ref(false)
const queryFormRef = ref()
const chartRef = ref()

const availableFields = ref([])
const searchableFields = ref([])
const queryHistory = ref([])
const queryResult = ref({
  data: null,
  columns: [],
  stats: [],
  total: 0
})

const dateRange = ref([])
const queryForm = reactive({
  query_type: 'order',
  fields: [],
  aggregation: 'count',
  conditions: [],
  privacy_level: 3,
  start_date: '',
  end_date: ''
})

const resultPagination = reactive({
  page: 1,
  page_size: 20
})

const privacyMarks = {
  1: '最低',
  2: '低',
  3: '中等',
  4: '高',
  5: '最高'
}

const getSensitivityColor = (level) => {
  const colorMap = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return colorMap[level] || ''
}

const getSensitivityText = (level) => {
  const textMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '极高'
  }
  return textMap[level] || level
}

const getPrivacyDescription = (level) => {
  const descriptions = {
    1: '最低隐私保护，数据可能直接显示',
    2: '低隐私保护，部分数据脱敏',
    3: '中等隐私保护，敏感数据加密',
    4: '高隐私保护，只显示统计结果',
    5: '最高隐私保护，严格差分隐私'
  }
  return descriptions[level] || ''
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadFields = async () => {
  try {
    const response = await fieldApi.getFieldList({ page: 1, page_size: 100 })
    if (response.code === 200) {
      availableFields.value = response.data.items || []
      searchableFields.value = availableFields.value.filter(field => field.is_searchable)
    }
  } catch (error) {
    console.error('加载字段列表失败:', error)
  }
}

const loadQueryHistory = async () => {
  try {
    // 这里调用API获取查询历史
    // const response = await queryApi.getQueryHistory()
    // if (response.code === 200) {
    //   queryHistory.value = response.data || []
    // }
    
    // 模拟数据
    queryHistory.value = [
      {
        title: '订单统计查询',
        created_at: '2024-01-20T10:30:00Z',
        query_type: 'statistics',
        conditions: []
      },
      {
        title: '客户分析查询',
        created_at: '2024-01-19T15:20:00Z',
        query_type: 'trend',
        conditions: []
      }
    ]
  } catch (error) {
    console.error('加载查询历史失败:', error)
  }
}

const addCondition = () => {
  queryForm.conditions.push({
    field: '',
    operator: 'eq',
    value: ''
  })
}

const removeCondition = (index) => {
  queryForm.conditions.splice(index, 1)
}

const resetQuery = () => {
  Object.assign(queryForm, {
    query_type: 'order',
    fields: [],
    aggregation: 'count',
    conditions: [],
    privacy_level: 3,
    start_date: '',
    end_date: ''
  })
  dateRange.value = []
  queryResult.value = {
    data: null,
    columns: [],
    stats: [],
    total: 0
  }
}

const executeQuery = async () => {
  if (queryForm.fields.length === 0) {
    ElMessage.warning('请选择要查询的字段')
    return
  }

  querying.value = true
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      queryForm.start_date = dateRange.value[0]
      queryForm.end_date = dateRange.value[1]
    }

    const queryParams = {
      ...queryForm,
      page: resultPagination.page,
      page_size: resultPagination.page_size
    }

    // 调用查询API
    const response = await orderApi.queryData(queryParams)
    if (response.code === 200) {
      queryResult.value = response.data
      
      // 如果是统计查询，绘制图表
      if (queryForm.query_type === 'statistics') {
        await nextTick()
        drawChart()
      }
      
      ElMessage.success('查询完成')
    }
  } catch (error) {
    ElMessage.error('查询失败')
    console.error(error)
  } finally {
    querying.value = false
  }
}

const handleResultPageChange = (page) => {
  resultPagination.page = page
  executeQuery()
}

const loadHistoryQuery = (query) => {
  Object.assign(queryForm, query)
  executeQuery()
}

const maskPrivacyData = (data, privacyLevel) => {
  if (!data) return ''
  
  const dataStr = String(data)
  const level = queryForm.privacy_level
  
  if (level >= 4) {
    return '***'
  } else if (level >= 3) {
    const maskLength = Math.floor(dataStr.length * 0.6)
    return dataStr.substring(0, dataStr.length - maskLength) + '*'.repeat(maskLength)
  } else if (level >= 2) {
    const maskLength = Math.floor(dataStr.length * 0.3)
    return dataStr.substring(0, dataStr.length - maskLength) + '*'.repeat(maskLength)
  }
  
  return dataStr
}

const drawChart = () => {
  // 这里可以使用 ECharts 或其他图表库绘制图表
  if (!chartRef.value || !queryResult.value.data) return
  
  // 示例：使用简单的图表展示
  console.log('绘制图表', queryResult.value.data)
}

const exportResult = () => {
  // 导出查询结果
  ElMessage.info('导出功能开发中')
}

const shareResult = () => {
  // 分享查询结果
  ElMessage.info('分享功能开发中')
}

onMounted(() => {
  loadFields()
  loadQueryHistory()
  addCondition() // 默认添加一个条件
})
</script>

<style scoped>
.query-page {
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.5rem;
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #606266;
  font-size: 1.1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-form-card {
  min-height: 600px;
}

.filter-conditions {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 12px;
  background-color: #fafafa;
}

.condition-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.condition-item:last-of-type {
  margin-bottom: 8px;
}

.privacy-description {
  margin-top: 8px;
  color: #909399;
  text-align: center;
}

.query-history {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-item:last-child {
  border-bottom: none;
}

.history-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.no-history {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.result-card {
  min-height: 600px;
}

.result-content {
  min-height: 500px;
}

.empty-result,
.no-result {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.result-stats {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 4px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.chart-container {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.result-actions {
  display: flex;
  gap: 8px;
}
</style>
