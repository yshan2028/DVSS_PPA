<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <NavHeader />
    
    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <SideNavigation />
      </el-aside>
      
      <!-- 内容区域 -->
      <el-main class="content-area">
        <!-- 角色登录区域 -->
        <UserLogin v-if="!authStore.isLoggedIn" />
        
        <!-- 登录后的主要功能 -->
        <div v-else class="dashboard-grid">
          <!-- 系统概览 -->
          <SystemOverview />
          
          <!-- L/S 值计算公式 -->
          <LSFormula />
          
          <!-- 快速操作 -->
          <QuickActions />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'

import NavHeader from '@/components/NavHeader.vue'
import SideNavigation from '@/components/SideNavigation.vue'
import UserLogin from '@/components/UserLogin.vue'
import SystemOverview from '@/components/SystemOverview.vue'
import LSFormula from '@/components/LSFormula.vue'
import QuickActions from '@/components/QuickActions.vue'

const authStore = useAuthStore()
const i18nStore = useI18nStore()

onMounted(() => {
  // 页面加载时的初始化逻辑
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.main-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.content-area {
  padding: 20px;
  overflow-y: auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 2fr 1fr;
  }
}
</style>
