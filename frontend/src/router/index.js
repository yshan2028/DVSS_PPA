import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 公共页面（前台）
const publicRoutes = [
  {
    path: '/',
    name: 'PublicLayout',
    component: () => import('@/components/Layout/PublicLayout.vue'),
    redirect: '/public/home',
    children: [
      {
        path: 'public/home',
        name: 'PublicHome',
        component: () => import('@/views/public/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'public/query',
        name: 'PublicQuery',
        component: () => import('@/views/public/Query.vue'),
        meta: { title: '数据查询' }
      },
      {
        path: 'public/encrypt',
        name: 'PublicEncrypt',
        component: () => import('@/views/public/Encrypt.vue'),
        meta: { title: '数据加密' }
      },
      {
        path: 'public/about',
        name: 'PublicAbout',
        component: () => import('@/views/public/About.vue'),
        meta: { title: '关于我们' }
      },
      {
        path: 'public/contact',
        name: 'PublicContact',
        component: () => import('@/views/public/Contact.vue'),
        meta: { title: '联系我们' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/public/Register.vue'),
    meta: { title: '注册' }
  }
]

// 管理后台页面
const adminRoutes = [
  {
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('@/components/Layout/AppLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { 
          title: '仪表板',
          requiresAuth: true,
          permissions: ['dashboard:view']
        }
      },
      // 用户管理
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue'),
        meta: { 
          title: '用户管理',
          requiresAuth: true,
          permissions: ['user:list']
        }
      },
      // 角色管理
      {
        path: 'roles',
        name: 'RoleManagement',
        component: () => import('@/views/admin/RoleManagement.vue'),
        meta: { 
          title: '角色管理',
          requiresAuth: true,
          permissions: ['role:list']
        }
      },
      // 字段管理
      {
        path: 'fields',
        name: 'FieldManagement',
        component: () => import('@/views/admin/FieldManagement.vue'),
        meta: { 
          title: '字段管理',
          requiresAuth: true,
          permissions: ['field:list']
        }
      },
      // 订单管理
      {
        path: 'orders',
        name: 'OrderManagement',
        component: () => import('@/views/admin/OrderManagement.vue'),
        meta: { 
          title: '订单管理',
          requiresAuth: true,
          permissions: ['order:list']
        }
      },
      // 分片管理
      {
        path: 'shards',
        name: 'ShardManagement',
        component: () => import('@/views/admin/ShardManagement.vue'),
        meta: { 
          title: '分片管理',
          requiresAuth: true,
          permissions: ['shard:list']
        }
      },
      // 日志管理
      {
        path: 'logs',
        name: 'LogManagement',
        component: () => import('@/views/admin/LogManagement.vue'),
        meta: { 
          title: '操作日志',
          requiresAuth: true,
          permissions: ['log:list']
        }
      },
      // 区块链管理
      {
        path: 'blockchain',
        name: 'BlockchainManagement',
        component: () => import('@/views/admin/BlockchainManagement.vue'),
        meta: { 
          title: '区块链管理',
          requiresAuth: true,
          permissions: ['blockchain:view']
        }
      },
      // 系统设置
      {
        path: 'settings',
        name: 'SystemSettings',
        component: () => import('@/views/admin/SystemSettings.vue'),
        meta: { 
          title: '系统设置',
          requiresAuth: true,
          permissions: ['system:config']
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...publicRoutes,
    ...adminRoutes,
    // 404页面
    {
      path: '/404',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '页面不存在' }
    },
    // 重定向所有未匹配路由到404页面
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - DVSS-PPA`
  } else {
    document.title = 'DVSS-PPA 数据验证与安全系统'
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 检查权限
    if (to.meta.permissions && to.meta.permissions.length > 0) {
      const hasPermission = to.meta.permissions.some(permission => 
        authStore.hasPermission(permission)
      )
      
      if (!hasPermission) {
        // 没有权限，重定向到首页或显示无权限页面
        next({
          path: '/admin/dashboard',
          query: { error: 'no_permission' }
        })
        return
      }
    }
  }

  // 如果已登录用户访问登录页，重定向到仪表板
  if (to.path === '/login' && authStore.isAuthenticated) {
    next('/admin/dashboard')
    return
  }

  next()
})

// 路由后置守卫
router.afterEach((to, from) => {
  // 页面加载完成后的处理
  // 可以在这里添加页面访问统计等功能
})

export default router
