<template>
  <div class="system-settings">
    <div class="page-header">
      <el-page-header>
        <template #content>
          <span class="text-large font-600 mr-3">系统设置</span>
        </template>
      </el-page-header>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane label="基本设置" name="basic">
        <el-card>
          <el-form :model="basicSettings" label-width="120px" class="settings-form">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input
                v-model="basicSettings.systemDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            <el-form-item label="系统版本">
              <el-input v-model="basicSettings.systemVersion" placeholder="如: v1.0.0" />
            </el-form-item>
            <el-form-item label="管理员邮箱">
              <el-input v-model="basicSettings.adminEmail" placeholder="请输入管理员邮箱" />
            </el-form-item>
            <el-form-item label="维护模式">
              <el-switch
                v-model="basicSettings.maintenanceMode"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="安全设置" name="security">
        <el-card>
          <el-form :model="securitySettings" label-width="120px" class="settings-form">
            <el-form-item label="登录超时">
              <el-select v-model="securitySettings.loginTimeout" placeholder="选择超时时间">
                <el-option label="30分钟" value="30" />
                <el-option label="1小时" value="60" />
                <el-option label="2小时" value="120" />
                <el-option label="8小时" value="480" />
              </el-select>
              <span class="form-help">用户无操作时自动登出的时间</span>
            </el-form-item>
            <el-form-item label="密码强度">
              <el-radio-group v-model="securitySettings.passwordStrength">
                <el-radio label="low">低 (6位以上)</el-radio>
                <el-radio label="medium">中 (8位+数字字母)</el-radio>
                <el-radio label="high">高 (8位+数字字母符号)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="登录失败限制">
              <el-input-number
                v-model="securitySettings.maxLoginAttempts"
                :min="3"
                :max="10"
              />
              <span class="form-help">连续登录失败次数限制</span>
            </el-form-item>
            <el-form-item label="双因子认证">
              <el-switch
                v-model="securitySettings.twoFactorAuth"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
            <el-form-item label="IP白名单">
              <el-input
                v-model="securitySettings.ipWhitelist"
                type="textarea"
                :rows="3"
                placeholder="每行一个IP地址或IP段，如: 192.168.1.0/24"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="隐私设置" name="privacy">
        <el-card>
          <el-form :model="privacySettings" label-width="150px" class="settings-form">
            <el-form-item label="默认隐私级别">
              <el-select v-model="privacySettings.defaultPrivacyLevel" placeholder="选择级别">
                <el-option label="公开" value="public" />
                <el-option label="部分可见" value="partial" />
                <el-option label="私有" value="private" />
                <el-option label="严格保密" value="confidential" />
              </el-select>
            </el-form-item>
            <el-form-item label="数据保留期限">
              <el-select v-model="privacySettings.dataRetentionPeriod" placeholder="选择期限">
                <el-option label="1年" value="1y" />
                <el-option label="3年" value="3y" />
                <el-option label="5年" value="5y" />
                <el-option label="永久" value="permanent" />
              </el-select>
            </el-form-item>
            <el-form-item label="自动匿名化">
              <el-switch
                v-model="privacySettings.autoAnonymization"
                active-text="启用"
                inactive-text="禁用"
              />
              <span class="form-help">过期数据自动进行匿名化处理</span>
            </el-form-item>
            <el-form-item label="可见字段配置">
              <div class="field-config">
                <div v-for="field in privacySettings.visibleFields" :key="field.name" class="field-item">
                  <span class="field-name">{{ field.label }}</span>
                  <el-select v-model="field.visibility" size="small">
                    <el-option label="所有用户可见" value="all" />
                    <el-option label="仅管理员可见" value="admin" />
                    <el-option label="相关角色可见" value="role" />
                    <el-option label="隐藏" value="hidden" />
                  </el-select>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="数据加密">
              <el-checkbox-group v-model="privacySettings.encryptionOptions">
                <el-checkbox label="database">数据库加密</el-checkbox>
                <el-checkbox label="transmission">传输加密</el-checkbox>
                <el-checkbox label="backup">备份加密</el-checkbox>
                <el-checkbox label="logs">日志加密</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="savePrivacySettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统监控" name="monitoring">
        <el-card>
          <el-form :model="monitoringSettings" label-width="120px" class="settings-form">
            <el-form-item label="性能监控">
              <el-switch
                v-model="monitoringSettings.performanceMonitoring"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
            <el-form-item label="错误日志级别">
              <el-select v-model="monitoringSettings.logLevel" placeholder="选择日志级别">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARN" value="warn" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            <el-form-item label="日志保留天数">
              <el-input-number
                v-model="monitoringSettings.logRetentionDays"
                :min="1"
                :max="365"
              />
            </el-form-item>
            <el-form-item label="性能阈值设置">
              <div class="threshold-config">
                <div class="threshold-item">
                  <span>响应时间警告(ms):</span>
                  <el-input-number v-model="monitoringSettings.thresholds.responseTime" :min="100" />
                </div>
                <div class="threshold-item">
                  <span>CPU使用率警告(%):</span>
                  <el-input-number v-model="monitoringSettings.thresholds.cpuUsage" :min="50" :max="100" />
                </div>
                <div class="threshold-item">
                  <span>内存使用率警告(%):</span>
                  <el-input-number v-model="monitoringSettings.thresholds.memoryUsage" :min="50" :max="100" />
                </div>
              </div>
            </el-form-item>
            <el-form-item label="报警通知">
              <el-checkbox-group v-model="monitoringSettings.alertMethods">
                <el-checkbox label="email">邮件</el-checkbox>
                <el-checkbox label="sms">短信</el-checkbox>
                <el-checkbox label="webhook">Webhook</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveMonitoringSettings" :loading="saving">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="备份恢复" name="backup">
        <el-card>
          <div class="backup-section">
            <el-form :model="backupSettings" label-width="120px" class="settings-form">
              <el-form-item label="自动备份">
                <el-switch
                  v-model="backupSettings.autoBackup"
                  active-text="启用"
                  inactive-text="禁用"
                />
              </el-form-item>
              <el-form-item label="备份频率">
                <el-select v-model="backupSettings.backupFrequency" placeholder="选择频率">
                  <el-option label="每天" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="每月" value="monthly" />
                </el-select>
              </el-form-item>
              <el-form-item label="备份保留数量">
                <el-input-number v-model="backupSettings.retentionCount" :min="1" :max="50" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBackupSettings" :loading="saving">
                  保存设置
                </el-button>
                <el-button type="success" @click="createBackup" :loading="backing">
                  立即备份
                </el-button>
              </el-form-item>
            </el-form>

            <el-divider />

            <div class="backup-list">
              <h4>备份记录</h4>
              <el-table :data="backupHistory" style="width: 100%">
                <el-table-column prop="filename" label="备份文件" />
                <el-table-column prop="size" label="文件大小" />
                <el-table-column prop="type" label="备份类型">
                  <template #default="{ row }">
                    <el-tag :type="row.type === 'auto' ? 'success' : 'primary'">
                      {{ row.type === 'auto' ? '自动' : '手动' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="createTime" label="创建时间" />
                <el-table-column label="操作" width="200">
                  <template #default="{ row }">
                    <el-button type="primary" text @click="downloadBackup(row)">
                      下载
                    </el-button>
                    <el-button type="warning" text @click="restoreBackup(row)">
                      恢复
                    </el-button>
                    <el-button type="danger" text @click="deleteBackup(row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const activeTab = ref('basic')
const saving = ref(false)
const backing = ref(false)

// 基本设置
const basicSettings = reactive({
  systemName: 'DVSS-PPA系统',
  systemDescription: '分布式可验证秘密共享隐私保护认证系统',
  systemVersion: 'v1.0.0',
  adminEmail: 'admin@dvss-ppa.com',
  maintenanceMode: false
})

// 安全设置
const securitySettings = reactive({
  loginTimeout: '60',
  passwordStrength: 'medium',
  maxLoginAttempts: 5,
  twoFactorAuth: false,
  ipWhitelist: ''
})

// 隐私设置
const privacySettings = reactive({
  defaultPrivacyLevel: 'partial',
  dataRetentionPeriod: '3y',
  autoAnonymization: true,
  visibleFields: [
    { name: 'name', label: '姓名', visibility: 'role' },
    { name: 'email', label: '邮箱', visibility: 'admin' },
    { name: 'phone', label: '电话', visibility: 'hidden' },
    { name: 'address', label: '地址', visibility: 'role' },
    { name: 'payment_info', label: '支付信息', visibility: 'hidden' }
  ],
  encryptionOptions: ['database', 'transmission']
})

// 监控设置
const monitoringSettings = reactive({
  performanceMonitoring: true,
  logLevel: 'info',
  logRetentionDays: 30,
  thresholds: {
    responseTime: 1000,
    cpuUsage: 80,
    memoryUsage: 85
  },
  alertMethods: ['email']
})

// 备份设置
const backupSettings = reactive({
  autoBackup: true,
  backupFrequency: 'daily',
  retentionCount: 10
})

// 备份历史
const backupHistory = ref([
  {
    id: 1,
    filename: 'backup_20240120_143000.sql',
    size: '45.2 MB',
    type: 'auto',
    createTime: '2024-01-20 14:30:00'
  },
  {
    id: 2,
    filename: 'backup_20240119_143000.sql',
    size: '44.8 MB',
    type: 'auto',
    createTime: '2024-01-19 14:30:00'
  }
])

// 方法
const saveBasicSettings = async () => {
  saving.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('基本设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const saveSecuritySettings = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('安全设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const savePrivacySettings = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('隐私设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const saveMonitoringSettings = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('监控设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const saveBackupSettings = async () => {
  saving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('备份设置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const createBackup = async () => {
  backing.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 3000))
    ElMessage.success('备份创建成功')
    // 刷新备份列表
  } catch (error) {
    ElMessage.error('备份创建失败')
  } finally {
    backing.value = false
  }
}

const downloadBackup = (backup) => {
  ElMessage.info(`下载备份: ${backup.filename}`)
}

const restoreBackup = (backup) => {
  ElMessageBox.confirm(`确定要恢复备份 ${backup.filename} 吗？此操作将覆盖当前数据。`, '确认恢复', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('备份恢复成功')
  })
}

const deleteBackup = (backup) => {
  ElMessageBox.confirm(`确定要删除备份 ${backup.filename} 吗？`, '确认删除', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('备份删除成功')
  })
}

onMounted(() => {
  // 初始化设置数据
})
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.settings-tabs {
  min-height: 600px;
}

.settings-form {
  max-width: 600px;
  padding: 20px;
}

.form-help {
  color: #999;
  font-size: 12px;
  margin-left: 10px;
}

.field-config {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

.field-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.field-item:last-child {
  margin-bottom: 0;
}

.field-name {
  font-weight: 500;
}

.threshold-config {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
}

.threshold-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.threshold-item:last-child {
  margin-bottom: 0;
}

.backup-section {
  padding: 20px;
}

.backup-list {
  margin-top: 20px;
}

.backup-list h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>
