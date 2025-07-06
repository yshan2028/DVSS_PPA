import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home,
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/encrypt',
      name: 'Encrypt',
      component: () => import('@/views/Encrypt.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/query',
      name: 'Query',
      component: () => import('@/views/Query.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dvss-analysis',
      name: 'DVSSAnalysis',
      component: () => import('@/views/DVSSAnalysis.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/blockchain-audit',
      name: 'BlockchainAudit',
      component: () => import('@/views/BlockchainAudit.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/monitoring',
      name: 'Monitoring',
      component: () => import('@/views/Monitoring.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/blockchain',
      name: 'Blockchain',
      component: () => import('@/views/Blockchain.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('@/views/Analytics.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isLoggedIn) {
      next('/login')
    } else {
      next()
    }
  } else {
    // 如果已登录且访问登录页或首页，重定向到仪表盘
    if (authStore.isLoggedIn && (to.path === '/login' || to.path === '/')) {
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router
