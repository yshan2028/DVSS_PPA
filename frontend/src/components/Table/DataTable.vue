<template>
  <div class="data-table">
    <!-- 表格工具栏 -->
    <div class="table-toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left">
          <el-button
            v-if="showAdd"
            type="primary"
            @click="$emit('add')"
            :icon="Plus"
          >
            新增
          </el-button>
          <el-button
            v-if="showBatchDelete && selectedRows.length > 0"
            type="danger"
            @click="handleBatchDelete"
            :icon="Delete"
          >
            批量删除
          </el-button>
        </slot>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar-right">
          <el-input
            v-if="showSearch"
            v-model="searchKeyword"
            placeholder="请输入搜索关键字"
            :prefix-icon="Search"
            clearable
            style="width: 200px"
            @input="handleSearch"
          />
          <el-button
            v-if="showRefresh"
            @click="$emit('refresh')"
            :icon="Refresh"
          >
            刷新
          </el-button>
        </slot>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      :data="data"
      v-loading="loading"
      :stripe="stripe"
      :border="border"
      :size="size"
      :height="height"
      :max-height="maxHeight"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
    >
      <!-- 多选列 -->
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
        align="center"
      />
      
      <!-- 序号列 -->
      <el-table-column
        v-if="showIndex"
        type="index"
        label="#"
        width="60"
        align="center"
        :index="getIndex"
      />

      <!-- 数据列 -->
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :min-width="column.minWidth"
        :fixed="column.fixed"
        :align="column.align || 'left'"
        :sortable="column.sortable"
        :show-overflow-tooltip="column.showOverflowTooltip !== false"
      >
        <template #default="scope">
          <slot
            :name="column.prop"
            :row="scope.row"
            :column="column"
            :index="scope.$index"
          >
            <!-- 默认渲染 -->
            <span v-if="!column.type">{{ scope.row[column.prop] }}</span>
            
            <!-- 标签类型 -->
            <el-tag
              v-else-if="column.type === 'tag'"
              :type="getTagType(scope.row[column.prop], column.tagMap)"
            >
              {{ getTagText(scope.row[column.prop], column.tagMap) }}
            </el-tag>
            
            <!-- 日期类型 -->
            <span v-else-if="column.type === 'date'">
              {{ formatDate(scope.row[column.prop], column.format) }}
            </span>
            
            <!-- 操作类型 -->
            <div v-else-if="column.type === 'action'" class="table-actions">
              <el-button
                v-for="action in column.actions"
                :key="action.name"
                :type="action.type || 'primary'"
                :size="action.size || 'small'"
                :icon="action.icon"
                :disabled="action.disabled && action.disabled(scope.row)"
                @click="handleAction(action.name, scope.row, scope.$index)"
                link
              >
                {{ action.label }}
              </el-button>
            </div>
          </slot>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="table-pagination" v-if="showPagination">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizes"
        :total="total"
        :layout="paginationLayout"
        :background="true"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Search, Refresh } from '@element-plus/icons-vue'
import { formatDate as utilFormatDate } from '@/utils/date'

// Props
const props = defineProps({
  // 表格数据
  data: {
    type: Array,
    default: () => []
  },
  // 表格列配置
  columns: {
    type: Array,
    required: true
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 分页配置
  pagination: {
    type: Object,
    default: () => ({
      page: 1,
      size: 20,
      total: 0
    })
  },
  // 表格属性
  stripe: {
    type: Boolean,
    default: true
  },
  border: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'default'
  },
  height: {
    type: [String, Number],
    default: undefined
  },
  maxHeight: {
    type: [String, Number],
    default: undefined
  },
  // 功能开关
  showToolbar: {
    type: Boolean,
    default: true
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  showIndex: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  showAdd: {
    type: Boolean,
    default: true
  },
  showBatchDelete: {
    type: Boolean,
    default: false
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  // 分页配置
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  paginationLayout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

// Emits
const emit = defineEmits([
  'add',
  'refresh',
  'selection-change',
  'sort-change',
  'row-click',
  'action',
  'search',
  'page-change',
  'size-change',
  'batch-delete'
])

// 响应式数据
const searchKeyword = ref('')
const selectedRows = ref([])
const currentPage = ref(props.pagination.page)
const pageSize = ref(props.pagination.size)
const total = ref(props.pagination.total)

// 监听分页属性变化
watch(() => props.pagination, (newVal) => {
  currentPage.value = newVal.page
  pageSize.value = newVal.size
  total.value = newVal.total
}, { deep: true })

// 计算序号
const getIndex = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
  emit('selection-change', selection)
}

// 处理排序变化
const handleSortChange = (sort) => {
  emit('sort-change', sort)
}

// 处理行点击
const handleRowClick = (row, column, event) => {
  emit('row-click', row, column, event)
}

// 处理操作按钮点击
const handleAction = (actionName, row, index) => {
  emit('action', actionName, row, index)
}

// 处理搜索
const handleSearch = (keyword) => {
  emit('search', keyword)
}

// 处理批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
      '批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('batch-delete', selectedRows.value)
  } catch {
    // 用户取消
  }
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  emit('page-change', page)
}

// 处理页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  emit('size-change', size)
}

// 获取标签类型
const getTagType = (value, tagMap) => {
  return tagMap?.[value]?.type || 'info'
}

// 获取标签文本
const getTagText = (value, tagMap) => {
  return tagMap?.[value]?.text || value
}

// 格式化日期
const formatDate = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  return utilFormatDate(date, format)
}
</script>

<style scoped>
.data-table {
  background: #fff;
  border-radius: 4px;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.toolbar-left .el-button {
  margin-right: 8px;
}

.toolbar-right .el-input {
  margin-right: 8px;
}

.table-actions .el-button {
  margin-right: 4px;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
