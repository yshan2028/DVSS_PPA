<template>
  <div class="home-page">
    <!-- 头部横幅 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">DVSS-PPA 数据验证与安全系统</h1>
        <p class="hero-subtitle">
          基于区块链的隐私保护数据分析平台，提供安全可靠的数据处理和验证服务
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/public/query')">
            <el-icon><Search /></el-icon>
            开始查询
          </el-button>
          <el-button size="large" @click="$router.push('/public/encrypt')">
            <el-icon><Lock /></el-icon>
            数据加密
          </el-button>
        </div>
      </div>
      <div class="hero-image">
        <el-image 
          src="/images/hero-banner.svg" 
          alt="DVSS-PPA" 
          fit="contain"
          style="width: 100%; height: 400px;"
        />
      </div>
    </section>

    <!-- 功能特色 -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <el-row :gutter="30">
          <el-col :span="8" v-for="feature in features" :key="feature.id">
            <el-card class="feature-card" shadow="hover">
              <div class="feature-icon">
                <el-icon :size="48" :color="feature.color">
                  <component :is="feature.icon" />
                </el-icon>
              </div>
              <h3 class="feature-title">{{ feature.title }}</h3>
              <p class="feature-description">{{ feature.description }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 数据统计 -->
    <section class="stats-section">
      <div class="container">
        <h2 class="section-title">平台数据</h2>
        <el-row :gutter="20">
          <el-col :span="6" v-for="stat in stats" :key="stat.key">
            <div class="stat-item">
              <div class="stat-number">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 工作流程 -->
    <section class="workflow-section">
      <div class="container">
        <h2 class="section-title">工作流程</h2>
        <div class="workflow-steps">
          <div 
            class="workflow-step" 
            v-for="(step, index) in workflowSteps" 
            :key="step.id"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h4 class="step-title">{{ step.title }}</h4>
              <p class="step-description">{{ step.description }}</p>
            </div>
            <div class="step-arrow" v-if="index < workflowSteps.length - 1">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 技术优势 -->
    <section class="advantages-section">
      <div class="container">
        <h2 class="section-title">技术优势</h2>
        <el-row :gutter="40">
          <el-col :span="12">
            <div class="advantage-content">
              <h3>区块链技术保障</h3>
              <ul class="advantage-list">
                <li>不可篡改的数据记录</li>
                <li>分布式存储确保安全</li>
                <li>智能合约自动执行</li>
                <li>透明可追溯的操作历史</li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="advantage-content">
              <h3>隐私保护算法</h3>
              <ul class="advantage-list">
                <li>先进的加密算法</li>
                <li>多重分片技术</li>
                <li>差分隐私保护</li>
                <li>零知识证明验证</li>
              </ul>
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 快速开始 -->
    <section class="quick-start-section">
      <div class="container">
        <div class="quick-start-content">
          <h2>准备开始使用？</h2>
          <p>立即体验我们的数据验证与安全服务</p>
          <div class="quick-start-actions">
            <el-button type="primary" size="large" @click="$router.push('/public/register')">
              立即注册
            </el-button>
            <el-button type="default" size="large" @click="$router.push('/public/about')">
              了解更多
            </el-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Search, 
  Lock, 
  Shield, 
  DataAnalysis, 
  Connection,
  ArrowRight 
} from '@element-plus/icons-vue'

const features = ref([
  {
    id: 1,
    title: '数据加密',
    description: '采用多种先进加密算法，确保数据传输和存储的安全性',
    icon: Lock,
    color: '#409EFF'
  },
  {
    id: 2,
    title: '隐私保护',
    description: '基于差分隐私和零知识证明技术，保护用户隐私数据',
    icon: Shield,
    color: '#67C23A'
  },
  {
    id: 3,
    title: '数据分析',
    description: '提供安全的数据分析服务，在保护隐私的前提下获得洞察',
    icon: DataAnalysis,
    color: '#E6A23C'
  },
  {
    id: 4,
    title: '区块链验证',
    description: '利用区块链技术确保数据的不可篡改性和可追溯性',
    icon: Connection,
    color: '#F56C6C'
  },
  {
    id: 5,
    title: '分片存储',
    description: '将数据分片存储，提高安全性和可用性',
    icon: 'Grid',
    color: '#909399'
  },
  {
    id: 6,
    title: '智能合约',
    description: '自动化执行数据处理流程，确保操作的透明和可信',
    icon: 'MagicStick',
    color: '#606266'
  }
])

const stats = ref([
  { key: 'orders', label: '处理订单', value: '10,000+' },
  { key: 'users', label: '活跃用户', value: '1,000+' },
  { key: 'encrypted', label: '加密数据', value: '50TB+' },
  { key: 'nodes', label: '网络节点', value: '100+' }
])

const workflowSteps = ref([
  {
    id: 1,
    title: '数据上传',
    description: '用户将需要处理的数据上传到系统'
  },
  {
    id: 2,
    title: '敏感度分析',
    description: '系统自动分析数据的敏感度级别'
  },
  {
    id: 3,
    title: '加密处理',
    description: '根据敏感度选择合适的加密算法'
  },
  {
    id: 4,
    title: '分片存储',
    description: '将加密数据分片存储到区块链网络'
  },
  {
    id: 5,
    title: '验证分析',
    description: '在保护隐私的前提下进行数据分析'
  }
])

const loadStats = async () => {
  try {
    // 这里可以调用API获取实时统计数据
    // const response = await api.getPublicStats()
    // if (response.code === 200) {
    //   stats.value = response.data
    // }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

/* 头部横幅 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
  display: flex;
  align-items: center;
  min-height: 500px;
}

.hero-content {
  flex: 1;
  color: white;
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  line-height: 1.6;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 20px;
}

.hero-image {
  flex: 1;
  max-width: 500px;
  margin: 0 auto;
}

/* 功能特色 */
.features-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 60px;
  color: #303133;
}

.feature-card {
  text-align: center;
  padding: 40px 20px;
  height: 100%;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  margin-bottom: 24px;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.feature-description {
  color: #606266;
  line-height: 1.6;
}

/* 数据统计 */
.stats-section {
  padding: 80px 20px;
  background: white;
}

.stat-item {
  text-align: center;
  padding: 30px;
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 1.1rem;
  color: #606266;
}

/* 工作流程 */
.workflow-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.workflow-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1000px;
  margin: 0 auto;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.step-number {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.step-content {
  text-align: center;
}

.step-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: #303133;
}

.step-description {
  color: #606266;
  line-height: 1.5;
}

.step-arrow {
  position: absolute;
  right: -30px;
  top: 30px;
  color: #409EFF;
  font-size: 1.5rem;
}

/* 技术优势 */
.advantages-section {
  padding: 80px 20px;
  background: white;
}

.advantage-content h3 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 30px;
  color: #303133;
}

.advantage-list {
  list-style: none;
  padding: 0;
}

.advantage-list li {
  padding: 12px 0;
  padding-left: 30px;
  position: relative;
  color: #606266;
  line-height: 1.6;
}

.advantage-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67C23A;
  font-weight: bold;
  font-size: 1.2rem;
}

/* 快速开始 */
.quick-start-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  text-align: center;
}

.quick-start-content {
  color: white;
}

.quick-start-content h2 {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.quick-start-content p {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.quick-start-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .workflow-steps {
    flex-direction: column;
    gap: 40px;
  }
  
  .step-arrow {
    display: none;
  }
  
  .quick-start-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
