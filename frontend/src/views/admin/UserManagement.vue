<template>
  <div class="user-management">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 搜索过滤器 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px" inline>
        <el-form-item label="用户名">
          <el-input 
            v-model="searchForm.username" 
            placeholder="请输入用户名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input 
            v-model="searchForm.email" 
            placeholder="请输入邮箱"
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
        <el-form-item label="角色">
          <el-select v-model="searchForm.role_id" placeholder="请选择角色" clearable style="width: 150px">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchUsers">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <el-table 
        :data="userList" 
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column prop="role_name" label="角色" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160">
          <template #default="{ row }">
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editUser(row)">
              编辑
            </el-button>
            <el-button type="warning" size="small" @click="resetPassword(row)">
              重置密码
            </el-button>
            <el-button 
              :type="row.is_active ? 'danger' : 'success'" 
              size="small" 
              @click="toggleUserStatus(row)"
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

    <!-- 新增/编辑用户对话框 -->
    <el-dialog 
      :title="editingUser ? '编辑用户' : '新增用户'" 
      v-model="showCreateDialog"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名" prop="full_name">
          <el-input v-model="userForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="userForm.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option 
              v-for="role in roles" 
              :key="role.id" 
              :label="role.name" 
              :value="role.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input 
            v-model="userForm.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">
          {{ editingUser ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog title="重置密码" v-model="showPasswordDialog" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="新密码" prop="password">
          <el-input 
            v-model="passwordForm.password" 
            type="password" 
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            placeholder="请确认新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="savePassword" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { userApi } from '@/api/user'
import { roleApi } from '@/api/role'

const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showPasswordDialog = ref(false)
const editingUser = ref(null)
const resetPasswordUser = ref(null)

const userList = ref([])
const roles = ref([])

const searchForm = reactive({
  username: '',
  email: '',
  is_active: null,
  role_id: null
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const userForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  role_id: null,
  is_active: true
})

const passwordForm = reactive({
  password: '',
  confirmPassword: ''
})

const userFormRef = ref()
const passwordFormRef = ref()

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度应该在3-50字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  role_id: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const passwordRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadUsers = async () => {
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

    const response = await userApi.getUserList(params)
    if (response.code === 200) {
      userList.value = response.data.items || []
      pagination.total = response.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const response = await roleApi.getRoleList({ page: 1, page_size: 100 })
    if (response.code === 200) {
      roles.value = response.data.items || []
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
  }
}

const searchUsers = () => {
  pagination.page = 1
  loadUsers()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    username: '',
    email: '',
    is_active: null,
    role_id: null
  })
  pagination.page = 1
  loadUsers()
}

const handleSizeChange = (val) => {
  pagination.page_size = val
  pagination.page = 1
  loadUsers()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadUsers()
}

const editUser = (user) => {
  editingUser.value = user
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    full_name: user.full_name,
    role_id: user.role_id,
    is_active: user.is_active,
    password: ''
  })
  showCreateDialog.value = true
}

const resetForm = () => {
  Object.assign(userForm, {
    username: '',
    email: '',
    full_name: '',
    password: '',
    role_id: null,
    is_active: true
  })
  editingUser.value = null
  userFormRef.value?.resetFields()
}

const saveUser = async () => {
  if (!userFormRef.value) return
  
  const valid = await userFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const userData = { ...userForm }
    
    if (editingUser.value) {
      // 编辑用户，移除密码字段
      delete userData.password
      const response = await userApi.updateUser(editingUser.value.id, userData)
      if (response.code === 200) {
        ElMessage.success('用户更新成功')
        showCreateDialog.value = false
        resetForm()
        loadUsers()
      }
    } else {
      // 新增用户
      const response = await userApi.createUser(userData)
      if (response.code === 200) {
        ElMessage.success('用户创建成功')
        showCreateDialog.value = false
        resetForm()
        loadUsers()
      }
    }
  } catch (error) {
    ElMessage.error(editingUser.value ? '用户更新失败' : '用户创建失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const resetPassword = (user) => {
  resetPasswordUser.value = user
  passwordForm.password = ''
  passwordForm.confirmPassword = ''
  showPasswordDialog.value = true
}

const savePassword = async () => {
  if (!passwordFormRef.value) return
  
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const response = await userApi.changePassword(resetPasswordUser.value.id, {
      new_password: passwordForm.password
    })
    if (response.code === 200) {
      ElMessage.success('密码重置成功')
      showPasswordDialog.value = false
      resetPasswordUser.value = null
    }
  } catch (error) {
    ElMessage.error('密码重置失败')
    console.error(error)
  } finally {
    saving.value = false
  }
}

const toggleUserStatus = async (user) => {
  const action = user.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${user.username}" 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await userApi.updateUser(user.id, {
      is_active: !user.is_active
    })
    
    if (response.code === 200) {
      ElMessage.success(`用户${action}成功`)
      loadUsers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`用户${action}失败`)
      console.error(error)
    }
  }
}

onMounted(() => {
  loadUsers()
  loadRoles()
})

// 监听对话框关闭，重置表单
watch(() => showCreateDialog.value, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>

<style scoped>
.user-management {
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
</style>
