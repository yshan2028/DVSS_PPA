import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useI18nStore = defineStore('i18n', () => {
  const currentLanguage = ref(localStorage.getItem('dvss-lang') || 'zh')

  const translations = ref({
    zh: {
      nav: {
        title: 'DVSS-PPA 隐私保护系统',
        dashboard: '控制台',
        encrypt: '数据加密',
        query: '数据查询',
        monitoring: '系统监控',
        blockchain: '区块链记录',
        analytics: '数据分析'
      },
      auth: {
        title: '角色登录',
        login: '登录',
        logout: '退出',
        selectRole: '选择用户角色',
        rolePlaceholder: '请选择角色',
        username: '用户名',
        usernamePlaceholder: '请输入用户名',
        currentUser: '当前用户',
        notLoggedIn: '未登录',
        rolePermissions: '角色权限',
        fillRequired: '请填写所有必填项',
        loginSuccess: '登录成功',
        loginFailed: '登录失败'
      },
      roles: {
        seller: '卖家',
        payment: '支付服务商',
        logistics: '物流公司',
        auditor: '审计机构',
        platform: '平台管理员'
      },
      overview: {
        systemStatus: '系统状态',
        online: '正常运行',
        totalRecords: '总记录数',
        today: '今日新增',
        performanceChart: '性能监控',
        roleDistribution: '角色分布',
        cpuUsage: 'CPU使用率',
        memoryUsage: '内存使用率'
      },
      formula: {
        title: 'L/S 值计算公式',
        privacyLevel: '隐私保护级别',
        securityLevel: '安全保护级别',
        fieldSensitivity: '字段敏感度',
        totalFields: '总字段数',
        accessibleFields: '可访问字段数',
        totalAccessible: '总可访问数',
        threshold: '门限值',
        totalShares: '总分片数',
        roleCoefficient: '角色系数',
        accessCoefficient: '访问系数',
        liveCalculation: '实时计算',
        currentL: '当前L值',
        currentS: '当前S值',
        calculationDetails: '计算详情',
        userRole: '用户角色',
        accessibleFieldCount: '可访问字段数量',
        averageSensitivity: '平均敏感度',
        highPrivacy: '高隐私保护',
        mediumPrivacy: '中等隐私保护',
        lowPrivacy: '低隐私保护',
        highSecurity: '高安全级别',
        mediumSecurity: '中等安全级别',
        lowSecurity: '低安全级别'
      },
      actions: {
        title: '快速操作',
        encrypt: '数据加密',
        query: '数据查询',
        monitor: '系统监控',
        blockchain: '区块链',
        totalEncryptions: '总加密次数',
        totalQueries: '总查询次数',
        activeUsers: '活跃用户',
        uptime: '运行时间'
      },
      encrypt: {
        title: '数据加密',
        description: '使用DVSS-PPA算法对敏感数据进行加密分片处理',
        dataInput: '数据输入',
        parameters: '加密参数',
        customerName: '客户姓名',
        customerPhone: '客户电话',
        paymentAmount: '支付金额',
        bankCard: '银行卡号',
        deliveryAddress: '配送地址',
        identityCard: '身份证号',
        threshold: '门限值',
        totalShares: '总分片数',
        executeEncrypt: '执行加密分片',
        livePreview: '实时预览',
        privacyLevel: '隐私级别',
        securityLevel: '安全级别',
        result: '加密结果',
        dataId: '数据ID',
        blockchainHash: '区块链哈希',
        lValue: 'L值',
        sValue: 'S值',
        copyId: '复制ID',
        queryData: '查询数据',
        reset: '重置',
        success: '加密成功',
        failed: '加密失败',
        idCopied: 'ID已复制到剪贴板'
      },
      query: {
        title: '数据查询',
        description: '根据角色权限查询和解密数据，展示RBAC访问控制效果',
        dataQuery: '数据查询',
        dataId: '数据ID',
        enterDataId: '请输入数据ID',
        execute: '执行查询',
        currentUser: '当前用户',
        roleDescription: '角色',
        result: '查询结果',
        dataFields: '数据字段',
        noAccess: '无访问权限',
        privacyAnalysis: '隐私分析',
        accessibleFields: '可访问字段',
        privacyLevel: '隐私级别',
        securityLevel: '安全级别',
        blockchainRecord: '区块链记录',
        hash: '哈希值',
        timestamp: '时间戳',
        export: '导出结果',
        queryAnother: '查询其他',
        history: '查询历史',
        status: '状态',
        actions: '操作',
        requery: '重新查询',
        success: '查询成功',
        failed: '查询失败',
        exported: '结果已导出',
        customerName: '客户姓名',
        customerPhone: '客户电话',
        paymentAmount: '支付金额',
        bankCard: '银行卡号',
        deliveryAddress: '配送地址',
        identityCard: '身份证号'
      },
      monitoring: {
        title: '系统监控',
        dataRecords: '数据记录',
        encryptedShards: '加密分片',
        blockchainRecords: '区块链记录',
        activeUsers: '活跃用户',
        cpuUsage: 'CPU 使用率',
        memoryUsage: '内存使用率',
        avgLatency: '平均延迟'
      }
    },
    en: {
      nav: {
        title: 'DVSS-PPA Privacy Protection Framework',
        dashboard: 'Dashboard',
        encryption: 'Encryption',
        blockchain: 'Blockchain',
        monitoring: 'Monitoring'
      },
      auth: {
        login: 'Login',
        logout: 'Logout',
        selectRole: 'Select Role',
        currentUser: 'Current User',
        notLoggedIn: 'Not Logged In'
      },
      encryption: {
        title: 'Data Encryption Demo',
        inputData: 'Input Data',
        threshold: 'Threshold',
        shares: 'Shares',
        encrypt: 'Encrypt',
        success: 'Encryption Successful',
        dataId: 'Data ID',
        lValue: 'L-Value (Privacy Level)',
        sValue: 'S-Value (Security Level)'
      },
      decryption: {
        title: 'Data Decryption Demo',
        queryId: 'Query ID',
        decrypt: 'Decrypt Data',
        success: 'Decryption Successful',
        accessibleFields: 'Accessible Fields',
        restrictedFields: 'Restricted Fields'
      },
      blockchain: {
        title: 'Blockchain Records',
        blockNumber: 'Block Number',
        txHash: 'Transaction Hash',
        operation: 'Operation',
        timestamp: 'Timestamp'
      },
      monitoring: {
        title: 'System Monitoring',
        dataRecords: 'Data Records',
        encryptedShards: 'Encrypted Shards',
        blockchainRecords: 'Blockchain Records',
        activeUsers: 'Active Users',
        cpuUsage: 'CPU Usage',
        memoryUsage: 'Memory Usage',
        avgLatency: 'Average Latency'
      }
    }
  })

  const setLanguage = (lang) => {
    currentLanguage.value = lang
    localStorage.setItem('dvss-lang', lang)
  }

  const t = (key) => {
    const keys = key.split('.')
    let value = translations.value[currentLanguage.value]
    for (const k of keys) {
      value = value?.[k]
    }
    return value || key
  }

  return {
    currentLanguage,
    translations,
    setLanguage,
    t
  }
})
