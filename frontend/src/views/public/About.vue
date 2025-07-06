<template>
  <div class="about-page">
    <!-- 头部介绍 -->
    <section class="hero-section">
      <div class="container">
        <h1 class="hero-title">关于 DVSS-PPA</h1>
        <p class="hero-subtitle">
          基于区块链的隐私保护数据分析平台，致力于为用户提供安全、可靠的数据处理和验证服务
        </p>
      </div>
    </section>

    <!-- 产品介绍 -->
    <section class="product-intro">
      <div class="container">
        <el-row :gutter="40">
          <el-col :span="12">
            <div class="intro-content">
              <h2>产品简介</h2>
              <p>
                DVSS-PPA（Data Validation and Security System - Privacy Preserving Analysis）
                是一个创新的数据安全平台，结合了区块链技术、密码学、隐私计算等先进技术，
                为企业和个人提供全面的数据保护解决方案。
              </p>
              <p>
                我们的平台不仅能够确保数据的安全性和隐私性，还能在保护隐私的前提下实现数据的有效分析和利用，
                为数字化时代的数据安全提供强有力的技术保障。
              </p>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="intro-image">
              <el-image 
                src="/images/about-intro.svg" 
                alt="产品介绍" 
                fit="contain"
                style="width: 100%; height: 300px;"
              />
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 核心技术 -->
    <section class="technology-section">
      <div class="container">
        <h2 class="section-title">核心技术</h2>
        <el-row :gutter="30">
          <el-col :span="8" v-for="tech in technologies" :key="tech.id">
            <el-card class="tech-card" shadow="hover">
              <div class="tech-icon">
                <el-icon :size="48" :color="tech.color">
                  <component :is="tech.icon" />
                </el-icon>
              </div>
              <h3 class="tech-title">{{ tech.title }}</h3>
              <p class="tech-description">{{ tech.description }}</p>
              <ul class="tech-features">
                <li v-for="feature in tech.features" :key="feature">{{ feature }}</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 应用场景 -->
    <section class="scenarios-section">
      <div class="container">
        <h2 class="section-title">应用场景</h2>
        <div class="scenarios-grid">
          <div 
            class="scenario-item" 
            v-for="scenario in scenarios" 
            :key="scenario.id"
          >
            <div class="scenario-icon">
              <el-icon :size="40" :color="scenario.color">
                <component :is="scenario.icon" />
              </el-icon>
            </div>
            <h3 class="scenario-title">{{ scenario.title }}</h3>
            <p class="scenario-description">{{ scenario.description }}</p>
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
            <div class="advantage-card">
              <h3>安全性保障</h3>
              <ul class="advantage-list">
                <li>端到端加密，确保数据传输安全</li>
                <li>多重密钥管理，防止单点故障</li>
                <li>区块链不可篡改特性，保证数据完整性</li>
                <li>智能合约自动执行，减少人为风险</li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="advantage-card">
              <h3>隐私保护</h3>
              <ul class="advantage-list">
                <li>差分隐私算法，保护个人信息</li>
                <li>零知识证明，验证无需暴露数据</li>
                <li>同态加密，支持密文计算</li>
                <li>安全多方计算，多方协作保护隐私</li>
              </ul>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="40" style="margin-top: 30px">
          <el-col :span="12">
            <div class="advantage-card">
              <h3>高性能</h3>
              <ul class="advantage-list">
                <li>分布式架构，支持高并发处理</li>
                <li>智能分片技术，提升处理效率</li>
                <li>缓存优化，减少重复计算</li>
                <li>负载均衡，确保系统稳定性</li>
              </ul>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="advantage-card">
              <h3>易用性</h3>
              <ul class="advantage-list">
                <li>直观的用户界面，简化操作流程</li>
                <li>丰富的API接口，支持系统集成</li>
                <li>详细的文档说明，降低使用门槛</li>
                <li>7x24小时技术支持</li>
              </ul>
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 团队介绍 -->
    <section class="team-section">
      <div class="container">
        <h2 class="section-title">团队介绍</h2>
        <div class="team-intro">
          <p>
            我们是一支由密码学专家、区块链开发者、数据科学家和安全工程师组成的专业团队。
            团队成员拥有丰富的技术背景和实战经验，致力于推动数据安全技术的创新与发展。
          </p>
        </div>
        <el-row :gutter="30">
          <el-col :span="8" v-for="member in teamMembers" :key="member.id">
            <el-card class="member-card" shadow="hover">
              <div class="member-avatar">
                <el-avatar :size="80" :src="member.avatar" />
              </div>
              <h3 class="member-name">{{ member.name }}</h3>
              <p class="member-title">{{ member.title }}</p>
              <p class="member-description">{{ member.description }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- 发展历程 -->
    <section class="timeline-section">
      <div class="container">
        <h2 class="section-title">发展历程</h2>
        <div class="timeline">
          <div 
            class="timeline-item" 
            v-for="milestone in milestones" 
            :key="milestone.id"
          >
            <div class="timeline-marker"></div>
            <div class="timeline-content">
              <div class="timeline-date">{{ milestone.date }}</div>
              <h3 class="timeline-title">{{ milestone.title }}</h3>
              <p class="timeline-description">{{ milestone.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 联系我们 -->
    <section class="contact-section">
      <div class="container">
        <div class="contact-content">
          <h2>联系我们</h2>
          <p>如果您对我们的产品和服务感兴趣，欢迎随时与我们联系</p>
          <div class="contact-actions">
            <el-button type="primary" size="large" @click="$router.push('/public/contact')">
              立即联系
            </el-button>
            <el-button size="large" @click="$router.push('/public/home')">
              返回首页
            </el-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  Shield, 
  Lock, 
  Connection,
  DataAnalysis,
  OfficeBuilding,
  Suitcase,
  DocumentCheck,
  CreditCard
} from '@element-plus/icons-vue'

const technologies = ref([
  {
    id: 1,
    title: '区块链技术',
    description: '基于以太坊和Hyperledger Fabric构建的安全可靠的分布式账本',
    icon: Connection,
    color: '#409EFF',
    features: [
      '不可篡改的数据记录',
      '去中心化存储',
      '智能合约自动执行',
      '透明可追溯'
    ]
  },
  {
    id: 2,
    title: '密码学算法',
    description: '采用国际先进的密码学算法，确保数据加密和隐私保护',
    icon: Lock,
    color: '#67C23A',
    features: [
      'AES-256 对称加密',
      'RSA-2048 非对称加密',
      '椭圆曲线密码学',
      '量子抗性算法'
    ]
  },
  {
    id: 3,
    title: '隐私计算',
    description: '先进的隐私保护技术，在保护数据隐私的同时实现数据价值挖掘',
    icon: Shield,
    color: '#E6A23C',
    features: [
      '差分隐私算法',
      '零知识证明',
      '同态加密计算',
      '安全多方计算'
    ]
  }
])

const scenarios = ref([
  {
    id: 1,
    title: '金融行业',
    description: '银行、保险等金融机构的敏感数据保护和合规性要求',
    icon: CreditCard,
    color: '#409EFF'
  },
  {
    id: 2,
    title: '医疗健康',
    description: '患者隐私数据保护和医疗数据安全共享',
    icon: DocumentCheck,
    color: '#67C23A'
  },
  {
    id: 3,
    title: '政府机构',
    description: '政务数据安全管理和公民隐私保护',
    icon: OfficeBuilding,
    color: '#E6A23C'
  },
  {
    id: 4,
    title: '企业服务',
    description: '企业内部数据安全管理和商业机密保护',
    icon: Suitcase,
    color: '#F56C6C'
  }
])

const teamMembers = ref([
  {
    id: 1,
    name: '张博士',
    title: '首席技术官',
    description: '密码学博士，15年信息安全领域经验，区块链技术专家',
    avatar: '/images/avatar1.jpg'
  },
  {
    id: 2,
    name: '李工程师',
    title: '架构师',
    description: '分布式系统专家，曾就职于知名互联网公司，负责大规模系统设计',
    avatar: '/images/avatar2.jpg'
  },
  {
    id: 3,
    name: '王研究员',
    title: '算法专家',
    description: '隐私计算领域资深研究员，在顶级会议发表多篇学术论文',
    avatar: '/images/avatar3.jpg'
  }
])

const milestones = ref([
  {
    id: 1,
    date: '2022年3月',
    title: '项目启动',
    description: '团队成立，开始DVSS-PPA项目的研发工作'
  },
  {
    id: 2,
    date: '2022年8月',
    title: '核心算法完成',
    description: '完成隐私保护算法和区块链集成的核心技术开发'
  },
  {
    id: 3,
    date: '2023年2月',
    title: '测试版发布',
    description: '发布首个测试版本，开始内部测试和优化'
  },
  {
    id: 4,
    date: '2023年9月',
    title: '正式上线',
    description: '平台正式上线，开始为用户提供数据安全服务'
  },
  {
    id: 5,
    date: '2024年1月',
    title: '版本升级',
    description: '发布2.0版本，新增更多隐私保护功能'
  }
])
</script>

<style scoped>
.about-page {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 头部介绍 */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 80px 20px;
  text-align: center;
  color: white;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 1.2rem;
  line-height: 1.6;
  opacity: 0.9;
  max-width: 800px;
  margin: 0 auto;
}

/* 产品介绍 */
.product-intro {
  padding: 80px 20px;
  background: white;
}

.intro-content h2 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 24px;
}

.intro-content p {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 20px;
  font-size: 1.1rem;
}

/* 核心技术 */
.technology-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 60px;
  color: #303133;
}

.tech-card {
  text-align: center;
  padding: 40px 20px;
  height: 100%;
  transition: transform 0.3s ease;
}

.tech-card:hover {
  transform: translateY(-10px);
}

.tech-icon {
  margin-bottom: 24px;
}

.tech-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #303133;
}

.tech-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.tech-features {
  list-style: none;
  padding: 0;
  text-align: left;
}

.tech-features li {
  padding: 6px 0;
  color: #606266;
  position: relative;
  padding-left: 20px;
}

.tech-features li::before {
  content: '•';
  color: #409EFF;
  position: absolute;
  left: 0;
}

/* 应用场景 */
.scenarios-section {
  padding: 80px 20px;
  background: white;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.scenario-item {
  text-align: center;
  padding: 30px 20px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.scenario-item:hover {
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.scenario-icon {
  margin-bottom: 20px;
}

.scenario-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.scenario-description {
  color: #606266;
  line-height: 1.6;
}

/* 技术优势 */
.advantages-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.advantage-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.advantage-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
}

.advantage-list {
  list-style: none;
  padding: 0;
}

.advantage-list li {
  padding: 10px 0;
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

/* 团队介绍 */
.team-section {
  padding: 80px 20px;
  background: white;
}

.team-intro {
  text-align: center;
  margin-bottom: 50px;
}

.team-intro p {
  color: #606266;
  line-height: 1.8;
  font-size: 1.1rem;
  max-width: 800px;
  margin: 0 auto;
}

.member-card {
  text-align: center;
  padding: 30px 20px;
}

.member-avatar {
  margin-bottom: 20px;
}

.member-name {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.member-title {
  color: #409EFF;
  font-weight: 500;
  margin-bottom: 12px;
}

.member-description {
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

/* 发展历程 */
.timeline-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.timeline {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #409EFF;
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
  padding-left: 60px;
}

.timeline-marker {
  position: absolute;
  left: 12px;
  top: 8px;
  width: 16px;
  height: 16px;
  background: #409EFF;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 3px #409EFF;
}

.timeline-date {
  color: #409EFF;
  font-weight: 600;
  margin-bottom: 8px;
}

.timeline-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.timeline-description {
  color: #606266;
  line-height: 1.6;
}

/* 联系我们 */
.contact-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  text-align: center;
  color: white;
}

.contact-content h2 {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.contact-content p {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.contact-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .scenarios-grid {
    grid-template-columns: 1fr;
  }
  
  .contact-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .timeline-item {
    padding-left: 50px;
  }
}
</style>
