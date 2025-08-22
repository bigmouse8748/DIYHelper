<template>
  <div class="debug-panel">
    <el-card class="debug-info" v-if="showDebug">
      <template #header>
        <div class="debug-header">
          <span>🔧 Debug Panel</span>
          <el-button size="small" text @click="toggleDebug">×</el-button>
        </div>
      </template>
      
      <div class="debug-content">
        <div class="debug-item">
          <strong>Route:</strong> {{ $route.path }}
        </div>
        <div class="debug-item">
          <strong>Auth:</strong> 
          <el-tag :type="authStore.isAuthenticated ? 'success' : 'danger'" size="small">
            {{ authStore.isAuthenticated ? 'Yes' : 'No' }}
          </el-tag>
        </div>
        <div class="debug-item">
          <strong>User:</strong> {{ authStore.user?.username || 'None' }}
        </div>
        <div class="debug-item">
          <strong>Token:</strong> 
          <el-tag :type="!!authStore.accessToken ? 'success' : 'danger'" size="small">
            {{ !!authStore.accessToken ? 'Yes' : 'No' }}
          </el-tag>
        </div>
        
        <div class="debug-actions">
          <el-button size="small" type="primary" @click="testLogin">
            Quick Login
          </el-button>
          <el-button size="small" @click="testLogout">
            Logout
          </el-button>
          <el-button size="small" @click="testNavigation">
            Test Nav
          </el-button>
        </div>
      </div>
    </el-card>
    
    <el-button 
      v-else
      class="debug-toggle" 
      size="small" 
      type="primary" 
      @click="toggleDebug"
      circle
    >
      🔧
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const showDebug = ref(false)

const toggleDebug = () => {
  showDebug.value = !showDebug.value
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

const testNavigation = () => {
  console.log('Testing navigation to login page...')
  router.push('/auth/login')
  ElMessage.info('Navigating to login page')
}
</script>

<style scoped>
.debug-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
}

.debug-info {
  width: 320px;
  font-size: 13px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.debug-toggle {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.debug-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.debug-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.debug-item:last-of-type {
  border-bottom: none;
}

.debug-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.debug-actions .el-button {
  flex: 1;
  min-width: 80px;
}
</style>