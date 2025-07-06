<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <el-header class="app-header" height="60px">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-text">DVSS</div>
          <h1 class="app-title">DVSS-PPA 系统</h1>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleUserCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" :src="userInfo.avatar">
                {{ userInfo.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userInfo.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人设置</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 侧边栏 -->
    <el-container class="main-container">
      <el-aside class="app-sidebar" :width="sidebarWidth">
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          :unique-opened="true"
          class="sidebar-menu"
          router
        >
          <!-- 根据用户角色显示不同菜单 -->
          <template v-for="menu in menus" :key="menu.path">
            <el-sub-menu v-if="menu.children" :index="menu.path">
              <template #title>
                <el-icon><component :is="menu.icon" /></el-icon>
                <span>{{ menu.title }}</span>
              </template>
              <el-menu-item
                v-for="child in menu.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon><component :is="child.icon" /></el-icon>
                <span>{{ child.title }}</span>
              </el-menu-item>
            </el-sub-menu>
            
            <el-menu-item v-else :index="menu.path">
              <el-icon><component :is="menu.icon" /></el-icon>
              <span>{{ menu.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
        
        <!-- 侧边栏折叠按钮 -->
        <div class="sidebar-toggle" @click="toggleSidebar">
          <el-icon><Fold v-if="!sidebarCollapsed" /><Expand v-else /></el-icon>
        </div>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <!-- 面包屑导航 -->
        <div class="breadcrumb-container">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="item in breadcrumbs"
              :key="item.path"
              :to="{ path: item.path }"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <!-- 页面内容 -->
        <div class="page-content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  Fold,
  Expand,
  House,
  User,
  Setting,
  Document,
  DataAnalysis,
  Lock,
  Monitor,
  Files
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏状态
const sidebarCollapsed = ref(false)
const sidebarWidth = computed(() => sidebarCollapsed.value ? '64px' : '200px')

// 用户信息
const userInfo = computed(() => authStore.userInfo || {})

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title
  }))
})

// 菜单配置
const menus = computed(() => {
  const user = authStore.userInfo
  const isAdmin = user?.role?.name === 'admin' || user?.is_superuser
  
  let menuConfig = []
  
  if (isAdmin) {
    // 管理员菜单
    menuConfig = [
      {
        path: '/admin/dashboard',
        title: '仪表板',
        icon: 'House'
      },
      {
        path: '/admin/users',
        title: '用户管理',
        icon: 'User',
        children: [
          { path: '/admin/users/list', title: '用户列表', icon: 'User' },
          { path: '/admin/roles/list', title: '角色管理', icon: 'Setting' }
        ]
      },
      {
        path: '/admin/orders',
        title: '订单管理',
        icon: 'Document',
        children: [
          { path: '/admin/orders/list', title: '订单列表', icon: 'Document' },
          { path: '/admin/orders/fields', title: '字段管理', icon: 'Files' }
        ]
      },
      {
        path: '/admin/security',
        title: '安全管理',
        icon: 'Lock',
        children: [
          { path: '/admin/security/encryption', title: '加密管理', icon: 'Lock' },
          { path: '/admin/security/shards', title: '分片管理', icon: 'Files' }
        ]
      },
      {
        path: '/admin/logs',
        title: '日志审计',
        icon: 'Monitor'
      },
      {
        path: '/admin/analytics',
        title: '数据分析',
        icon: 'DataAnalysis'
      },
      {
        path: '/admin/blockchain',
        title: '区块链',
        icon: 'Monitor'
      }
    ]
  } else {
    // 普通用户菜单
    menuConfig = [
      {
        path: '/dashboard',
        title: '首页',
        icon: 'House'
      },
      {
        path: '/orders',
        title: '我的订单',
        icon: 'Document'
      },
      {
        path: '/query',
        title: '数据查询',
        icon: 'DataAnalysis'
      },
      {
        path: '/security',
        title: '安全中心',
        icon: 'Lock'
      }
    ]
  }
  
  return menuConfig
})

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'password':
      router.push('/profile/password')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await authStore.logout()
        ElMessage.success('退出登录成功')
        router.push('/login')
      } catch (error) {
        // 用户取消退出
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  
  .header-content {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .header-left {
    display: flex;
    align-items: center;
    
    .logo {
      width: 32px;
      height: 32px;
      margin-right: 12px;
    }
    
    .app-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .header-right {
    .user-dropdown {
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 4px;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      .username {
        margin: 0 8px;
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

.main-container {
  flex: 1;
}

.app-sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  position: relative;
  transition: width 0.3s;
  
  .sidebar-menu {
    height: 100%;
    border-right: none;
  }
  
  .sidebar-toggle {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f7fa;
    border-radius: 50%;
    cursor: pointer;
    transition: background-color 0.3s;
    
    &:hover {
      background: #e4e7ed;
    }
  }
}

.app-main {
  background: #f5f7fa;
  padding: 0;
  
  .breadcrumb-container {
    background: #fff;
    padding: 12px 20px;
    border-bottom: 1px solid #e4e7ed;
    margin-bottom: 20px;
  }
  
  .page-content {
    padding: 0 20px 20px;
  }
}
</style>
