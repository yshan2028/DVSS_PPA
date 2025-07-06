<template>
  <el-card class="ls-formula-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon><Tools /></el-icon>
        <span>{{ t('formula.title') }}</span>
      </div>
    </template>

    <div class="formula-content">
      <!-- L值公式 -->
      <div class="formula-section">
        <h4 class="formula-title">
          <el-tag type="primary" size="large">L</el-tag>
          {{ t('formula.privacyLevel') }}
        </h4>
        <div class="formula-display">
          <el-card class="formula-card" shadow="never">
            <div class="formula-math">
              L = (Σ S<sub>i</sub> / n) × (A<sub>r</sub> / A<sub>total</sub>) × 10
            </div>
            <div class="formula-explanation">
              <p><strong>S<sub>i</sub></strong>: {{ t('formula.fieldSensitivity') }}</p>
              <p><strong>n</strong>: {{ t('formula.totalFields') }}</p>
              <p><strong>A<sub>r</sub></strong>: {{ t('formula.accessibleFields') }}</p>
              <p><strong>A<sub>total</sub></strong>: {{ t('formula.totalAccessible') }}</p>
            </div>
          </el-card>
        </div>
      </div>

      <!-- S值公式 -->
      <div class="formula-section">
        <h4 class="formula-title">
          <el-tag type="success" size="large">S</el-tag>
          {{ t('formula.securityLevel') }}
        </h4>
        <div class="formula-display">
          <el-card class="formula-card" shadow="never">
            <div class="formula-math">
              S = (t / n × 100) × R<sub>c</sub> × A<sub>c</sub>
            </div>
            <div class="formula-explanation">
              <p><strong>t</strong>: {{ t('formula.threshold') }}</p>
              <p><strong>n</strong>: {{ t('formula.totalShares') }}</p>
              <p><strong>R<sub>c</sub></strong>: {{ t('formula.roleCoefficient') }}</p>
              <p><strong>A<sub>c</sub></strong>: {{ t('formula.accessCoefficient') }}</p>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 实时计算示例 -->
      <div class="live-calculation" v-if="authStore.isLoggedIn">
        <h4>{{ t('formula.liveCalculation') }}</h4>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="calc-result l-value">
              <div class="calc-label">{{ t('formula.currentL') }}</div>
              <div class="calc-number">{{ currentLValue.toFixed(2) }}</div>
              <div class="calc-description">{{ getLValueDescription() }}</div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="calc-result s-value">
              <div class="calc-label">{{ t('formula.currentS') }}</div>
              <div class="calc-number">{{ currentSValue.toFixed(2) }}</div>
              <div class="calc-description">{{ getSValueDescription() }}</div>
            </div>
          </el-col>
        </el-row>

        <!-- 计算详情 -->
        <el-collapse class="calc-details">
          <el-collapse-item :title="t('formula.calculationDetails')" name="details">
            <div class="detail-row">
              <span>{{ t('formula.userRole') }}:</span>
              <el-tag :type="getRoleTagType(authStore.currentUser?.role)">
                {{ getRoleLabel(authStore.currentUser?.role) }}
              </el-tag>
            </div>
            <div class="detail-row">
              <span>{{ t('formula.accessibleFieldCount') }}:</span>
              <strong>{{ accessibleFieldsCount }} / {{ totalFieldsCount }}</strong>
            </div>
            <div class="detail-row">
              <span>{{ t('formula.averageSensitivity') }}:</span>
              <strong>{{ averageSensitivity.toFixed(2) }}</strong>
            </div>
            <div class="detail-row">
              <span>{{ t('formula.roleCoefficient') }}:</span>
              <strong>{{ roleCoefficient }}</strong>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18nStore } from '@/stores/i18n'
import { Tools } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = i18nStore

// 字段敏感度配置
const fieldSensitivity = {
  customer_name: 3,
  customer_phone: 4,
  payment_amount: 5,
  bank_card_number: 5,
  delivery_address: 3,
  identity_card: 5
}

// 角色系数配置
const roleCoefficients = {
  seller: 0.8,
  payment_provider: 1.0,
  logistics: 0.7,
  auditor: 1.2,
  platform: 1.5
}

// 角色权限映射
const rolePermissions = {
  seller: ['customer_name', 'customer_phone', 'delivery_address'],
  payment_provider: ['payment_amount', 'bank_card_number'],
  logistics: ['customer_phone', 'delivery_address'],
  auditor: ['customer_name', 'payment_amount', 'identity_card'],
  platform: ['customer_name', 'payment_amount']
}

const totalFieldsCount = Object.keys(fieldSensitivity).length

const accessibleFieldsCount = computed(() => {
  if (!authStore.currentUser?.role) return 0
  const permissions = rolePermissions[authStore.currentUser.role] || []
  return permissions.length
})

const averageSensitivity = computed(() => {
  if (!authStore.currentUser?.role) return 0
  const permissions = rolePermissions[authStore.currentUser.role] || []
  if (permissions.length === 0) return 0
  
  const totalSensitivity = permissions.reduce((sum, field) => {
    return sum + (fieldSensitivity[field] || 0)
  }, 0)
  
  return totalSensitivity / permissions.length
})

const roleCoefficient = computed(() => {
  if (!authStore.currentUser?.role) return 1
  return roleCoefficients[authStore.currentUser.role] || 1
})

// L值计算
const currentLValue = computed(() => {
  if (!authStore.currentUser?.role) return 0
  
  const avgSensitivity = averageSensitivity.value
  const accessRatio = accessibleFieldsCount.value / totalFieldsCount
  
  return avgSensitivity * accessRatio * 10
})

// S值计算 (简化版本，实际项目中应该从加密参数获取)
const currentSValue = computed(() => {
  if (!authStore.currentUser?.role) return 0
  
  const threshold = 3  // 默认门限值
  const totalShares = 5  // 默认分片数
  const thresholdRatio = (threshold / totalShares) * 100
  const roleFactor = roleCoefficient.value
  const accessFactor = 1.0  // 访问系数
  
  return thresholdRatio * roleFactor * accessFactor
})

const getRoleTagType = (role) => {
  const types = {
    seller: 'primary',
    payment_provider: 'success',
    logistics: 'warning',
    auditor: 'danger',
    platform: 'info'
  }
  return types[role] || 'default'
}

const getRoleLabel = (role) => {
  const labels = {
    seller: t('roles.seller'),
    payment_provider: t('roles.payment'),
    logistics: t('roles.logistics'),
    auditor: t('roles.auditor'),
    platform: t('roles.platform')
  }
  return labels[role] || role
}

const getLValueDescription = () => {
  const lValue = currentLValue.value
  if (lValue >= 8) return t('formula.highPrivacy')
  if (lValue >= 5) return t('formula.mediumPrivacy')
  return t('formula.lowPrivacy')
}

const getSValueDescription = () => {
  const sValue = currentSValue.value
  if (sValue >= 80) return t('formula.highSecurity')
  if (sValue >= 50) return t('formula.mediumSecurity')
  return t('formula.lowSecurity')
}
</script>

<style scoped>
.ls-formula-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.formula-content {
  padding: 10px 0;
}

.formula-section {
  margin-bottom: 30px;
}

.formula-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  color: #303133;
}

.formula-card {
  background: #F8F9FA;
  border: 1px solid #E4E7ED;
}

.formula-math {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 15px;
}

.formula-explanation {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.formula-explanation p {
  margin: 0;
  padding: 8px;
  background: #F0F2F5;
  border-radius: 4px;
  font-size: 14px;
}

.live-calculation {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.live-calculation h4 {
  margin-bottom: 20px;
  color: #303133;
}

.calc-result {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(103, 194, 58, 0.1));
}

.calc-result.l-value {
  border-left: 4px solid #409EFF;
}

.calc-result.s-value {
  border-left: 4px solid #67C23A;
}

.calc-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.calc-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.l-value .calc-number {
  color: #409EFF;
}

.s-value .calc-number {
  color: #67C23A;
}

.calc-description {
  font-size: 12px;
  color: #909399;
}

.calc-details {
  margin-top: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #F0F2F5;
}

.detail-row:last-child {
  border-bottom: none;
}
</style>
