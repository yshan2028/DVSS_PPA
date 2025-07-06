/**
 * 国际化状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useI18nStore = defineStore('i18n', () => {
  // 状态
  const currentLanguage = ref('zh') // 默认中文
  const supportedLanguages = ref([
    { code: 'zh', name: '中文' },
    { code: 'en', name: 'English' }
  ])

  // 语言包
  const messages = ref({
    zh: {
      // 通用
      common: {
        confirm: '确认',
        cancel: '取消',
        save: '保存',
        edit: '编辑',
        delete: '删除',
        add: '添加',
        search: '搜索',
        loading: '加载中...',
        success: '操作成功',
        error: '操作失败',
        noData: '暂无数据'
      },
      // 菜单
      menu: {
        dashboard: '仪表板',
        userManagement: '用户管理',
        roleManagement: '角色管理',
        fieldManagement: '字段管理',
        orderManagement: '订单管理',
        shardManagement: '分片管理',
        logManagement: '日志管理',
        blockchainManagement: '区块链管理',
        systemSettings: '系统设置'
      },
      // 认证
      auth: {
        login: '登录',
        logout: '退出',
        username: '用户名',
        password: '密码',
        loginSuccess: '登录成功',
        loginFailed: '登录失败',
        pleaseLogin: '请先登录'
      }
    },
    en: {
      // Common
      common: {
        confirm: 'Confirm',
        cancel: 'Cancel',
        save: 'Save',
        edit: 'Edit',
        delete: 'Delete',
        add: 'Add',
        search: 'Search',
        loading: 'Loading...',
        success: 'Success',
        error: 'Error',
        noData: 'No Data'
      },
      // Menu
      menu: {
        dashboard: 'Dashboard',
        userManagement: 'User Management',
        roleManagement: 'Role Management',
        fieldManagement: 'Field Management',
        orderManagement: 'Order Management',
        shardManagement: 'Shard Management',
        logManagement: 'Log Management',
        blockchainManagement: 'Blockchain Management',
        systemSettings: 'System Settings'
      },
      // Auth
      auth: {
        login: 'Login',
        logout: 'Logout',
        username: 'Username',
        password: 'Password',
        loginSuccess: 'Login Success',
        loginFailed: 'Login Failed',
        pleaseLogin: 'Please Login'
      }
    }
  })

  // 方法
  const setLanguage = (lang) => {
    if (supportedLanguages.value.find(l => l.code === lang)) {
      currentLanguage.value = lang
      // 保存到localStorage
      localStorage.setItem('language', lang)
    }
  }

  const t = (key) => {
    const keys = key.split('.')
    let value = messages.value[currentLanguage.value]
    
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = value[k]
      } else {
        return key // 如果找不到翻译，返回原key
      }
    }
    
    return value || key
  }

  const initLanguage = () => {
    // 从localStorage获取语言设置
    const savedLang = localStorage.getItem('language')
    if (savedLang && supportedLanguages.value.find(l => l.code === savedLang)) {
      currentLanguage.value = savedLang
    } else {
      // 根据浏览器语言设置默认语言
      const browserLang = navigator.language.split('-')[0]
      if (supportedLanguages.value.find(l => l.code === browserLang)) {
        currentLanguage.value = browserLang
      }
    }
  }

  // 初始化
  initLanguage()

  return {
    currentLanguage,
    supportedLanguages,
    messages,
    setLanguage,
    t,
    initLanguage
  }
})
