<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>{{ $t('auth.welcome') }}</h1>
        <p>{{ $t('auth.loginSubtitle') }}</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="$t('auth.username')"
            :prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="$t('auth.password')"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="authStore.isLoading"
            @click="handleLogin"
          >
            {{ $t('auth.login') }}
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <span>{{ $t('auth.noAccount') }}</span>
          <el-link type="primary" @click="goToRegister">
            {{ $t('auth.register') }}
          </el-link>
        </div>
      </el-form>

      <!-- Demo account info -->
      <el-card class="demo-info" shadow="never">
        <div class="demo-content">
          <h3>Test Your Login</h3>
          <p>Please register a new account or try manual login to test the authentication system.</p>
          <div class="demo-credentials">
            <el-tag>Database: PostgreSQL</el-tag>
            <el-tag type="success">Persistent Storage</el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, FormInstance, FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: t('auth.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 20, message: t('auth.usernameLength'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.passwordRequired'), trigger: 'blur' },
    { min: 6, message: t('auth.passwordLength'), trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  console.log('=== LOGIN DEBUG: handleLogin called ===')
  console.log('loginForm:', loginForm)
  console.log('loginFormRef.value:', loginFormRef.value)
  
  if (!loginFormRef.value) {
    console.log('=== LOGIN DEBUG: No form ref, returning ===')
    return
  }

  try {
    console.log('=== LOGIN DEBUG: Starting validation ===')
    await loginFormRef.value.validate()
    console.log('=== LOGIN DEBUG: Validation passed ===')
    
    console.log('=== LOGIN DEBUG: Calling authStore.loginUser ===')
    await authStore.loginUser(loginForm.username, loginForm.password)
    console.log('=== LOGIN DEBUG: Login completed successfully ===')
    
    ElMessage.success(t('auth.loginSuccess'))
    
    // Redirect to tool identification page
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/tool-identification')
  } catch (error: any) {
    console.log('=== LOGIN DEBUG: Login error ===', error)
    ElMessage.error(error.message || t('auth.loginFailed'))
  }
}

// Demo login removed for security

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  color: #606266;
  font-size: 14px;
}

.login-form {
  margin-bottom: 24px;
}

.login-button {
  width: 100%;
  height: 44px;
}

.form-footer {
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.demo-info {
  margin-top: 24px;
  background: #f8f9fa;
}

.demo-content {
  text-align: center;
}

.demo-content h3 {
  color: #303133;
  margin-bottom: 8px;
  font-size: 16px;
}

.demo-content p {
  color: #606266;
  font-size: 14px;
  margin-bottom: 16px;
}

.demo-credentials {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
</style>