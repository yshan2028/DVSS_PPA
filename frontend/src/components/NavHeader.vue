<template>
  <el-header class="nav-header">
    <div class="header-content">
      <!-- Logo和标题 -->
      <div class="logo-section">
        <el-icon class="logo-icon">
          <Lock />
        </el-icon>
        <h1 class="title">{{ t('nav.title') }}</h1>
      </div>
      
      <!-- 用户信息和语言切换 -->
      <div class="user-section">
        <!-- 语言切换 -->
        <el-dropdown class="language-dropdown">
          <el-button type="text" class="language-btn">
            <el-icon><Setting /></el-icon>
            {{ i18nStore.currentLanguage === 'zh' ? '中文' : 'English' }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="i18nStore.setLanguage('zh')">中文</el-dropdown-item>
              <el-dropdown-item @click="i18nStore.setLanguage('en')">English</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 用户信息 -->
        <div v-if="authStore.isLoggedIn" class="user-info">
          <el-avatar :size="32" class="user-avatar">
            {{ authStore.currentUser?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="user-details">
            <span class="username">{{ authStore.currentUser?.username }}</span>
            <el-tag :type="getRoleTagType(authStore.currentUser?.role)" size="small">
              {{ getRoleLabel(authStore.currentUser?.role) }}
            </el-tag>
          </div>
          <el-button type="text" @click="handleLogout" class="logout-btn">
            <el-icon><SwitchButton /></el-icon>
            {{ t('auth.logout') }}
          </el-button>
        </div>
        <div v-else class="user-info">
          <span class="not-logged-in">{{ t('auth.notLoggedIn') }}</span>
        </div>
      </div>
    </div>
  </el-header>
</template>

<script setup>
import { Lock, Setting, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const i18nStore = useI18nStore()
const router = useRouter()
const { t } = i18nStore

const getRoleTagType = (role) => {
  const types = {
    seller: 'primary',
    payment_provider: 'success',
    logistics: 'warning',
    auditor: 'danger',
    platform: 'info'
  }
  return types[role] || 'default'
}

const getRoleLabel = (role) => {
  const labels = {
    seller: t('roles.seller'),
    payment_provider: t('roles.payment'),
    logistics: t('roles.logistics'),
    auditor: t('roles.auditor'),
    platform: t('roles.platform')
  }
  return labels[role] || role
}

const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success(t('auth.logoutSuccess') || '退出成功')
  router.push('/')
}
</script>

<style scoped>
.nav-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  height: 60px;
  line-height: 60px;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
  color: #fff;
}

.title {
  color: #fff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.language-dropdown {
  color: #fff;
}

.language-btn {
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.language-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
}

.username {
  font-weight: 500;
}

.logout-btn {
  color: #fff;
  font-size: 16px;
}

.not-logged-in {
  color: rgba(255, 255, 255, 0.7);
}
</style>
