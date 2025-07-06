<template>
  <div class="field-management">
    <div class="page-header">
      <h2>字段管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增字段
      </el-button>
    </div>

    <!-- 搜索过滤器 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="100px" inline>
        <el-form-item label="字段名称">
          <el-input 
            v-model="searchForm.field_name" 
            placeholder="请输入字段名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="字段类型">
          <el-select v-model="searchForm.field_type" placeholder="请选择字段类型" clearable style="width: 150px">
            <el-option label="字符串" value="string" />
            <el-option label="整数" value="integer" />
            <el-option label="浮点数" value="float" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="日期" value="date" />
            <el-option label="时间戳" value="timestamp" />
          </el-select>
        </el-form-item>
        <el-form-item label="敏感级别">
          <el-select v-model="searchForm.sensitivity_level" placeholder="请选择敏感级别" clearable style="width: 120px">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="极高" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchFields">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 字段列表 -->
    <el-card class="table-card">
      <el-table 
        :data="fieldList" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="field_name" label="字段名称" />
        <el-table-column prop="field_type" label="字段类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getFieldTypeColor(row.field_type)">
              {{ getFieldTypeText(row.field_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sensitivity_level" label="敏感级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getSensitivityColor(row.sensitivity_level)">
              {{ getSensitivityText(row.sensitivity_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="encryption_algorithm" label="加密算法" width="120" />
        <el-table-column prop="is_required" label="必填" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_required ? 'success' : 'info'">
              {{ row.is_required ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editField(row)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="viewFieldUsage(row)">
              使用情况
            </el-button>
            <el-button 
              :type="row.is_active ? 'danger' : 'success'" 
              size="small" 
              @click="toggleFieldStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          :current-page="pagination.page"
          :page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑字段对话框 -->
    <el-dialog 
      :title="editingField ? '编辑字段' : '新增字段'" 
      v-model="showCreateDialog"
      width="600px"
    >
      <el-form :model="fieldForm" :rules="fieldRules" ref="fieldFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="字段名称" prop="field_name">
              <el-input v-model="fieldForm.field_name" placeholder="请输入字段名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="字段类型" prop="field_type">
              <el-select v-model="fieldForm.field_type" style="width: 100%">
                <el-option label="字符串" value="string" />
                <el-option label="整数" value="integer" />
                <el-option label="浮点数" value="float" />
                <el-option label="布尔值" value="boolean" />
                <el-option label="日期" value="date" />
                <el-option label="时间戳" value="timestamp" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="字段描述" prop="description">
          <el-input 
            v-model="fieldForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入字段描述"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="敏感级别" prop="sensitivity_level">
              <el-select v-model="fieldForm.sensitivity_level" style="width: 100%">
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
                <el-option label="极高" value="critical" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="加密算法" prop="encryption_algorithm">
              <el-select v-model="fieldForm.encryption_algorithm" style="width: 100%">
                <el-option label="AES-256" value="AES256" />
                <el-option label="RSA-2048" value="RSA2048" />
                <el-option label="ChaCha20" value="ChaCha20" />
                <el-option label="SM4" value="SM4" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="是否必填">
              <el-switch v-model="fieldForm.is_required" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="是否可搜索">
              <el-switch v-model="fieldForm.is_searchable" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态">
              <el-switch v-model="fieldForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="验证规则">
          <el-input 
            v-model="fieldForm.validation_rules" 
            placeholder="请输入验证规则(JSON格式)"
          />
        </el-form-item>

        <el-form-item label="默认值">
          <el-input 
            v-model="fieldForm.default_value" 
            placeholder="请输入默认值"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveField" :loading="saving">
          {{ editingField ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 字段使用情况对话框 -->
    <el-dialog title="字段使用情况" v-model="showUsageDialog" width="700px">
      <div class="field-usage" v-if="currentField">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="字段名称">{{ currentField.field_name }}</el-descriptions-item>
          <el-descriptions-item label="使用次数">{{ currentField.usage_count }}</el-descriptions-item>
          <el-descriptions-item label="首次使用">{{ formatDate(currentField.first_used_at) }}</el-descriptions-item>
          <el-descriptions-item label="最近使用">{{ formatDate(currentField.last_used_at) }}</el-descriptions-item>
        </el-descriptions>
        
        <div style="margin-top: 20px">
          <h4>使用统计</h4>
          <el-table :data="usageStats" style="width: 100%">
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="usage_count" label="使用次数" />
            <el-table-column prop="order_count" label="订单数量" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { fieldApi } from '@/api/field'

const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showUsageDialog = ref(false)
const editingField = ref(null)
const currentField = ref(null)

const fieldList = ref([])
const usageStats = ref([])

const searchForm = reactive({
  field_name: '',
  field_type: '',
  sensitivity_level: '',
  is_active: null
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const fieldForm = reactive({
  field_name: '',
  field_type: 'string',
  description: '',
  sensitivity_level: 'low',
  encryption_algorithm: 'AES256',
  is_required: false,
  is_searchable: true,
  is_active: true,
  validation_rules: '',
  default_value: ''
})

const fieldFormRef = ref()

const fieldRules = {
  field_name: [
    { required: true, message: '请输入字段名称', trigger: 'blur' },
    { min: 2, max: 50, message: '字段名称长度应该在2-50字符之间', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '字段名称必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  field_type: [
    { required: true, message: '请选择字段类型', trigger: 'change' }
  ],
  sensitivity_level: [
    { required: true, message: '请选择敏感级别', trigger: 'change' }
  ],
  encryption_algorithm: [
    { required: true, message: '请选择加密算法', trigger: 'change' }
  ]
}

const getFieldTypeColor = (type) => {
  const colorMap = {
    'string': '',
    'integer': 'success',
    'float': 'warning',
    'boolean': 'info',
    'date': 'primary',
    'timestamp': 'danger'
  }
  return colorMap[type] || ''
}

const getFieldTypeText = (type) => {
  const textMap = {
    'string': '字符串',
    'integer': '整数',
    'float': '浮点数',
    'boolean': '布尔值',
    'date': '日期',
    'timestamp': '时间戳'
  }
  return textMap[type] || type
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

const formatDate = (dateStr) => {
  if (!dateStr) return '暂无'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadFields = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') {
        delete params[key]
      }
    })

    const response = await fieldApi.getFieldList(params)
    if (response.code === 200) {
      fieldList.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载字段列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchFields = () => {
  pagination.page = 1
  loadFields()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    field_name: '',
    field_type: '',
    sensitivity_level: '',
    is_active: null
  })
  pagination.page = 1
  loadFields()
}

const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadFields()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadFields()
}

const editField = (field) => {
  editingField.value = field
  Object.assign(fieldForm, {
    field_name: field.field_name,
    field_type: field.field_type,
    description: field.description,
    sensitivity_level: field.sensitivity_level,
    encryption_algorithm: field.encryption_algorithm,
    is_required: field.is_required,
    is_searchable: field.is_searchable,
    is_active: field.is_active,
    validation_rules: field.validation_rules || '',
    default_value: field.default_value || ''
  })
  showCreateDialog.value = true
}

const resetForm = () => {
  Object.assign(fieldForm, {
    field_name: '',
    field_type: 'string',
    description: '',
    sensitivity_level: 'low',
    encryption_algorithm: 'AES256',
    is_required: false,
    is_searchable: true,
    is_active: true,
    validation_rules: '',
    default_value: ''
  })
  editingField.value = null
  fieldFormRef.value?.resetFields()
}

const saveField = async () => {
  if (!fieldFormRef.value) return
  
  const valid = await fieldFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const fieldData = { ...fieldForm }
    
    // 处理验证规则
    if (fieldData.validation_rules) {
      try {
        JSON.parse(fieldData.validation_rules)
      } catch (e) {
        ElMessage.error('验证规则必须是有效的JSON格式')
        saving.value = false
        return
      }
    }

    if (editingField.value) {
      const response = await fieldApi.updateField(editingField.value.id, fieldData)
      if (response.code === 200) {
        ElMessage.success('字段更新成功')
        showCreateDialog.value = false
        resetForm()
        loadFields()
      }
    } else {
      const response = await fieldApi.createField(fieldData)
      if (response.code === 200) {
        ElMessage.success('字段创建成功')
        showCreateDialog.value = false
        resetForm()
        loadFields()
      }
    }
  } catch (error) {
    ElMessage.error(editingField.value ? '字段更新失败' : '字段创建失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const viewFieldUsage = async (field) => {
  currentField.value = field
  
  try {
    const response = await fieldApi.getFieldUsage(field.id)
    if (response.code === 200) {
      usageStats.value = response.data.usage_stats || []
    }
  } catch (error) {
    console.error('加载字段使用情况失败:', error)
    usageStats.value = []
  }
  
  showUsageDialog.value = true
}

const toggleFieldStatus = async (field) => {
  const action = field.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}字段 "${field.field_name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await fieldApi.updateField(field.id, {
      is_active: !field.is_active
    })
    
    if (response.code === 200) {
      ElMessage.success(`字段${action}成功`)
      loadFields()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`字段${action}失败`)
      console.error(error)
    }
  }
}

onMounted(() => {
  loadFields()
})
</script>

<style scoped>
.field-management {
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

.field-usage {
  padding: 16px 0;
}
</style>
