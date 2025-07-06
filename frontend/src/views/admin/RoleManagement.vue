<template>
  <div class="role-management">
    <div class="page-header">
      <h2>角色管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增角色
      </el-button>
    </div>

    <!-- 搜索过滤器 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px" inline>
        <el-form-item label="角色名称">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入角色名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable style="width: 120px">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchRoles">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 角色列表 -->
    <el-card class="table-card">
      <el-table 
        :data="roleList" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="角色名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="permissions" label="权限数量" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.permissions ? row.permissions.length : 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editRole(row)">
              编辑
            </el-button>
            <el-button type="info" size="small" @click="managePermissions(row)">
              权限配置
            </el-button>
            <el-button 
              :type="row.is_active ? 'danger' : 'success'" 
              size="small" 
              @click="toggleRoleStatus(row)"
              :disabled="row.name === 'admin'"
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

    <!-- 新增/编辑角色对话框 -->
    <el-dialog 
      :title="editingRole ? '编辑角色' : '新增角色'" 
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="roleForm" :rules="roleRules" ref="roleFormRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="roleForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="roleForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRole" :loading="saving">
          {{ editingRole ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog 
      title="权限配置" 
      v-model="showPermissionDialog"
      width="600px"
    >
      <div class="permission-config">
        <div class="permission-header">
          <span>为角色 "{{ currentRole?.name }}" 配置权限</span>
        </div>
        <el-tree
          ref="permissionTreeRef"
          :data="permissionTree"
          :props="treeProps"
          node-key="id"
          show-checkbox
          :default-checked-keys="checkedPermissions"
          @check="handlePermissionCheck"
        />
      </div>
      <template #footer>
        <el-button @click="showPermissionDialog = false">取消</el-button>
        <el-button type="primary" @click="savePermissions" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { roleApi } from '@/api/role'

const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showPermissionDialog = ref(false)
const editingRole = ref(null)
const currentRole = ref(null)

const roleList = ref([])
const permissionTree = ref([])
const checkedPermissions = ref([])

const searchForm = reactive({
  name: '',
  is_active: null
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const roleForm = reactive({
  name: '',
  description: '',
  is_active: true
})

const roleFormRef = ref()
const permissionTreeRef = ref()

const treeProps = {
  children: 'children',
  label: 'name'
}

const roleRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度应该在2-50字符之间', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述长度不能超过200字符', trigger: 'blur' }
  ]
}

// 模拟权限树数据
const mockPermissionTree = [
  {
    id: 'user',
    name: '用户管理',
    children: [
      { id: 'user:list', name: '查看用户列表' },
      { id: 'user:create', name: '创建用户' },
      { id: 'user:update', name: '编辑用户' },
      { id: 'user:delete', name: '删除用户' },
      { id: 'user:reset_password', name: '重置密码' }
    ]
  },
  {
    id: 'role',
    name: '角色管理',
    children: [
      { id: 'role:list', name: '查看角色列表' },
      { id: 'role:create', name: '创建角色' },
      { id: 'role:update', name: '编辑角色' },
      { id: 'role:delete', name: '删除角色' },
      { id: 'role:assign_permissions', name: '分配权限' }
    ]
  },
  {
    id: 'order',
    name: '订单管理',
    children: [
      { id: 'order:list', name: '查看订单列表' },
      { id: 'order:create', name: '创建订单' },
      { id: 'order:update', name: '编辑订单' },
      { id: 'order:delete', name: '删除订单' },
      { id: 'order:encrypt', name: '加密订单' },
      { id: 'order:decrypt', name: '解密订单' }
    ]
  },
  {
    id: 'field',
    name: '字段管理',
    children: [
      { id: 'field:list', name: '查看字段列表' },
      { id: 'field:create', name: '创建字段' },
      { id: 'field:update', name: '编辑字段' },
      { id: 'field:delete', name: '删除字段' }
    ]
  },
  {
    id: 'shard',
    name: '分片管理',
    children: [
      { id: 'shard:list', name: '查看分片列表' },
      { id: 'shard:create', name: '创建分片' },
      { id: 'shard:update', name: '编辑分片' },
      { id: 'shard:delete', name: '删除分片' }
    ]
  },
  {
    id: 'log',
    name: '日志管理',
    children: [
      { id: 'log:list', name: '查看操作日志' },
      { id: 'log:export', name: '导出日志' }
    ]
  },
  {
    id: 'system',
    name: '系统管理',
    children: [
      { id: 'system:config', name: '系统配置' },
      { id: 'system:monitor', name: '系统监控' },
      { id: 'system:backup', name: '数据备份' }
    ]
  }
]

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadRoles = async () => {
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

    const response = await roleApi.getRoleList(params)
    if (response.code === 200) {
      roleList.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载角色列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const searchRoles = () => {
  pagination.page = 1
  loadRoles()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    name: '',
    is_active: null
  })
  pagination.page = 1
  loadRoles()
}

const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadRoles()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadRoles()
}

const editRole = (role) => {
  editingRole.value = role
  Object.assign(roleForm, {
    name: role.name,
    description: role.description,
    is_active: role.is_active
  })
  showCreateDialog.value = true
}

const resetForm = () => {
  Object.assign(roleForm, {
    name: '',
    description: '',
    is_active: true
  })
  editingRole.value = null
  roleFormRef.value?.resetFields()
}

const saveRole = async () => {
  if (!roleFormRef.value) return
  
  const valid = await roleFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingRole.value) {
      const response = await roleApi.updateRole(editingRole.value.id, roleForm)
      if (response.code === 200) {
        ElMessage.success('角色更新成功')
        showCreateDialog.value = false
        resetForm()
        loadRoles()
      }
    } else {
      const response = await roleApi.createRole(roleForm)
      if (response.code === 200) {
        ElMessage.success('角色创建成功')
        showCreateDialog.value = false
        resetForm()
        loadRoles()
      }
    }
  } catch (error) {
    ElMessage.error(editingRole.value ? '角色更新失败' : '角色创建失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const managePermissions = async (role) => {
  currentRole.value = role
  permissionTree.value = mockPermissionTree
  
  try {
    const response = await roleApi.getRolePermissions(role.id)
    if (response.code === 200) {
      checkedPermissions.value = response.data || []
    }
  } catch (error) {
    console.error('加载角色权限失败:', error)
    checkedPermissions.value = []
  }
  
  showPermissionDialog.value = true
}

const handlePermissionCheck = () => {
  // 权限选择变化处理
}

const savePermissions = async () => {
  if (!currentRole.value) return

  saving.value = true
  try {
    const checkedKeys = permissionTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys()
    const allPermissions = [...checkedKeys, ...halfCheckedKeys]

    const response = await roleApi.updateRolePermissions(currentRole.value.id, {
      permissions: allPermissions
    })
    
    if (response.code === 200) {
      ElMessage.success('权限配置保存成功')
      showPermissionDialog.value = false
      loadRoles()
    }
  } catch (error) {
    ElMessage.error('权限配置保存失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const toggleRoleStatus = async (role) => {
  if (role.name === 'admin') {
    ElMessage.warning('管理员角色不能禁用')
    return
  }

  const action = role.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}角色 "${role.name}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await roleApi.updateRole(role.id, {
      is_active: !role.is_active
    })
    
    if (response.code === 200) {
      ElMessage.success(`角色${action}成功`)
      loadRoles()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`角色${action}失败`)
      console.error(error)
    }
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.role-management {
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

.permission-config {
  max-height: 400px;
  overflow-y: auto;
}

.permission-header {
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 500;
}
</style>
