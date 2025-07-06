<template>
  <div class="side-navigation">
    <el-menu
      :default-active="$route.path"
      router
      :unique-opened="true"
      text-color="#ffffff"
      active-text-color="#409EFF"
      background-color="transparent"
    >
      <div class="nav-header">
        <el-icon><Lock /></el-icon>
        <span>{{ t('nav.title') }}</span>
      </div>

      <el-menu-item index="/dashboard" v-if="authStore.isLoggedIn">
        <el-icon><House /></el-icon>
        <span>{{ t('nav.dashboard') }}</span>
      </el-menu-item>

      <el-menu-item index="/dvss-analysis" v-if="authStore.isLoggedIn">
        <el-icon><DataLine /></el-icon>
        <span>{{ t('nav.dvssAnalysis') }}</span>
      </el-menu-item>

      <el-menu-item index="/encrypt" v-if="authStore.isLoggedIn">
        <el-icon><Lock /></el-icon>
        <span>{{ t('nav.encrypt') }}</span>
      </el-menu-item>

      <el-menu-item index="/query" v-if="authStore.isLoggedIn">
        <el-icon><Search /></el-icon>
        <span>{{ t('nav.query') }}</span>
      </el-menu-item>

      <el-menu-item index="/blockchain-audit" v-if="authStore.isLoggedIn">
        <el-icon><Link /></el-icon>
        <span>{{ t('nav.blockchainAudit') }}</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import { 
  Lock, 
  House, 
  Search, 
  Monitor, 
  Link, 
  DataLine 
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore
</script>

<style scoped>
.side-navigation {
  height: 100%;
  padding: 10px 0;
}

.nav-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
  color: #ffffff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 10px;
}

.el-menu {
  border-right: none;
}

.el-menu-item {
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.3s ease;
}

.el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.el-menu-item.is-active {
  background: rgba(64, 158, 255, 0.2) !important;
  border: 1px solid rgba(64, 158, 255, 0.3);
}
</style>
