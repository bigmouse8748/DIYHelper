<template>
  <div class="landing-page">
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
            <el-button type="primary" size="large" @click="handleGetStarted">
              Start Free Trial
            </el-button>
            <el-button size="large" @click="handleSignIn">
              Sign In
            </el-button>
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
                  <div class="demo-icon">🔍</div>
                  <div class="demo-text">
                    <h4>Tool Identification</h4>
                    <p>Upload image → AI identifies → Get purchase links</p>
                  </div>
                </div>
                <div class="demo-section">
                  <div class="demo-icon">🛒</div>
                  <div class="demo-text">
                    <h4>Smart Recommendations</h4>
                    <p>Project type → Product suggestions → Best prices</p>
                  </div>
                </div>
                <div class="demo-section">
                  <div class="demo-icon">📊</div>
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
    <section class="features" id="features">
      <div class="features-container">
        <h2 class="features-title">Powerful Features</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>Tool Identification</h3>
            <p>Upload an image of any tool and our AI will instantly identify it and find the best purchasing options from top retailers.</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🛒</div>
            <h3>Smart Recommendations</h3>
            <p>Get intelligent product recommendations tailored to your specific DIY project needs and budget.</p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Project Analysis</h3>
            <p>Complete analysis of your DIY projects with step-by-step guidance and safety recommendations.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Debug Panel (Development) -->
    <div v-if="showDebug" class="debug-panel">
      <el-button 
        type="primary" 
        circle 
        @click="debugVisible = !debugVisible"
        style="position: fixed; top: 20px; right: 20px; z-index: 1000;"
      >
        🔧
      </el-button>
      
      <el-card v-show="debugVisible" class="debug-info">
        <template #header>
          <div class="debug-header">
            <span>🔧 Debug Panel</span>
            <el-button text @click="debugVisible = false">×</el-button>
          </div>
        </template>
        
        <div class="debug-item">
          <strong>Status:</strong> <span>Vue.js SPA</span>
        </div>
        <div class="debug-item">
          <strong>Mode:</strong> <span>Unified Application</span>
        </div>
        <div class="debug-item">
          <strong>Backend:</strong> <span :class="backendStatus.class">{{ backendStatus.text }}</span>
        </div>
        
        <div class="debug-actions">
          <el-button type="primary" size="small" @click="testBackend">Test API</el-button>
          <el-button size="small" @click="testLogin">Test Login</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api, { AUTH_ENDPOINTS, AGENT_ENDPOINTS } from '@/utils/api'

const router = useRouter()

// Debug panel state
const showDebug = ref(import.meta.env.DEV)
const debugVisible = ref(false)
const backendStatus = ref({
  text: 'Checking...',
  class: 'status-checking'
})

// Navigation handlers
const handleGetStarted = () => {
  router.push('/auth/register')
}

const handleSignIn = () => {
  router.push('/auth/login')
}

// Debug functions
const testBackend = async () => {
  try {
    const response = await api.get(AGENT_ENDPOINTS.AVAILABLE_AGENTS)
    const data = response.data
    console.log('Backend API test successful:', data)
    backendStatus.value = {
      text: 'Connected',
      class: 'status-success'
    }
    ElMessage.success('Backend API is working! Check console for details.')
  } catch (error) {
    console.error('Backend API test failed:', error)
    backendStatus.value = {
      text: 'Failed',
      class: 'status-error'
    }
    ElMessage.error('Backend API test failed. Make sure the backend is running.')
  }
}

const testLogin = async () => {
  const loginData = {
    email: 'test2@example.com',
    password: 'Password123'
  }

  try {
    const response = await api.post(AUTH_ENDPOINTS.LOGIN, loginData)
    const data = response.data
    console.log('Login test successful:', data)
    ElMessage.success('Login test successful! Check console for details.')
  } catch (error) {
    console.error('Login test failed:', error)
    ElMessage.error('Login test failed. Check console for details.')
  }
}

// Initialize
onMounted(() => {
  if (showDebug.value) {
    setTimeout(testBackend, 1000)
  }
})
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  background: #ffffff;
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
  align-items: center;
  /* Default desktop layout */
  grid-template-columns: 1fr 1fr;
  gap: 80px;
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

.control.red { background: #ff5f57; }
.control.yellow { background: #ffbd2e; }
.control.green { background: #28ca42; }

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
  font-weight: bold;
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

/* Features Section */
.features {
  padding: 80px 20px;
  background: #f8f9fa;
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.features-title {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 60px 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
}

.feature-card {
  background: white;
  padding: 40px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: #667eea;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
  margin: 0 auto 20px;
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

/* Debug Panel */
.debug-info {
  position: fixed;
  top: 70px;
  right: 20px;
  width: 300px;
  z-index: 999;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.debug-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.debug-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.status-checking { color: #909399; }
.status-success { color: #67c23a; }
.status-error { color: #f56c6c; }

/* Desktop Layout (default) */
@media (min-width: 769px) {
  .hero-container {
    grid-template-columns: 1fr 1fr;
    gap: 80px;
    text-align: left;
  }
  
  .hero-content {
    text-align: left;
  }
  
  .hero-actions {
    justify-content: flex-start;
  }
  
  .stats-row {
    justify-content: flex-start;
  }
  
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
  }
}

/* Mobile Layout */
@media (max-width: 768px) {
  .hero {
    padding: 60px 16px;
  }
  
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-content {
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
    flex-wrap: wrap;
  }
  
  .stats-row {
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>