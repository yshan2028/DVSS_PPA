<template>
  <div class="layout-container">
    <!-- 导航栏 -->
    <div class="navbar">
      <div class="nav-left">
        <div class="logo">
          <el-icon><Lock /></el-icon>
          <span>DVSS-PPA</span>
        </div>
      </div>
      <div class="nav-right">
        <div v-if="authStore.isLoggedIn" class="user-info">
          <span class="username">{{ authStore.currentUser?.username }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32">
              <el-icon><User /></el-icon>
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside :width="sidebarCollapsed ? '64px' : '240px'" class="sidebar">
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon>
            <component :is="sidebarCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
        </div>
        
        <el-menu
          :default-active="$route.path"
          class="sidebar-menu"
          :collapse="sidebarCollapsed"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item>
          
          <el-menu-item index="/query">
            <el-icon><Search /></el-icon>
            <template #title>数据查询</template>
          </el-menu-item>
          
          <el-menu-item index="/encrypt" v-if="canUploadData">
            <el-icon><Upload /></el-icon>
            <template #title>数据上传</template>
          </el-menu-item>
          
          <el-menu-item index="/dvss-analysis">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>敏感度分析</template>
          </el-menu-item>
          
          <el-menu-item index="/blockchain-audit">
            <el-icon><Document /></el-icon>
            <template #title>区块链审计</template>
          </el-menu-item>
          
          <el-menu-item index="/monitoring">
            <el-icon><Monitor /></el-icon>
            <template #title>系统监控</template>
          </el-menu-item>
          
          <el-sub-menu index="/advanced" v-if="hasAdvancedPermissions">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>高级功能</span>
            </template>
            <el-menu-item index="/blockchain">区块链管理</el-menu-item>
            <el-menu-item index="/analytics">数据分析</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 内容区域 -->
      <el-main class="content-area">
        <slot></slot>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const sidebarCollapsed = ref(false)

// 计算属性
const canUploadData = computed(() => {
  const permissions = authStore.currentUser?.permissions || []
  return permissions.includes('write_order') || permissions.includes('manage')
})

const hasAdvancedPermissions = computed(() => {
  const user = authStore.currentUser
  return user && (user.access_level >= 4 || user.permissions?.includes('manage'))
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        authStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.navbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-left .logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.nav-left .logo .el-icon {
  font-size: 24px;
}

.nav-right .user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: #606266;
  font-size: 14px;
}

.main-container {
  height: calc(100vh - 60px);
}

.sidebar {
  background: white;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s;
  position: relative;
  overflow: hidden;
}

.sidebar-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.3s;
}

.sidebar-toggle:hover {
  background: #e4e7ed;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 120px);
  overflow-y: auto;
  margin-top: 50px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

.content-area {
  padding: 0;
  overflow: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar {
    padding: 0 10px;
  }
  
  .nav-left .logo span {
    display: none;
  }
  
  .sidebar {
    position: fixed;
    height: calc(100vh - 60px);
    z-index: 999;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .content-area {
    margin-left: 0 !important;
  }
}
</style>
