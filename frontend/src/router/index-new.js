/**
 * 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth-new'
import { ElMessage } from 'element-plus'

// 布局组件
const Layout = () => import('@/components/Layout/index.vue')

// 前台页面
const PublicRoutes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/public/Home.vue'),
    meta: {
      title: '首页',
      public: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/public/Login.vue'),
    meta: {
      title: '用户登录',
      public: true
    }
  },
  {
    path: '/encrypt',
    name: 'Encrypt',
    component: () => import('@/views/public/Encrypt.vue'),
    meta: {
      title: '数据加密',
      public: true
    }
  },
  {
    path: '/query',
    name: 'Query',
    component: () => import('@/views/public/Query.vue'),
    meta: {
      title: '数据查询',
      requiresAuth: true
    }
  }
]

// 后台管理路由
const AdminRoutes = {
  path: '/admin',
  component: Layout,
  redirect: '/admin/dashboard',
  meta: {
    title: '系统管理',
    requiresAuth: true,
    roles: ['admin', 'manager']
  },
  children: [
    {
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/admin/Dashboard.vue'),
      meta: {
        title: '仪表盘',
        icon: 'Dashboard'
      }
    },
    
    // 用户管理
    {
      path: 'user',
      name: 'UserManagement',
      redirect: '/admin/user/list',
      meta: {
        title: '用户管理',
        icon: 'User'
      },
      children: [
        {
          path: 'list',
          name: 'UserList',
          component: () => import('@/views/admin/User/UserList.vue'),
          meta: {
            title: '用户列表',
            permissions: ['user:read']
          }
        },
        {
          path: 'create',
          name: 'UserCreate',
          component: () => import('@/views/admin/User/UserForm.vue'),
          meta: {
            title: '创建用户',
            permissions: ['user:create'],
            hidden: true
          }
        },
        {
          path: 'edit/:id',
          name: 'UserEdit',
          component: () => import('@/views/admin/User/UserForm.vue'),
          meta: {
            title: '编辑用户',
            permissions: ['user:update'],
            hidden: true
          }
        },
        {
          path: 'detail/:id',
          name: 'UserDetail',
          component: () => import('@/views/admin/User/UserDetail.vue'),
          meta: {
            title: '用户详情',
            permissions: ['user:read'],
            hidden: true
          }
        }
      ]
    },
    
    // 角色管理
    {
      path: 'role',
      name: 'RoleManagement',
      redirect: '/admin/role/list',
      meta: {
        title: '角色管理',
        icon: 'UserFilled'
      },
      children: [
        {
          path: 'list',
          name: 'RoleList',
          component: () => import('@/views/admin/Role/RoleList.vue'),
          meta: {
            title: '角色列表',
            permissions: ['role:read']
          }
        },
        {
          path: 'create',
          name: 'RoleCreate',
          component: () => import('@/views/admin/Role/RoleForm.vue'),
          meta: {
            title: '创建角色',
            permissions: ['role:create'],
            hidden: true
          }
        },
        {
          path: 'edit/:id',
          name: 'RoleEdit',
          component: () => import('@/views/admin/Role/RoleForm.vue'),
          meta: {
            title: '编辑角色',
            permissions: ['role:update'],
            hidden: true
          }
        },
        {
          path: 'permission/:id',
          name: 'RolePermission',
          component: () => import('@/views/admin/Role/RolePermission.vue'),
          meta: {
            title: '权限配置',
            permissions: ['role:permission'],
            hidden: true
          }
        }
      ]
    },
    
    // 字段管理
    {
      path: 'field',
      name: 'FieldManagement',
      redirect: '/admin/field/list',
      meta: {
        title: '字段管理',
        icon: 'Grid'
      },
      children: [
        {
          path: 'list',
          name: 'FieldList',
          component: () => import('@/views/admin/Field/FieldList.vue'),
          meta: {
            title: '字段列表',
            permissions: ['field:read']
          }
        },
        {
          path: 'create',
          name: 'FieldCreate',
          component: () => import('@/views/admin/Field/FieldForm.vue'),
          meta: {
            title: '创建字段',
            permissions: ['field:create'],
            hidden: true
          }
        },
        {
          path: 'edit/:id',
          name: 'FieldEdit',
          component: () => import('@/views/admin/Field/FieldForm.vue'),
          meta: {
            title: '编辑字段',
            permissions: ['field:update'],
            hidden: true
          }
        },
        {
          path: 'sensitivity',
          name: 'SensitivityConfig',
          component: () => import('@/views/admin/Field/SensitivityConfig.vue'),
          meta: {
            title: '敏感度配置',
            permissions: ['field:config']
          }
        }
      ]
    },
    
    // 订单管理
    {
      path: 'order',
      name: 'OrderManagement',
      redirect: '/admin/order/list',
      meta: {
        title: '订单管理',
        icon: 'Document'
      },
      children: [
        {
          path: 'list',
          name: 'OrderList',
          component: () => import('@/views/admin/Order/OrderList.vue'),
          meta: {
            title: '订单列表',
            permissions: ['order:read']
          }
        },
        {
          path: 'detail/:id',
          name: 'OrderDetail',
          component: () => import('@/views/admin/Order/OrderDetail.vue'),
          meta: {
            title: '订单详情',
            permissions: ['order:read'],
            hidden: true
          }
        },
        {
          path: 'upload',
          name: 'OrderUpload',
          component: () => import('@/views/admin/Order/OrderUpload.vue'),
          meta: {
            title: '批量上传',
            permissions: ['order:create']
          }
        },
        {
          path: 'encryption',
          name: 'OrderEncryption',
          component: () => import('@/views/admin/Order/OrderEncryption.vue'),
          meta: {
            title: '加密管理',
            permissions: ['order:encrypt']
          }
        }
      ]
    },
    
    // 分片管理
    {
      path: 'shard',
      name: 'ShardManagement',
      redirect: '/admin/shard/list',
      meta: {
        title: '分片管理',
        icon: 'Connection'
      },
      children: [
        {
          path: 'list',
          name: 'ShardList',
          component: () => import('@/views/admin/Shard/ShardList.vue'),
          meta: {
            title: '分片列表',
            permissions: ['shard:read']
          }
        },
        {
          path: 'detail/:id',
          name: 'ShardDetail',
          component: () => import('@/views/admin/Shard/ShardDetail.vue'),
          meta: {
            title: '分片详情',
            permissions: ['shard:read'],
            hidden: true
          }
        },
        {
          path: 'nodes',
          name: 'NodeManagement',
          component: () => import('@/views/admin/Shard/NodeManagement.vue'),
          meta: {
            title: '节点管理',
            permissions: ['shard:manage']
          }
        },
        {
          path: 'reconstruction',
          name: 'ShardReconstruction',
          component: () => import('@/views/admin/Shard/ShardReconstruction.vue'),
          meta: {
            title: '数据重构',
            permissions: ['shard:reconstruct']
          }
        }
      ]
    },
    
    // 日志管理
    {
      path: 'log',
      name: 'LogManagement',
      redirect: '/admin/log/operation',
      meta: {
        title: '日志管理',
        icon: 'Document'
      },
      children: [
        {
          path: 'operation',
          name: 'OperationLog',
          component: () => import('@/views/admin/Log/OperationLog.vue'),
          meta: {
            title: '操作日志',
            permissions: ['log:read']
          }
        },
        {
          path: 'encryption',
          name: 'EncryptionLog',
          component: () => import('@/views/admin/Log/EncryptionLog.vue'),
          meta: {
            title: '加密日志',
            permissions: ['log:read']
          }
        },
        {
          path: 'decryption',
          name: 'DecryptionLog',
          component: () => import('@/views/admin/Log/DecryptionLog.vue'),
          meta: {
            title: '解密日志',
            permissions: ['log:read']
          }
        },
        {
          path: 'query',
          name: 'QueryLog',
          component: () => import('@/views/admin/Log/QueryLog.vue'),
          meta: {
            title: '查询日志',
            permissions: ['log:read']
          }
        },
        {
          path: 'audit',
          name: 'AuditReport',
          component: () => import('@/views/admin/Log/AuditReport.vue'),
          meta: {
            title: '审计报告',
            permissions: ['log:audit']
          }
        }
      ]
    }
  ]
}

// 错误页面
const ErrorRoutes = [
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在',
      public: true
    }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '无权限访问',
      public: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

// 创建路由
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...PublicRoutes,
    AdminRoutes,
    ...ErrorRoutes
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - DVSS-PPA系统` : 'DVSS-PPA系统'
  
  // 公开路由直接通过
  if (to.meta.public) {
    return next()
  }
  
  // 需要认证的路由
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      ElMessage.warning('请先登录')
      return next('/login')
    }
    
    // 检查角色权限
    if (to.meta.roles && !to.meta.roles.some(role => authStore.hasRole(role))) {
      ElMessage.error('无权限访问此页面')
      return next('/403')
    }
    
    // 检查具体权限
    if (to.meta.permissions && !to.meta.permissions.some(permission => authStore.hasPermission(permission))) {
      ElMessage.error('无权限访问此页面')
      return next('/403')
    }
  }
  
  next()
})

export default router
