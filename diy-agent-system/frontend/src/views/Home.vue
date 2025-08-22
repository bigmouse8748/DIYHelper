<template>
  <div class="home">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">{{ $t('home.hero.title') }}</h1>
        <p class="hero-subtitle">{{ $t('home.hero.subtitle') }}</p>
        <div class="hero-actions">
          <el-button 
            v-if="!authStore.isAuthenticated" 
            type="primary" 
            size="large" 
            @click="goToLogin"
          >
            {{ $t('home.hero.getStarted') }}
          </el-button>
          <el-button 
            v-else 
            type="primary" 
            size="large" 
            @click="goToDIYAssistant"
          >
            {{ $t('home.hero.startProject') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="section-title">{{ $t('home.features.title') }}</h2>
      <div class="features-grid">
        <!-- DIY Smart Assistant -->
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#409eff"><MagicStick /></el-icon>
              <h3>{{ $t('home.features.diyAssistant.title') }}</h3>
            </div>
          </template>
          <p class="feature-description">{{ $t('home.features.diyAssistant.description') }}</p>
          <div class="feature-benefits">
            <div v-for="(benefit, index) in diyBenefits" :key="index" class="benefit-item">
              <el-icon color="#67c23a"><Check /></el-icon>
              <span>{{ benefit }}</span>
            </div>
          </div>
          <div class="feature-action">
            <el-button 
              type="primary" 
              @click="handleFeatureClick('diy')"
              :disabled="!authStore.isAuthenticated"
            >
              {{ authStore.isAuthenticated ? $t('home.features.tryNow') : $t('home.features.loginRequired') }}
            </el-button>
          </div>
        </el-card>

        <!-- Product Recommendations -->
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#67c23a"><ShoppingBag /></el-icon>
              <h3>{{ $t('home.features.productRecommendations.title') }}</h3>
            </div>
          </template>
          <p class="feature-description">{{ $t('home.features.productRecommendations.description') }}</p>
          <div class="feature-benefits">
            <div v-for="(benefit, index) in productBenefits" :key="index" class="benefit-item">
              <el-icon color="#67c23a"><Check /></el-icon>
              <span>{{ benefit }}</span>
            </div>
          </div>
          <div class="feature-action">
            <el-button 
              type="primary" 
              @click="handleFeatureClick('products')"
            >
              {{ $t('home.features.tryNow') }}
            </el-button>
          </div>
        </el-card>

        <!-- Tool Identification -->
        <el-card class="feature-card" shadow="hover">
          <template #header>
            <div class="feature-header">
              <el-icon :size="32" color="#e6a23c"><Search /></el-icon>
              <h3>{{ $t('home.features.toolIdentification.title') }}</h3>
            </div>
          </template>
          <p class="feature-description">{{ $t('home.features.toolIdentification.description') }}</p>
          <div class="feature-benefits">
            <div v-for="(benefit, index) in toolBenefits" :key="index" class="benefit-item">
              <el-icon color="#67c23a"><Check /></el-icon>
              <span>{{ benefit }}</span>
            </div>
          </div>
          <div class="feature-action">
            <el-button 
              type="primary" 
              @click="handleFeatureClick('tool')"
              :disabled="!authStore.isAuthenticated"
            >
              {{ authStore.isAuthenticated ? $t('home.features.tryNow') : $t('home.features.loginRequired') }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Examples Section -->
    <div class="examples-section">
      <h2 class="section-title">{{ $t('home.examples.title') }}</h2>
      <div class="examples-grid">
        <!-- DIY Project Example -->
        <el-card class="example-card" shadow="hover">
          <div class="example-image">
            <img src="https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=250&fit=crop" alt="DIY Project Example">
          </div>
          <div class="example-content">
            <h4>{{ $t('home.examples.diy.title') }}</h4>
            <p>{{ $t('home.examples.diy.description') }}</p>
            <div class="example-features">
              <el-tag v-for="(feature, index) in diyExampleFeatures" :key="index" size="small">
                {{ feature }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- Tool Identification Example -->
        <el-card class="example-card" shadow="hover">
          <div class="example-image">
            <img src="https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=250&fit=crop" alt="Tool Identification Example">
          </div>
          <div class="example-content">
            <h4>{{ $t('home.examples.tool.title') }}</h4>
            <p>{{ $t('home.examples.tool.description') }}</p>
            <div class="example-features">
              <el-tag v-for="(feature, index) in toolExampleFeatures" :key="index" size="small" type="warning">
                {{ feature }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Authentication Prompt -->
    <div v-if="!authStore.isAuthenticated" class="auth-prompt">
      <el-card class="prompt-card">
        <div class="prompt-content">
          <h3>{{ $t('home.authPrompt.title') }}</h3>
          <p>{{ $t('home.authPrompt.description') }}</p>
          <div class="prompt-actions">
            <el-button type="primary" size="large" @click="goToRegister">
              {{ $t('home.authPrompt.register') }}
            </el-button>
            <el-button size="large" @click="goToLogin">
              {{ $t('home.authPrompt.login') }}
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- User Dashboard Link -->
    <div v-else class="dashboard-prompt">
      <el-card class="prompt-card">
        <div class="prompt-content">
          <h3>{{ $t('home.welcomeBack', { username: authStore.currentUser?.username }) }}</h3>
          <p>{{ $t('home.dashboardPrompt.description') }}</p>
          <div class="prompt-actions">
            <el-button type="primary" size="large" @click="goToDashboard">
              {{ $t('home.dashboardPrompt.dashboard') }}
            </el-button>
            <el-button size="large" @click="goToDIYAssistant">
              {{ $t('home.dashboardPrompt.newProject') }}
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { MagicStick, Search, Check, ShoppingBag } from '@element-plus/icons-vue'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

const router = useRouter()
const { t } = useI18n()
const authStore = useCognitoAuthStore()

// Computed properties for arrays to avoid i18n issues
const diyBenefits = computed(() => {
  const locale = t('home.features.diyAssistant.benefits')
  if (Array.isArray(locale)) {
    return locale
  }
  // Fallback if i18n doesn't work properly
  return [
    'AI-powered project analysis',
    'Smart material recommendations', 
    'Real-time product pricing',
    'Step-by-step guidance'
  ]
})

const toolBenefits = computed(() => {
  const locale = t('home.features.toolIdentification.benefits')
  if (Array.isArray(locale)) {
    return locale
  }
  // Fallback
  return [
    'Instant tool recognition',
    'Detailed specifications',
    'Price comparison',
    'Shopping recommendations'
  ]
})

const productBenefits = computed(() => {
  const locale = t('home.features.productRecommendations.benefits')
  if (Array.isArray(locale)) {
    return locale
  }
  // Fallback
  return [
    'Curated product selection',
    'Competitive pricing',
    'Multiple merchant options',
    'No login required'
  ]
})

const diyExampleFeatures = computed(() => {
  const locale = t('home.examples.diy.features')
  if (Array.isArray(locale)) {
    return locale
  }
  // Fallback
  return ['Material List', 'Tool Recommendations', 'Safety Tips', 'Step-by-Step Guide']
})

const toolExampleFeatures = computed(() => {
  const locale = t('home.examples.tool.features')
  if (Array.isArray(locale)) {
    return locale
  }
  // Fallback
  return ['Brand Recognition', 'Model Details', 'Price Comparison', 'Alternative Options']
})

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const goToDIYAssistant = () => {
  router.push('/diy-assistant')
}

const goToToolIdentification = () => {
  router.push('/tool-identification')
}

const goToProducts = () => {
  router.push('/products')
}

const handleFeatureClick = (feature: 'diy' | 'tool' | 'products') => {
  if (feature === 'products') {
    goToProducts()
    return
  }
  
  if (!authStore.isAuthenticated) {
    ElMessage.info(t('home.messages.loginRequired'))
    return
  }
  
  if (feature === 'diy') {
    goToDIYAssistant()
  } else {
    goToToolIdentification()
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.hero-section {
  text-align: center;
  margin-bottom: 80px;
  padding: 60px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
}

.hero-content {
  max-width: 600px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(45deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 40px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.section-title {
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 40px;
  color: #303133;
}

.features-section {
  margin-bottom: 80px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature-card {
  height: 100%;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #303133;
}

.feature-description {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
  font-size: 14px;
}

.feature-benefits {
  margin-bottom: 24px;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.feature-action {
  text-align: center;
}

.examples-section {
  margin-bottom: 80px;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 32px;
}

.example-card {
  overflow: hidden;
  transition: transform 0.3s;
}

.example-card:hover {
  transform: translateY(-4px);
}

.example-image {
  overflow: hidden;
  height: 200px;
}

.example-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.example-card:hover .example-image img {
  transform: scale(1.05);
}

.example-content {
  padding: 20px;
}

.example-content h4 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
}

.example-content p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
  font-size: 14px;
}

.example-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.auth-prompt,
.dashboard-prompt {
  margin-top: 60px;
}

.prompt-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.prompt-card :deep(.el-card__body) {
  background: transparent;
}

.prompt-content {
  text-align: center;
  color: white;
  padding: 20px;
}

.prompt-content h3 {
  margin: 0 0 16px 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.prompt-content p {
  margin-bottom: 24px;
  opacity: 0.9;
  line-height: 1.6;
}

.prompt-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .home {
    padding: 20px;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .features-grid,
  .examples-grid {
    grid-template-columns: 1fr;
  }
  
  .prompt-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .prompt-actions .el-button {
    width: 200px;
  }
}
</style>