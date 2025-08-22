<template>
  <div class="test-page">
    <div class="test-container">
      <h1>Test Page</h1>
      
      <div class="test-section">
        <h2>Navigation Test</h2>
        <div class="button-group">
          <el-button type="primary" @click="goToLogin">
            Go to Login
          </el-button>
          <el-button type="success" @click="goToRegister">
            Go to Register
          </el-button>
          <el-button type="warning" @click="goToDashboard">
            Go to Dashboard
          </el-button>
          <el-button type="info" @click="goHome">
            Go Home
          </el-button>
        </div>
      </div>
      
      <div class="test-section">
        <h2>Auth Store Test</h2>
        <div class="auth-info">
          <p><strong>Authenticated:</strong> {{ authStore.isAuthenticated }}</p>
          <p><strong>User:</strong> {{ authStore.user?.username || 'None' }}</p>
          <p><strong>Token:</strong> {{ !!authStore.accessToken ? 'Yes' : 'No' }}</p>
        </div>
        <div class="button-group">
          <el-button type="primary" @click="testLogin">
            Test Login
          </el-button>
          <el-button @click="testLogout">
            Test Logout
          </el-button>
        </div>
      </div>
      
      <div class="test-section">
        <h2>Current Route</h2>
        <p><strong>Path:</strong> {{ $route.path }}</p>
        <p><strong>Name:</strong> {{ $route.name }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const goToLogin = () => {
  console.log('Going to login...')
  router.push('/auth/login')
}

const goToRegister = () => {
  console.log('Going to register...')
  router.push('/auth/register')
}

const goToDashboard = () => {
  console.log('Going to dashboard...')
  router.push('/dashboard')
}

const goHome = () => {
  console.log('Going home...')
  router.push('/')
}

const testLogin = async () => {
  try {
    console.log('Testing login...')
    await authStore.login({
      email: 'test2@example.com',
      password: 'Password123'
    })
    ElMessage.success('Login successful!')
  } catch (error: any) {
    console.error('Login error:', error)
    ElMessage.error('Login failed: ' + error.message)
  }
}

const testLogout = async () => {
  await authStore.logout()
  ElMessage.success('Logged out!')
}
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.test-container {
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  background: white;
  padding: 24px;
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-section h2 {
  margin: 0 0 16px 0;
  color: #303133;
}

.button-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.auth-info {
  margin-bottom: 16px;
}

.auth-info p {
  margin: 4px 0;
  color: #606266;
}
</style>