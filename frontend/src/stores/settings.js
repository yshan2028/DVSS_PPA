import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    basicSettings: {
      systemName: 'DVSS-PPA系统',
      systemDescription: '基于区块链的数据分片与隐私保护系统',
      systemVersion: '1.0.0',
      adminEmail: '',
      timezone: 'Asia/Shanghai',
      language: 'zh-CN'
    },
    securitySettings: {
      passwordStrength: 'medium',
      loginFailLimit: 5,
      lockDuration: 30,
      sessionTimeout: 120,
      enableTwoFactor: false,
      enableIpWhitelist: false
    },
    dataSettings: {
      dataRetentionDays: 365,
      logRetentionDays: 30,
      enableBackup: true,
      backupInterval: 'weekly',
      backupRetention: 10,
      enableCompression: true
    },
    blockchainSettings: {
      networkType: 'development',
      consensusAlgorithm: 'solo',
      blockSizeLimit: 10,
      transactionTimeout: 30,
      enableTLS: false,
      chaincodeLogLevel: 'info'
    },
    sensitivitySettings: [
      {
        fieldName: 'name',
        fieldType: 'string',
        sensitivityLevel: 'medium',
        encryptionMethod: 'aes256',
        description: '用户姓名字段'
      },
      {
        fieldName: 'idCard',
        fieldType: 'idcard',
        sensitivityLevel: 'high',
        encryptionMethod: 'aes256',
        description: '身份证号码字段'
      }
    ],
    loading: false
  }),

  getters: {
    // 获取所有设置
    allSettings: (state) => ({
      basic: state.basicSettings,
      security: state.securitySettings,
      data: state.dataSettings,
      blockchain: state.blockchainSettings,
      sensitivity: state.sensitivitySettings
    }),
    
    // 获取系统基本信息
    systemInfo: (state) => ({
      name: state.basicSettings.systemName,
      version: state.basicSettings.systemVersion,
      description: state.basicSettings.systemDescription
    }),
    
    // 获取安全策略摘要
    securitySummary: (state) => ({
      passwordPolicy: state.securitySettings.passwordStrength,
      sessionTimeout: state.securitySettings.sessionTimeout,
      twoFactorEnabled: state.securitySettings.enableTwoFactor,
      ipWhitelistEnabled: state.securitySettings.enableIpWhitelist
    }),
    
    // 获取数据管理策略
    dataManagementPolicy: (state) => ({
      retention: state.dataSettings.dataRetentionDays,
      backupEnabled: state.dataSettings.enableBackup,
      backupInterval: state.dataSettings.backupInterval,
      compressionEnabled: state.dataSettings.enableCompression
    }),
    
    // 获取区块链网络配置
    networkConfig: (state) => ({
      type: state.blockchainSettings.networkType,
      consensus: state.blockchainSettings.consensusAlgorithm,
      tlsEnabled: state.blockchainSettings.enableTLS,
      blockSizeLimit: state.blockchainSettings.blockSizeLimit
    }),
    
    // 根据敏感度等级获取字段配置
    sensitiveFieldsByLevel: (state) => (level) => {
      return state.sensitivitySettings.filter(field => field.sensitivityLevel === level)
    },
    
    // 获取字段加密配置
    encryptionConfigByField: (state) => (fieldName) => {
      const config = state.sensitivitySettings.find(field => field.fieldName === fieldName)
      return config ? {
        method: config.encryptionMethod,
        level: config.sensitivityLevel
      } : null
    }
  },

  actions: {
    // 获取所有设置
    async getAllSettings() {
      this.loading = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 这里应该调用实际的API
        // const response = await settingsAPI.getAllSettings()
        // this.loadSettings(response.data)
        
        return {
          basic: this.basicSettings,
          security: this.securitySettings,
          data: this.dataSettings,
          blockchain: this.blockchainSettings,
          sensitivity: this.sensitivitySettings
        }
      } catch (error) {
        console.error('获取系统设置失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新基础设置
    async updateBasicSettings(settings) {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.updateBasicSettings(settings)
        
        this.basicSettings = { ...this.basicSettings, ...settings }
        return { success: true, message: '基础设置更新成功' }
      } catch (error) {
        console.error('更新基础设置失败:', error)
        throw error
      }
    },

    // 更新安全设置
    async updateSecuritySettings(settings) {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.updateSecuritySettings(settings)
        
        this.securitySettings = { ...this.securitySettings, ...settings }
        return { success: true, message: '安全设置更新成功' }
      } catch (error) {
        console.error('更新安全设置失败:', error)
        throw error
      }
    },

    // 更新数据设置
    async updateDataSettings(settings) {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.updateDataSettings(settings)
        
        this.dataSettings = { ...this.dataSettings, ...settings }
        return { success: true, message: '数据设置更新成功' }
      } catch (error) {
        console.error('更新数据设置失败:', error)
        throw error
      }
    },

    // 更新区块链设置
    async updateBlockchainSettings(settings) {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.updateBlockchainSettings(settings)
        
        this.blockchainSettings = { ...this.blockchainSettings, ...settings }
        return { success: true, message: '区块链设置更新成功' }
      } catch (error) {
        console.error('更新区块链设置失败:', error)
        throw error
      }
    },

    // 更新敏感度设置
    async updateSensitivitySettings(settings) {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.updateSensitivitySettings(settings)
        
        this.sensitivitySettings = [...settings]
        return { success: true, message: '敏感度设置更新成功' }
      } catch (error) {
        console.error('更新敏感度设置失败:', error)
        throw error
      }
    },

    // 立即备份
    async backupNow() {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.backupNow()
        
        // 模拟备份过程
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        return { success: true, message: '数据备份已启动' }
      } catch (error) {
        console.error('立即备份失败:', error)
        throw error
      }
    },

    // 重启网络
    async restartNetwork() {
      try {
        // 这里应该调用实际的API
        // const response = await settingsAPI.restartNetwork()
        
        // 模拟重启过程
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        return { success: true, message: '网络重启命令已发送' }
      } catch (error) {
        console.error('重启网络失败:', error)
        throw error
      }
    },

    // 重置设置到默认值
    resetToDefaults() {
      this.basicSettings = {
        systemName: 'DVSS-PPA系统',
        systemDescription: '基于区块链的数据分片与隐私保护系统',
        systemVersion: '1.0.0',
        adminEmail: '',
        timezone: 'Asia/Shanghai',
        language: 'zh-CN'
      }
      
      this.securitySettings = {
        passwordStrength: 'medium',
        loginFailLimit: 5,
        lockDuration: 30,
        sessionTimeout: 120,
        enableTwoFactor: false,
        enableIpWhitelist: false
      }
      
      this.dataSettings = {
        dataRetentionDays: 365,
        logRetentionDays: 30,
        enableBackup: true,
        backupInterval: 'weekly',
        backupRetention: 10,
        enableCompression: true
      }
      
      this.blockchainSettings = {
        networkType: 'development',
        consensusAlgorithm: 'solo',
        blockSizeLimit: 10,
        transactionTimeout: 30,
        enableTLS: false,
        chaincodeLogLevel: 'info'
      }
      
      this.sensitivitySettings = [
        {
          fieldName: 'name',
          fieldType: 'string',
          sensitivityLevel: 'medium',
          encryptionMethod: 'aes256',
          description: '用户姓名字段'
        }
      ]
    },

    // 加载设置数据
    loadSettings(settingsData) {
      if (settingsData.basic) {
        this.basicSettings = { ...this.basicSettings, ...settingsData.basic }
      }
      if (settingsData.security) {
        this.securitySettings = { ...this.securitySettings, ...settingsData.security }
      }
      if (settingsData.data) {
        this.dataSettings = { ...this.dataSettings, ...settingsData.data }
      }
      if (settingsData.blockchain) {
        this.blockchainSettings = { ...this.blockchainSettings, ...settingsData.blockchain }
      }
      if (settingsData.sensitivity) {
        this.sensitivitySettings = [...settingsData.sensitivity]
      }
    },

    // 验证设置配置
    validateSettings(settingsType, settings) {
      const validators = {
        basic: this.validateBasicSettings,
        security: this.validateSecuritySettings,
        data: this.validateDataSettings,
        blockchain: this.validateBlockchainSettings,
        sensitivity: this.validateSensitivitySettings
      }
      
      const validator = validators[settingsType]
      return validator ? validator(settings) : { valid: true }
    },

    // 验证基础设置
    validateBasicSettings(settings) {
      const errors = []
      
      if (!settings.systemName || settings.systemName.trim().length < 2) {
        errors.push('系统名称至少需要2个字符')
      }
      
      if (settings.adminEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(settings.adminEmail)) {
        errors.push('管理员邮箱格式不正确')
      }
      
      return {
        valid: errors.length === 0,
        errors
      }
    },

    // 验证安全设置
    validateSecuritySettings(settings) {
      const errors = []
      
      if (settings.loginFailLimit < 3 || settings.loginFailLimit > 10) {
        errors.push('登录失败限制次数应在3-10之间')
      }
      
      if (settings.lockDuration < 5 || settings.lockDuration > 1440) {
        errors.push('锁定时长应在5-1440分钟之间')
      }
      
      if (settings.sessionTimeout < 10 || settings.sessionTimeout > 480) {
        errors.push('会话超时时间应在10-480分钟之间')
      }
      
      return {
        valid: errors.length === 0,
        errors
      }
    },

    // 验证数据设置
    validateDataSettings(settings) {
      const errors = []
      
      if (settings.dataRetentionDays < 30 || settings.dataRetentionDays > 3650) {
        errors.push('数据保留期应在30-3650天之间')
      }
      
      if (settings.logRetentionDays < 7 || settings.logRetentionDays > 365) {
        errors.push('日志保留期应在7-365天之间')
      }
      
      if (settings.enableBackup && (!settings.backupRetention || settings.backupRetention < 1)) {
        errors.push('备份保留数量至少为1')
      }
      
      return {
        valid: errors.length === 0,
        errors
      }
    },

    // 验证区块链设置
    validateBlockchainSettings(settings) {
      const errors = []
      
      if (settings.blockSizeLimit < 1 || settings.blockSizeLimit > 100) {
        errors.push('区块大小限制应在1-100MB之间')
      }
      
      if (settings.transactionTimeout < 10 || settings.transactionTimeout > 300) {
        errors.push('交易超时时间应在10-300秒之间')
      }
      
      return {
        valid: errors.length === 0,
        errors
      }
    },

    // 验证敏感度设置
    validateSensitivitySettings(settings) {
      const errors = []
      
      if (!Array.isArray(settings)) {
        errors.push('敏感度设置必须是数组格式')
        return { valid: false, errors }
      }
      
      const fieldNames = new Set()
      settings.forEach((field, index) => {
        if (!field.fieldName || field.fieldName.trim().length === 0) {
          errors.push(`第${index + 1}项：字段名称不能为空`)
        } else if (fieldNames.has(field.fieldName)) {
          errors.push(`第${index + 1}项：字段名称"${field.fieldName}"重复`)
        } else {
          fieldNames.add(field.fieldName)
        }
        
        if (!field.fieldType) {
          errors.push(`第${index + 1}项：必须选择字段类型`)
        }
        
        if (!field.sensitivityLevel) {
          errors.push(`第${index + 1}项：必须选择敏感度等级`)
        }
        
        if (!field.encryptionMethod) {
          errors.push(`第${index + 1}项：必须选择加密方法`)
        }
      })
      
      return {
        valid: errors.length === 0,
        errors
      }
    },

    // 导出设置配置
    async exportSettings() {
      try {
        const settings = this.allSettings
        const dataStr = JSON.stringify(settings, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const url = window.URL.createObjectURL(dataBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = `dvss_settings_${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        return { success: true, message: '设置配置导出成功' }
      } catch (error) {
        console.error('导出设置失败:', error)
        throw error
      }
    },

    // 导入设置配置
    async importSettings(file) {
      try {
        const text = await file.text()
        const settings = JSON.parse(text)
        
        // 验证导入的设置
        const validationResults = []
        if (settings.basic) validationResults.push(this.validateSettings('basic', settings.basic))
        if (settings.security) validationResults.push(this.validateSettings('security', settings.security))
        if (settings.data) validationResults.push(this.validateSettings('data', settings.data))
        if (settings.blockchain) validationResults.push(this.validateSettings('blockchain', settings.blockchain))
        if (settings.sensitivity) validationResults.push(this.validateSettings('sensitivity', settings.sensitivity))
        
        const hasErrors = validationResults.some(result => !result.valid)
        if (hasErrors) {
          const allErrors = validationResults.flatMap(result => result.errors || [])
          throw new Error('导入的设置配置有误：' + allErrors.join('; '))
        }
        
        // 加载设置
        this.loadSettings(settings)
        
        return { success: true, message: '设置配置导入成功' }
      } catch (error) {
        console.error('导入设置失败:', error)
        throw error
      }
    }
  }
})
