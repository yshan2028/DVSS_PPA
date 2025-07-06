<template>
  <div class="system-settings">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基础配置 -->
      <el-tab-pane label="基础配置" name="basic">
        <el-card>
          <el-form
            ref="basicFormRef"
            :model="basicForm"
            :rules="basicRules"
            label-width="150px"
          >
            <el-form-item label="系统名称" prop="systemName">
              <el-input v-model="basicForm.systemName" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统描述" prop="systemDescription">
              <el-input
                v-model="basicForm.systemDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            <el-form-item label="系统版本" prop="systemVersion">
              <el-input v-model="basicForm.systemVersion" placeholder="请输入系统版本" readonly />
            </el-form-item>
            <el-form-item label="管理员邮箱" prop="adminEmail">
              <el-input v-model="basicForm.adminEmail" placeholder="请输入管理员邮箱" />
            </el-form-item>
            <el-form-item label="系统时区" prop="timezone">
              <el-select v-model="basicForm.timezone" placeholder="请选择时区">
                <el-option label="北京时间 (UTC+8)" value="Asia/Shanghai" />
                <el-option label="东京时间 (UTC+9)" value="Asia/Tokyo" />
                <el-option label="伦敦时间 (UTC+0)" value="Europe/London" />
                <el-option label="纽约时间 (UTC-5)" value="America/New_York" />
              </el-select>
            </el-form-item>
            <el-form-item label="系统语言" prop="language">
              <el-select v-model="basicForm.language" placeholder="请选择语言">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveBasic">保存配置</el-button>
              <el-button @click="handleResetBasic">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 安全配置 -->
      <el-tab-pane label="安全配置" name="security">
        <el-card>
          <el-form
            ref="securityFormRef"
            :model="securityForm"
            :rules="securityRules"
            label-width="150px"
          >
            <el-form-item label="密码强度" prop="passwordStrength">
              <el-radio-group v-model="securityForm.passwordStrength">
                <el-radio label="low">低（6位以上）</el-radio>
                <el-radio label="medium">中（8位以上，包含字母和数字）</el-radio>
                <el-radio label="high">高（8位以上，包含大小写字母、数字和特殊字符）</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="登录失败限制" prop="loginFailLimit">
              <el-input-number
                v-model="securityForm.loginFailLimit"
                :min="3"
                :max="10"
                placeholder="登录失败次数限制"
              />
              <span class="form-tip">连续登录失败达到此次数将锁定账户</span>
            </el-form-item>
            <el-form-item label="锁定时长（分钟）" prop="lockDuration">
              <el-input-number
                v-model="securityForm.lockDuration"
                :min="5"
                :max="1440"
                placeholder="账户锁定时长"
              />
            </el-form-item>
            <el-form-item label="会话超时（分钟）" prop="sessionTimeout">
              <el-input-number
                v-model="securityForm.sessionTimeout"
                :min="10"
                :max="480"
                placeholder="用户会话超时时间"
              />
            </el-form-item>
            <el-form-item label="启用两步验证" prop="enableTwoFactor">
              <el-switch v-model="securityForm.enableTwoFactor" />
              <span class="form-tip">启用后用户登录需要额外的验证步骤</span>
            </el-form-item>
            <el-form-item label="启用IP白名单" prop="enableIpWhitelist">
              <el-switch v-model="securityForm.enableIpWhitelist" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveSecurity">保存配置</el-button>
              <el-button @click="handleResetSecurity">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 数据配置 -->
      <el-tab-pane label="数据配置" name="data">
        <el-card>
          <el-form
            ref="dataFormRef"
            :model="dataForm"
            :rules="dataRules"
            label-width="150px"
          >
            <el-form-item label="数据保留期（天）" prop="dataRetentionDays">
              <el-input-number
                v-model="dataForm.dataRetentionDays"
                :min="30"
                :max="3650"
                placeholder="数据保留天数"
              />
              <span class="form-tip">超过此天数的数据将被自动清理</span>
            </el-form-item>
            <el-form-item label="日志保留期（天）" prop="logRetentionDays">
              <el-input-number
                v-model="dataForm.logRetentionDays"
                :min="7"
                :max="365"
                placeholder="日志保留天数"
              />
            </el-form-item>
            <el-form-item label="启用数据备份" prop="enableBackup">
              <el-switch v-model="dataForm.enableBackup" />
            </el-form-item>
            <el-form-item label="备份周期" prop="backupInterval" v-if="dataForm.enableBackup">
              <el-select v-model="dataForm.backupInterval" placeholder="请选择备份周期">
                <el-option label="每天" value="daily" />
                <el-option label="每周" value="weekly" />
                <el-option label="每月" value="monthly" />
              </el-select>
            </el-form-item>
            <el-form-item label="备份保留数量" prop="backupRetention" v-if="dataForm.enableBackup">
              <el-input-number
                v-model="dataForm.backupRetention"
                :min="1"
                :max="30"
                placeholder="备份文件保留数量"
              />
            </el-form-item>
            <el-form-item label="启用数据压缩" prop="enableCompression">
              <el-switch v-model="dataForm.enableCompression" />
              <span class="form-tip">启用后将压缩存储的数据以节省空间</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveData">保存配置</el-button>
              <el-button @click="handleResetData">重置</el-button>
              <el-button type="warning" @click="handleBackupNow" v-if="dataForm.enableBackup">
                立即备份
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 区块链配置 -->
      <el-tab-pane label="区块链配置" name="blockchain">
        <el-card>
          <el-form
            ref="blockchainFormRef"
            :model="blockchainForm"
            :rules="blockchainRules"
            label-width="150px"
          >
            <el-form-item label="网络类型" prop="networkType">
              <el-radio-group v-model="blockchainForm.networkType">
                <el-radio label="development">开发网络</el-radio>
                <el-radio label="testing">测试网络</el-radio>
                <el-radio label="production">生产网络</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="共识算法" prop="consensusAlgorithm">
              <el-select v-model="blockchainForm.consensusAlgorithm" placeholder="请选择共识算法">
                <el-option label="Solo" value="solo" />
                <el-option label="Kafka" value="kafka" />
                <el-option label="Raft" value="raft" />
              </el-select>
            </el-form-item>
            <el-form-item label="区块大小限制（MB）" prop="blockSizeLimit">
              <el-input-number
                v-model="blockchainForm.blockSizeLimit"
                :min="1"
                :max="100"
                placeholder="区块大小限制"
              />
            </el-form-item>
            <el-form-item label="交易超时（秒）" prop="transactionTimeout">
              <el-input-number
                v-model="blockchainForm.transactionTimeout"
                :min="10"
                :max="300"
                placeholder="交易超时时间"
              />
            </el-form-item>
            <el-form-item label="启用TLS" prop="enableTLS">
              <el-switch v-model="blockchainForm.enableTLS" />
            </el-form-item>
            <el-form-item label="链码日志级别" prop="chaincodeLogLevel">
              <el-select v-model="blockchainForm.chaincodeLogLevel" placeholder="请选择日志级别">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARN" value="warn" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveBlockchain">保存配置</el-button>
              <el-button @click="handleResetBlockchain">重置</el-button>
              <el-button type="warning" @click="handleRestartNetwork">重启网络</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 敏感度配置 -->
      <el-tab-pane label="敏感度配置" name="sensitivity">
        <el-card>
          <div class="sensitivity-header">
            <span>敏感字段配置</span>
            <el-button type="primary" size="small" @click="handleAddSensitivity">
              <el-icon><Plus /></el-icon>
              添加配置
            </el-button>
          </div>
          
          <el-table :data="sensitivityList" stripe border>
            <el-table-column prop="fieldName" label="字段名称" width="150" />
            <el-table-column prop="fieldType" label="字段类型" width="120" />
            <el-table-column prop="sensitivityLevel" label="敏感度等级" width="120">
              <template #default="{ row }">
                <el-tag :type="getSensitivityType(row.sensitivityLevel)" size="small">
                  {{ getSensitivityText(row.sensitivityLevel) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="encryptionMethod" label="加密方法" width="120" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column label="操作" width="150">
              <template #default="{ row, $index }">
                <el-button type="primary" size="small" @click="handleEditSensitivity(row, $index)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDeleteSensitivity($index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 敏感度配置对话框 -->
    <el-dialog
      v-model="sensitivityDialogVisible"
      :title="sensitivityDialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="sensitivityFormRef"
        :model="sensitivityForm"
        :rules="sensitivityFormRules"
        label-width="120px"
      >
        <el-form-item label="字段名称" prop="fieldName">
          <el-input v-model="sensitivityForm.fieldName" placeholder="请输入字段名称" />
        </el-form-item>
        <el-form-item label="字段类型" prop="fieldType">
          <el-select v-model="sensitivityForm.fieldType" placeholder="请选择字段类型">
            <el-option label="字符串" value="string" />
            <el-option label="数字" value="number" />
            <el-option label="日期" value="date" />
            <el-option label="邮箱" value="email" />
            <el-option label="电话" value="phone" />
            <el-option label="身份证" value="idcard" />
          </el-select>
        </el-form-item>
        <el-form-item label="敏感度等级" prop="sensitivityLevel">
          <el-select v-model="sensitivityForm.sensitivityLevel" placeholder="请选择敏感度等级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="极高" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="加密方法" prop="encryptionMethod">
          <el-select v-model="sensitivityForm.encryptionMethod" placeholder="请选择加密方法">
            <el-option label="AES-256" value="aes256" />
            <el-option label="DES" value="des" />
            <el-option label="RSA" value="rsa" />
            <el-option label="MD5哈希" value="md5" />
            <el-option label="SHA256哈希" value="sha256" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="sensitivityForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="sensitivityDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveSensitivity">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

// 响应式数据
const activeTab = ref('basic')
const sensitivityDialogVisible = ref(false)
const sensitivityDialogTitle = ref('添加敏感度配置')
const currentSensitivityIndex = ref(-1)

// 基础配置表单
const basicFormRef = ref()
const basicForm = reactive({
  systemName: 'DVSS-PPA系统',
  systemDescription: '基于区块链的数据分片与隐私保护系统',
  systemVersion: '1.0.0',
  adminEmail: '',
  timezone: 'Asia/Shanghai',
  language: 'zh-CN'
})

const basicRules = {
  systemName: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  adminEmail: [
    { required: true, message: '请输入管理员邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 安全配置表单
const securityFormRef = ref()
const securityForm = reactive({
  passwordStrength: 'medium',
  loginFailLimit: 5,
  lockDuration: 30,
  sessionTimeout: 120,
  enableTwoFactor: false,
  enableIpWhitelist: false
})

const securityRules = {
  passwordStrength: [{ required: true, message: '请选择密码强度', trigger: 'change' }],
  loginFailLimit: [{ required: true, message: '请设置登录失败限制', trigger: 'blur' }],
  lockDuration: [{ required: true, message: '请设置锁定时长', trigger: 'blur' }],
  sessionTimeout: [{ required: true, message: '请设置会话超时时间', trigger: 'blur' }]
}

// 数据配置表单
const dataFormRef = ref()
const dataForm = reactive({
  dataRetentionDays: 365,
  logRetentionDays: 30,
  enableBackup: true,
  backupInterval: 'weekly',
  backupRetention: 10,
  enableCompression: true
})

const dataRules = {
  dataRetentionDays: [{ required: true, message: '请设置数据保留期', trigger: 'blur' }],
  logRetentionDays: [{ required: true, message: '请设置日志保留期', trigger: 'blur' }]
}

// 区块链配置表单
const blockchainFormRef = ref()
const blockchainForm = reactive({
  networkType: 'development',
  consensusAlgorithm: 'solo',
  blockSizeLimit: 10,
  transactionTimeout: 30,
  enableTLS: false,
  chaincodeLogLevel: 'info'
})

const blockchainRules = {
  networkType: [{ required: true, message: '请选择网络类型', trigger: 'change' }],
  consensusAlgorithm: [{ required: true, message: '请选择共识算法', trigger: 'change' }]
}

// 敏感度配置
const sensitivityList = ref([
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
])

const sensitivityFormRef = ref()
const sensitivityForm = reactive({
  fieldName: '',
  fieldType: '',
  sensitivityLevel: '',
  encryptionMethod: '',
  description: ''
})

const sensitivityFormRules = {
  fieldName: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  fieldType: [{ required: true, message: '请选择字段类型', trigger: 'change' }],
  sensitivityLevel: [{ required: true, message: '请选择敏感度等级', trigger: 'change' }],
  encryptionMethod: [{ required: true, message: '请选择加密方法', trigger: 'change' }]
}

// 保存配置方法
const handleSaveBasic = async () => {
  try {
    await basicFormRef.value.validate()
    await settingsStore.updateBasicSettings(basicForm)
    ElMessage.success('基础配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const handleSaveSecurity = async () => {
  try {
    await securityFormRef.value.validate()
    await settingsStore.updateSecuritySettings(securityForm)
    ElMessage.success('安全配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const handleSaveData = async () => {
  try {
    await dataFormRef.value.validate()
    await settingsStore.updateDataSettings(dataForm)
    ElMessage.success('数据配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const handleSaveBlockchain = async () => {
  try {
    await blockchainFormRef.value.validate()
    await settingsStore.updateBlockchainSettings(blockchainForm)
    ElMessage.success('区块链配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

// 重置配置方法
const handleResetBasic = () => {
  basicFormRef.value.resetFields()
}

const handleResetSecurity = () => {
  securityFormRef.value.resetFields()
}

const handleResetData = () => {
  dataFormRef.value.resetFields()
}

const handleResetBlockchain = () => {
  blockchainFormRef.value.resetFields()
}

// 特殊操作
const handleBackupNow = async () => {
  try {
    await settingsStore.backupNow()
    ElMessage.success('备份任务已启动')
  } catch (error) {
    ElMessage.error('备份失败：' + error.message)
  }
}

const handleRestartNetwork = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重启区块链网络吗？此操作会暂时中断服务。',
      '确认重启',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await settingsStore.restartNetwork()
    ElMessage.success('网络重启命令已发送')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重启失败：' + error.message)
    }
  }
}

// 敏感度配置操作
const handleAddSensitivity = () => {
  sensitivityDialogTitle.value = '添加敏感度配置'
  currentSensitivityIndex.value = -1
  Object.assign(sensitivityForm, {
    fieldName: '',
    fieldType: '',
    sensitivityLevel: '',
    encryptionMethod: '',
    description: ''
  })
  sensitivityDialogVisible.value = true
}

const handleEditSensitivity = (row, index) => {
  sensitivityDialogTitle.value = '编辑敏感度配置'
  currentSensitivityIndex.value = index
  Object.assign(sensitivityForm, row)
  sensitivityDialogVisible.value = true
}

const handleSaveSensitivity = async () => {
  try {
    await sensitivityFormRef.value.validate()
    
    const newItem = { ...sensitivityForm }
    
    if (currentSensitivityIndex.value >= 0) {
      sensitivityList.value[currentSensitivityIndex.value] = newItem
    } else {
      sensitivityList.value.push(newItem)
    }
    
    await settingsStore.updateSensitivitySettings(sensitivityList.value)
    ElMessage.success('敏感度配置保存成功')
    sensitivityDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
  }
}

const handleDeleteSensitivity = async (index) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个敏感度配置吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    sensitivityList.value.splice(index, 1)
    await settingsStore.updateSensitivitySettings(sensitivityList.value)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

// 工具函数
const getSensitivityType = (level) => {
  const typeMap = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return typeMap[level] || 'info'
}

const getSensitivityText = (level) => {
  const textMap = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '极高'
  }
  return textMap[level] || level
}

// 生命周期
onMounted(async () => {
  try {
    const settings = await settingsStore.getAllSettings()
    if (settings.basic) Object.assign(basicForm, settings.basic)
    if (settings.security) Object.assign(securityForm, settings.security)
    if (settings.data) Object.assign(dataForm, settings.data)
    if (settings.blockchain) Object.assign(blockchainForm, settings.blockchain)
    if (settings.sensitivity) sensitivityList.value = settings.sensitivity
  } catch (error) {
    console.error('获取系统设置失败:', error)
  }
})
</script>

<style scoped>
.system-settings {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.settings-tabs {
  margin-top: 20px;
}

.form-tip {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.sensitivity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.dialog-footer {
  text-align: right;
}
</style>
