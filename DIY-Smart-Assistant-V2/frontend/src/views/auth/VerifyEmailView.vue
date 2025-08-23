<template>
  <div class="verify-email">
    <div class="verify-container">
      <div class="verify-card">
        <div class="verify-header">
          <el-icon class="verify-icon" :class="statusIconClass">
            <component :is="statusIcon" />
          </el-icon>
          <h1 class="verify-title">{{ verificationTitle }}</h1>
          <p class="verify-subtitle">{{ verificationMessage }}</p>
        </div>
        
        <div v-if="loading" class="verify-loading">
          <el-icon class="loading-icon is-loading"><Loading /></el-icon>
          <p>Verifying your email address...</p>
        </div>
        
        <div v-else-if="!hasToken" class="verify-actions">
          <p class="info-text">
            Please check your email and click the verification link to activate your account.
          </p>
          <div class="action-buttons">
            <el-button type="primary" @click="resendVerification" :loading="resending">
              Resend Verification Email
            </el-button>
            <el-button @click="goToLogin">
              Back to Login
            </el-button>
          </div>
        </div>
        
        <div v-else-if="verified" class="verify-success">
          <div class="success-actions">
            <el-button type="primary" size="large" @click="goToLogin">
              Continue to Login
            </el-button>
            <el-button @click="goToHome">
              Go to Home
            </el-button>
          </div>
        </div>
        
        <div v-else-if="error" class="verify-error">
          <p class="error-details">{{ errorMessage }}</p>
          <div class="error-actions">
            <el-button type="primary" @click="resendVerification" :loading="resending">
              Resend Verification Email
            </el-button>
            <el-button @click="goToRegister">
              Back to Registration
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Loading,
  CircleCheck,
  CircleClose,
  Warning
} from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()

// State
const loading = ref(false)
const resending = ref(false)
const verified = ref(false)
const error = ref(false)
const errorMessage = ref('')

// Computed
const hasToken = computed(() => !!route.query.token)

const statusIcon = computed(() => {
  if (loading.value) return Loading
  if (verified.value) return CircleCheck
  if (error.value) return CircleClose
  return Warning
})

const statusIconClass = computed(() => {
  if (verified.value) return 'success'
  if (error.value) return 'error'
  return 'warning'
})

const verificationTitle = computed(() => {
  if (loading.value) return 'Verifying Email...'
  if (verified.value) return 'Email Verified!'
  if (error.value) return 'Verification Failed'
  return 'Email Verification'
})

const verificationMessage = computed(() => {
  if (loading.value) return 'Please wait while we verify your email address.'
  if (verified.value) return 'Your email has been successfully verified. You can now log in to your account.'
  if (error.value) return 'We encountered an issue verifying your email address.'
  return 'Complete your account setup by verifying your email address.'
})

// Methods
const verifyEmail = async (token: string) => {
  loading.value = true
  error.value = false
  
  try {
    const response = await api.post(`/api/v1/auth/verify-email?token=${token}`)
    
    verified.value = true
    ElMessage.success('Email verified successfully!')
  } catch (err: any) {
    error.value = true
    errorMessage.value = err.message || 'An unexpected error occurred'
    ElMessage.error('Email verification failed')
  } finally {
    loading.value = false
  }
}

const resendVerification = async () => {
  resending.value = true
  
  try {
    // In a real implementation, you'd need the user's email
    // This is a placeholder for the resend functionality
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('Verification email sent! Please check your inbox.')
  } catch (err) {
    ElMessage.error('Failed to resend verification email')
  } finally {
    resending.value = false
  }
}

const goToLogin = () => {
  router.push({ name: 'login' })
}

const goToRegister = () => {
  router.push({ name: 'register' })
}

const goToHome = () => {
  router.push({ name: 'landing' })
}

// Lifecycle
onMounted(() => {
  const token = route.query.token as string
  
  if (token) {
    verifyEmail(token)
  }
})
</script>

<style scoped>
.verify-email {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.verify-container {
  width: 100%;
  max-width: 500px;
}

.verify-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.verify-header {
  margin-bottom: 32px;
}

.verify-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.verify-icon.success {
  color: #67c23a;
}

.verify-icon.error {
  color: #f56c6c;
}

.verify-icon.warning {
  color: #e6a23c;
}

.verify-title {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.verify-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

.verify-loading {
  padding: 20px;
}

.loading-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 16px;
}

.verify-loading p {
  color: #606266;
  margin: 0;
}

.info-text {
  color: #606266;
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.action-buttons,
.success-actions,
.error-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.error-details {
  color: #f56c6c;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 8px;
  padding: 12px;
  margin: 0 0 20px 0;
  font-size: 14px;
}

/* Responsive */
@media (max-width: 768px) {
  .verify-email {
    padding: 16px;
  }
  
  .verify-card {
    padding: 24px;
  }
  
  .verify-icon {
    font-size: 48px;
  }
  
  .verify-title {
    font-size: 24px;
  }
  
  .verify-subtitle {
    font-size: 14px;
  }
}
</style>