<template>
  <el-card class="user-login-card" shadow="always">
    <template #header>
      <div class="card-header">
        <el-icon><User /></el-icon>
        <span>{{ t('auth.title') }}</span>
      </div>
    </template>

    <div class="login-content">
      <el-form :model="loginForm" label-position="top">
        <el-form-item :label="t('auth.selectRole')">
          <el-select 
            v-model="loginForm.role" 
            :placeholder="t('auth.rolePlaceholder')"
            size="large"
            style="width: 100%"
          >
            <el-option
              v-for="role in availableRoles"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            >
              <div class="role-option">
                <el-tag :type="role.type" size="small">{{ role.code }}</el-tag>
                <span class="role-name">{{ role.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="t('auth.username')">
          <el-input
            v-model="loginForm.username"
            :placeholder="t('auth.usernamePlaceholder')"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            @click="handleLogin"
            :loading="loading"
            style="width: 100%"
          >
            {{ t('auth.login') }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="role-permissions" v-if="loginForm.role">
        <h4>{{ t('auth.rolePermissions') }}</h4>
        <div class="permission-grid">
          <el-tag
            v-for="field in getRolePermissions(loginForm.role)"
            :key="field"
            type="success"
            size="small"
          >
            {{ field }}
          </el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import { User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore

const loading = ref(false)
const loginForm = ref({
  role: '',
  username: ''
})

const availableRoles = computed(() => [
  { value: 'seller', label: t('roles.seller'), code: 'SE', type: 'primary' },
  { value: 'payment_provider', label: t('roles.payment'), code: 'PP', type: 'success' },
  { value: 'logistics', label: t('roles.logistics'), code: 'LO', type: 'warning' },
  { value: 'auditor', label: t('roles.auditor'), code: 'AU', type: 'danger' },
  { value: 'platform', label: t('roles.platform'), code: 'PL', type: 'info' }
])

const rolePermissions = {
  seller: ['customer_name', 'customer_phone', 'delivery_address'],
  payment_provider: ['payment_amount', 'bank_card_number'],
  logistics: ['customer_phone_partial', 'delivery_address'],
  auditor: ['customer_name', 'payment_amount', 'identity_card'],
  platform: ['customer_name', 'payment_amount', 'all_metadata']
}

const getRolePermissions = (role) => {
  return rolePermissions[role] || []
}

const handleLogin = async () => {
  if (!loginForm.value.role || !loginForm.value.username) {
    ElMessage.warning(t('auth.fillRequired'))
    return
  }

  loading.value = true
  try {
    await authStore.login(loginForm.value.role, loginForm.value.username)
    ElMessage.success(t('auth.loginSuccess'))
  } catch (error) {
    ElMessage.error(t('auth.loginFailed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.user-login-card {
  max-width: 480px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.login-content {
  padding: 10px 0;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role-name {
  font-weight: 500;
}

.role-permissions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.role-permissions h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}

.permission-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
