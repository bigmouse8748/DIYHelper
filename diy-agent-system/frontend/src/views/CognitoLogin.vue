<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="32" class="logo-icon"><Tools /></el-icon>
          <h2>{{ $t('auth.welcome') }}</h2>
          <p class="subtitle">{{ $t('auth.loginSubtitle') }}</p>
        </div>
      </template>

      <!-- Email/Password Login Form -->
      <el-form 
        v-if="!showEmailConfirmation && !showForgotPassword"
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="email">
          <el-input
            v-model="loginForm.email"
            type="email"
            :placeholder="$t('auth.emailPlaceholder')"
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="$t('auth.passwordPlaceholder')"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <div class="form-actions">
          <el-button 
            type="primary" 
            size="large" 
            :loading="authStore.isLoading"
            @click="handleLogin"
            class="login-btn"
          >
            {{ $t('auth.login') }}
          </el-button>
          
          <div class="links">
            <el-link 
              type="primary" 
              @click="showForgotPassword = true"
              class="forgot-link"
            >
              {{ $t('auth.forgotPassword') }}
            </el-link>
          </div>
        </div>
      </el-form>

      <!-- Email Confirmation Form -->
      <div v-if="showEmailConfirmation" class="confirmation-form">
        <div class="confirmation-header">
          <el-icon :size="48" color="#67c23a"><SuccessFilled /></el-icon>
          <h3>{{ $t('auth.confirmEmail') }}</h3>
          <p>{{ $t('auth.confirmEmailMessage') }}</p>
        </div>
        
        <el-form @submit.prevent="handleEmailConfirmation">
          <el-form-item>
            <el-input
              v-model="confirmationForm.email"
              type="email"
              :placeholder="$t('auth.emailPlaceholder')"
              size="large"
              :prefix-icon="Message"
              disabled
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="confirmationForm.code"
              :placeholder="$t('auth.confirmationCode')"
              size="large"
              :prefix-icon="Key"
              maxlength="6"
              @keyup.enter="handleEmailConfirmation"
            />
          </el-form-item>

          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              :loading="authStore.isLoading"
              @click="handleEmailConfirmation"
              class="confirm-btn"
            >
              {{ $t('auth.confirmEmail') }}
            </el-button>
            
            <el-button 
              size="large" 
              @click="showEmailConfirmation = false"
              class="back-btn"
            >
              {{ $t('common.back') }}
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- Forgot Password Form -->
      <div v-if="showForgotPassword && !showResetPassword" class="forgot-form">
        <div class="forgot-header">
          <el-icon :size="48" color="#e6a23c"><QuestionFilled /></el-icon>
          <h3>{{ $t('auth.resetPassword') }}</h3>
          <p>{{ $t('auth.resetPasswordMessage') }}</p>
        </div>
        
        <el-form @submit.prevent="handleForgotPassword">
          <el-form-item>
            <el-input
              v-model="forgotForm.email"
              type="email"
              :placeholder="$t('auth.emailPlaceholder')"
              size="large"
              :prefix-icon="Message"
              @keyup.enter="handleForgotPassword"
            />
          </el-form-item>

          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              :loading="authStore.isLoading"
              @click="handleForgotPassword"
              class="reset-btn"
            >
              {{ $t('auth.sendResetCode') }}
            </el-button>
            
            <el-button 
              size="large" 
              @click="showForgotPassword = false"
              class="back-btn"
            >
              {{ $t('common.back') }}
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- Reset Password Form -->
      <div v-if="showResetPassword" class="reset-form">
        <div class="reset-header">
          <el-icon :size="48" color="#409eff"><Lock /></el-icon>
          <h3>{{ $t('auth.newPassword') }}</h3>
          <p>{{ $t('auth.newPasswordMessage') }}</p>
        </div>
        
        <el-form @submit.prevent="handlePasswordReset">
          <el-form-item>
            <el-input
              v-model="resetForm.email"
              type="email"
              :placeholder="$t('auth.emailPlaceholder')"
              size="large"
              :prefix-icon="Message"
              disabled
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="resetForm.code"
              :placeholder="$t('auth.confirmationCode')"
              size="large"
              :prefix-icon="Key"
              maxlength="6"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input
              v-model="resetForm.newPassword"
              type="password"
              :placeholder="$t('auth.newPasswordPlaceholder')"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handlePasswordReset"
            />
          </el-form-item>

          <div class="form-actions">
            <el-button 
              type="primary" 
              size="large" 
              :loading="authStore.isLoading"
              @click="handlePasswordReset"
              class="reset-btn"
            >
              {{ $t('auth.resetPassword') }}
            </el-button>
            
            <el-button 
              size="large" 
              @click="showResetPassword = false; showForgotPassword = false"
              class="back-btn"
            >
              {{ $t('common.back') }}
            </el-button>
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="card-footer">
          <p>{{ $t('auth.noAccount') }}</p>
          <router-link to="/register" class="register-link">
            {{ $t('auth.signUpNow') }}
          </router-link>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Tools, Message, Lock, Key, SuccessFilled, QuestionFilled } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

const { t } = useI18n()
const authStore = useCognitoAuthStore()

// Form states
const showEmailConfirmation = ref(false)
const showForgotPassword = ref(false)
const showResetPassword = ref(false)

// Login form
const loginFormRef = ref()
const loginForm = reactive({
  email: '',
  password: ''
})

const loginRules = {
  email: [
    { required: true, message: t('validation.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('validation.emailInvalid'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('validation.passwordRequired'), trigger: 'blur' }
  ]
}

// Email confirmation form
const confirmationForm = reactive({
  email: '',
  code: ''
})

// Forgot password form
const forgotForm = reactive({
  email: ''
})

// Reset password form
const resetForm = reactive({
  email: '',
  code: '',
  newPassword: ''
})

// Handle login
const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()
    await authStore.login(loginForm.email, loginForm.password)
  } catch (error) {
    console.error('Login failed:', error)
  }
}

// Handle email confirmation
const handleEmailConfirmation = async () => {
  if (!confirmationForm.code) {
    ElMessage.error(t('validation.confirmationCodeRequired'))
    return
  }
  
  try {
    await authStore.confirmEmail(confirmationForm.email, confirmationForm.code)
    showEmailConfirmation.value = false
    ElMessage.success(t('auth.emailConfirmed'))
  } catch (error) {
    console.error('Email confirmation failed:', error)
  }
}

// Handle forgot password
const handleForgotPassword = async () => {
  if (!forgotForm.email) {
    ElMessage.error(t('validation.emailRequired'))
    return
  }
  
  try {
    await authStore.forgotPassword(forgotForm.email)
    resetForm.email = forgotForm.email
    showResetPassword.value = true
  } catch (error) {
    console.error('Forgot password failed:', error)
  }
}

// Handle password reset
const handlePasswordReset = async () => {
  if (!resetForm.code || !resetForm.newPassword) {
    ElMessage.error(t('validation.allFieldsRequired'))
    return
  }
  
  try {
    await authStore.confirmPasswordReset(resetForm.email, resetForm.code, resetForm.newPassword)
    showResetPassword.value = false
    showForgotPassword.value = false
    ElMessage.success(t('auth.passwordResetSuccess'))
  } catch (error) {
    console.error('Password reset failed:', error)
  }
}

// Show email confirmation if coming from registration
if (history.state?.showEmailConfirmation) {
  showEmailConfirmation.value = true
  confirmationForm.email = history.state.email || ''
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.logo-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-weight: 600;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-form,
.confirmation-form,
.forgot-form,
.reset-form {
  padding: 0 20px 20px 20px;
}

.form-actions {
  margin-top: 24px;
}

.login-btn,
.confirm-btn,
.reset-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

.back-btn {
  width: 100%;
  height: 44px;
  margin-top: 12px;
  border-radius: 8px;
}

.links {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.forgot-link {
  font-size: 14px;
}

.confirmation-header,
.forgot-header,
.reset-header {
  text-align: center;
  margin-bottom: 24px;
}

.confirmation-header h3,
.forgot-header h3,
.reset-header h3 {
  margin: 16px 0 8px 0;
  color: #303133;
}

.confirmation-header p,
.forgot-header p,
.reset-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.card-footer {
  text-align: center;
  padding: 16px;
  background-color: #f8f9fa;
}

.card-footer p {
  margin: 0 0 8px 0;
  color: #606266;
  font-size: 14px;
}

.register-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.register-link:hover {
  color: #337ecc;
}

:deep(.el-card__header) {
  padding: 0;
}

:deep(.el-card__footer) {
  padding: 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}
</style>