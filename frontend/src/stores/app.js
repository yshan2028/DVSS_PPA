/**
 * 应用全局状态管理
 */
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 侧边栏
    sidebar: {
      opened: true,
      withoutAnimation: false
    },
    
    // 设备类型
    device: 'desktop',
    
    // 主题
    theme: 'light',
    
    // 语言
    language: 'zh-CN',
    
    // 加载状态
    loading: false,
    
    // 全局配置
    settings: {
      title: 'DVSS-PPA系统',
      logo: '/logo.png',
      fixedHeader: true,
      sidebarLogo: true,
      tagsView: true
    },
    
    // 系统信息
    systemInfo: {
      version: '1.0.0',
      environment: 'development'
    },
    
    // 错误信息
    errorLogs: []
  }),

  getters: {
    // 侧边栏状态
    sidebarOpened: (state) => state.sidebar.opened,
    
    // 当前主题
    currentTheme: (state) => state.theme,
    
    // 当前语言
    currentLanguage: (state) => state.language,
    
    // 是否移动设备
    isMobile: (state) => state.device === 'mobile',
    
    // 是否正在加载
    isLoading: (state) => state.loading,
    
    // 应用设置
    appSettings: (state) => state.settings
  },

  actions: {
    // 切换侧边栏
    toggleSidebar() {
      this.sidebar.opened = !this.sidebar.opened
      this.sidebar.withoutAnimation = false
      
      // 保存到本地存储
      localStorage.setItem('sidebarStatus', this.sidebar.opened ? '1' : '0')
    },

    // 关闭侧边栏
    closeSidebar(withoutAnimation = false) {
      this.sidebar.opened = false
      this.sidebar.withoutAnimation = withoutAnimation
      localStorage.setItem('sidebarStatus', '0')
    },

    // 设置设备类型
    setDevice(device) {
      this.device = device
    },

    // 切换主题
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', this.theme)
      
      // 更新HTML类名
      document.documentElement.className = this.theme
    },

    // 设置主题
    setTheme(theme) {
      this.theme = theme
      localStorage.setItem('theme', theme)
      document.documentElement.className = theme
    },

    // 设置语言
    setLanguage(language) {
      this.language = language
      localStorage.setItem('language', language)
    },

    // 设置加载状态
    setLoading(loading) {
      this.loading = loading
    },

    // 更新设置
    updateSettings(settings) {
      this.settings = { ...this.settings, ...settings }
      localStorage.setItem('appSettings', JSON.stringify(this.settings))
    },

    // 添加错误日志
    addErrorLog(errorInfo) {
      this.errorLogs.unshift({
        ...errorInfo,
        timestamp: new Date().toISOString(),
        id: Date.now()
      })
      
      // 只保留最近100条错误日志
      if (this.errorLogs.length > 100) {
        this.errorLogs = this.errorLogs.slice(0, 100)
      }
    },

    // 清除错误日志
    clearErrorLogs() {
      this.errorLogs = []
    },

    // 初始化应用状态
    initApp() {
      // 恢复侧边栏状态
      const sidebarStatus = localStorage.getItem('sidebarStatus')
      if (sidebarStatus) {
        this.sidebar.opened = sidebarStatus === '1'
      }

      // 恢复主题
      const theme = localStorage.getItem('theme')
      if (theme) {
        this.setTheme(theme)
      }

      // 恢复语言
      const language = localStorage.getItem('language')
      if (language) {
        this.language = language
      }

      // 恢复设置
      const settings = localStorage.getItem('appSettings')
      if (settings) {
        try {
          this.settings = { ...this.settings, ...JSON.parse(settings) }
        } catch (error) {
          console.warn('恢复应用设置失败:', error)
        }
      }

      // 检测设备类型
      this.checkDevice()
    },

    // 检测设备类型
    checkDevice() {
      const rect = document.body.getBoundingClientRect()
      const device = rect.width - 1 < 992 ? 'mobile' : 'desktop'
      this.setDevice(device)
    },

    // 处理窗口大小变化
    handleResize() {
      if (!document.hidden) {
        this.checkDevice()
        
        // 移动设备自动关闭侧边栏
        if (this.device === 'mobile' && this.sidebar.opened) {
          this.closeSidebar(true)
        }
      }
    }
  }
})
