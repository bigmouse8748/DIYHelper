<template>
  <div class="home">
    <!-- Header -->
    <header class="site-header">
      <div class="header-container">
        <div class="logo-section">
          <el-icon class="logo-icon"><Tools /></el-icon>
          <h1 class="site-title">DIY Smart Assistant</h1>
        </div>
        
        <nav class="main-nav">
          <a href="#features" class="nav-link">Features</a>
          <a href="#how-it-works" class="nav-link">How It Works</a>
          <a href="#pricing" class="nav-link">Pricing</a>
          <a href="#about" class="nav-link">About</a>
        </nav>
        
        <div class="auth-section">
          <template v-if="!authStore.isAuthenticated">
            <el-button text @click="navigateToLogin">Sign In</el-button>
            <el-button type="primary" @click="navigateToRegister">Get Started</el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="navigateToDashboard">Dashboard</el-button>
          </template>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="hero-title">
            Intelligent DIY Project Assistant
          </h1>
          <h2 class="hero-subtitle">
            Transform your DIY projects with AI-powered tool identification, 
            smart product recommendations, and expert guidance.
          </h2>
          
          <div class="hero-actions">
            <template v-if="!authStore.isAuthenticated">
              <el-button type="primary" size="large" @click="navigateToRegister">
                Start Free Trial
              </el-button>
              <el-button size="large" @click="navigateToLogin">
                Sign In
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="large" @click="navigateToDashboard">
                Go to Dashboard
              </el-button>
            </template>
          </div>

          <div class="social-proof">
            <p class="proof-text">Trusted by 10,000+ DIY enthusiasts</p>
            <div class="stats-row">
              <div class="stat">
                <span class="stat-number">15K+</span>
                <span class="stat-label">Tools Identified</span>
              </div>
              <div class="stat">
                <span class="stat-number">8K+</span>
                <span class="stat-label">Projects Completed</span>
              </div>
              <div class="stat">
                <span class="stat-number">98%</span>
                <span class="stat-label">Accuracy Rate</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="hero-image">
          <div class="demo-interface">
            <div class="demo-window">
              <div class="window-header">
                <div class="window-controls">
                  <span class="control red"></span>
                  <span class="control yellow"></span>
                  <span class="control green"></span>
                </div>
                <span class="window-title">DIY Assistant</span>
              </div>
              <div class="window-content">
                <div class="demo-section">
                  <div class="demo-icon"><el-icon><Search /></el-icon></div>
                  <div class="demo-text">
                    <h4>Tool Identification</h4>
                    <p>Upload image → AI identifies → Get purchase links</p>
                  </div>
                </div>
                <div class="demo-section">
                  <div class="demo-icon"><el-icon><ShoppingBag /></el-icon></div>
                  <div class="demo-text">
                    <h4>Smart Recommendations</h4>
                    <p>Project type → Product suggestions → Best prices</p>
                  </div>
                </div>
                <div class="demo-section">
                  <div class="demo-icon"><el-icon><DataAnalysis /></el-icon></div>
                  <div class="demo-text">
                    <h4>Project Analysis</h4>
                    <p>Multiple images → Complete guidance → Step-by-step</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="features-container">
        <h2 class="features-title">Powerful Features</h2>
        <el-row :gutter="30">
          <el-col :xs="24" :md="8">
            <div class="feature-card">
              <el-icon class="feature-icon"><Search /></el-icon>
              <h3>Tool Identification</h3>
              <p>Upload an image to identify any tool instantly</p>
            </div>
          </el-col>
          
          <el-col :xs="24" :md="8">
            <div class="feature-card">
              <el-icon class="feature-icon"><ShoppingBag /></el-icon>
              <h3>Product Recommendation</h3>
              <p>Get smart product recommendations for your projects</p>
            </div>
          </el-col>
          
          <el-col :xs="24" :md="8">
            <div class="feature-card">
              <el-icon class="feature-icon"><DataAnalysis /></el-icon>
              <h3>Project Analysis</h3>
              <p>Complete analysis of your DIY projects with step-by-step guidance</p>
            </div>
          </el-col>
        </el-row>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-container">
        <h2>Ready to Start Your DIY Journey?</h2>
        <p>Join thousands of DIY enthusiasts who use our AI-powered assistant</p>
        <el-button
          v-if="!authStore.isAuthenticated"
          type="primary"
          size="large"
          @click="navigateToRegister"
        >
          Get Started Today
        </el-button>
        <el-button
          v-if="authStore.isAuthenticated"
          type="primary"
          size="large"
          @click="navigateToToolIdentification"
        >
          Start Identifying Tools
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Tools, Search, ShoppingBag, DataAnalysis, User, HomeFilled } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// Navigation helper functions
const navigateToLogin = () => {
  console.log('🔗 Navigating to login page...')
  try {
    router.push('/auth/login')
    console.log('✅ Navigation successful')
  } catch (error) {
    console.error('❌ Navigation failed:', error)
  }
}

const navigateToRegister = () => {
  console.log('🔗 Navigating to register page...')
  try {
    router.push('/auth/register')
    console.log('✅ Navigation successful')
  } catch (error) {
    console.error('❌ Navigation failed:', error)
  }
}

const navigateToDashboard = () => {
  console.log('🔗 Navigating to dashboard...')
  try {
    router.push('/dashboard')
    console.log('✅ Navigation successful')
  } catch (error) {
    console.error('❌ Navigation failed:', error)
  }
}

const navigateToToolIdentification = () => {
  console.log('🔗 Navigating to tool identification...')
  try {
    router.push('/tools/identification')
    console.log('✅ Navigation successful')
  } catch (error) {
    console.error('❌ Navigation failed:', error)
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: #ffffff;
}

/* Header Styles */
.site-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
  color: #667eea;
}

.site-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0;
}

.main-nav {
  display: flex;
  gap: 32px;
}

.nav-link {
  color: #606266;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #667eea;
}

.auth-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
  padding: 80px 20px;
  min-height: 600px;
  display: flex;
  align-items: center;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

.hero-content {
  text-align: left;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 20px 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 20px;
  color: #606266;
  margin: 0 0 40px 0;
  line-height: 1.6;
  font-weight: 400;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-bottom: 60px;
}

.hero-actions .el-button {
  padding: 14px 28px;
  font-size: 16px;
  border-radius: 8px;
}

.social-proof {
  border-top: 1px solid #e4e7ed;
  padding-top: 32px;
}

.proof-text {
  color: #909399;
  font-size: 14px;
  margin: 0 0 16px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.stats-row {
  display: flex;
  gap: 40px;
}

.stat {
  text-align: left;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

/* Demo Interface */
.hero-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.demo-interface {
  width: 100%;
  max-width: 500px;
}

.demo-window {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.window-header {
  background: #f5f7fa;
  padding: 12px 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 12px;
}

.window-controls {
  display: flex;
  gap: 6px;
}

.control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.control.red {
  background: #ff5f57;
}

.control.yellow {
  background: #ffbd2e;
}

.control.green {
  background: #28ca42;
}

.window-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.window-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.demo-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9ff;
  border: 1px solid #e1e6ff;
}

.demo-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  background: #667eea;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.demo-text h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.demo-text p {
  font-size: 14px;
  color: #606266;
  margin: 0;
  line-height: 1.4;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
    height: 60px;
  }
  
  .main-nav {
    display: none;
  }
  
  .site-title {
    font-size: 20px;
  }
  
  .logo-icon {
    font-size: 28px;
  }
  
  .hero {
    padding: 60px 16px;
  }
  
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .hero-actions {
    justify-content: center;
  }
  
  .stats-row {
    gap: 20px;
    justify-content: center;
  }
  
  .demo-interface {
    max-width: 100%;
  }
}

.features {
  padding: 80px 20px;
  background: #f8f9fa;
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
}

.features-title {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 60px 0;
}

.feature-card {
  text-align: center;
  padding: 40px 20px;
}

.feature-icon {
  font-size: 64px;
  color: #667eea;
  margin-bottom: 24px;
}

.feature-card h3 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

.feature-card p {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.cta {
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.cta-container {
  max-width: 800px;
  margin: 0 auto;
}

.cta h2 {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
}

.cta p {
  font-size: 18px;
  margin: 0 0 40px 0;
  opacity: 0.9;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }

  .hero-title {
    font-size: 36px;
    justify-content: center;
  }

  .hero-icon {
    font-size: 42px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .hero-actions {
    justify-content: center;
  }

  .features-title {
    font-size: 28px;
  }

  .cta h2 {
    font-size: 28px;
  }
}
</style>
