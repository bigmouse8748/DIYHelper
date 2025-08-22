<template>
  <div class="register-container">
    <el-card class="register-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="32" class="logo-icon"><UserFilled /></el-icon>
          <h2>{{ $t('auth.createAccount') }}</h2>
          <p class="subtitle">{{ $t('auth.registerSubtitle') }}</p>
        </div>
      </template>

      <el-form 
        ref="registerFormRef" 
        :model="registerForm" 
        :rules="registerRules" 
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            :placeholder="$t('auth.emailPlaceholder')"
            size="large"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            :placeholder="$t('auth.usernamePlaceholder')"
            size="large"
            :prefix-icon="User"
            clearable
            maxlength="20"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            :placeholder="$t('auth.passwordPlaceholder')"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
          <div class="password-requirements">
            <div class="requirement" :class="{ valid: hasMinLength }">
              <el-icon :size="12"><Check /></el-icon>
              {{ $t('auth.passwordMinLength') }}
            </div>
            <div class="requirement" :class="{ valid: hasUppercase }">
              <el-icon :size="12"><Check /></el-icon>
              {{ $t('auth.passwordUppercase') }}
            </div>
            <div class="requirement" :class="{ valid: hasLowercase }">
              <el-icon :size="12"><Check /></el-icon>
              {{ $t('auth.passwordLowercase') }}
            </div>
            <div class="requirement" :class="{ valid: hasNumbers }">
              <el-icon :size="12"><Check /></el-icon>
              {{ $t('auth.passwordNumbers') }}
            </div>
          </div>
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            :placeholder="$t('auth.confirmPasswordPlaceholder')"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item prop="agreeTerms">
          <el-checkbox v-model="registerForm.agreeTerms" size="large">
            {{ $t('auth.agreeToTerms') }}
            <el-link type="primary" @click="showTermsDialog = true">
              {{ $t('auth.termsAndConditions') }}
            </el-link>
          </el-checkbox>
        </el-form-item>

        <div class="form-actions">
          <el-button 
            type="primary" 
            size="large" 
            :loading="authStore.isLoading"
            @click="handleRegister"
            class="register-btn"
            :disabled="!isFormValid"
          >
            {{ $t('auth.createAccount') }}
          </el-button>
        </div>
      </el-form>

      <template #footer>
        <div class="card-footer">
          <p>{{ $t('auth.alreadyHaveAccount') }}</p>
          <router-link to="/login" class="login-link">
            {{ $t('auth.signInNow') }}
          </router-link>
        </div>
      </template>
    </el-card>

    <!-- Terms and Conditions Dialog -->
    <el-dialog
      v-model="showTermsDialog"
      :title="$t('auth.termsAndConditions')"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="terms-content">
        <h3>{{ $t('auth.termsTitle') }}</h3>
        <p>{{ $t('auth.termsIntro') }}</p>
        
        <h4>1. {{ $t('auth.termsAcceptance') }}</h4>
        <p>{{ $t('auth.termsAcceptanceContent') }}</p>
        
        <h4>2. {{ $t('auth.termsService') }}</h4>
        <p>{{ $t('auth.termsServiceContent') }}</p>
        
        <h4>3. {{ $t('auth.termsPrivacy') }}</h4>
        <p>{{ $t('auth.termsPrivacyContent') }}</p>
        
        <h4>4. {{ $t('auth.termsLimitations') }}</h4>
        <p>{{ $t('auth.termsLimitationsContent') }}</p>
        
        <h4>5. {{ $t('auth.termsChanges') }}</h4>
        <p>{{ $t('auth.termsChangesContent') }}</p>
      </div>
      
      <template #footer>
        <el-button @click="showTermsDialog = false">
          {{ $t('common.close') }}
        </el-button>
        <el-button 
          type="primary" 
          @click="acceptTerms"
        >
          {{ $t('auth.acceptTerms') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled, Message, User, Lock, Check } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'

const { t } = useI18n()
const router = useRouter()
const authStore = useCognitoAuthStore()

const showTermsDialog = ref(false)

// Register form
const registerFormRef = ref()
const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

// Password validation computed properties
const hasMinLength = computed(() => registerForm.password.length >= 8)
const hasUppercase = computed(() => /[A-Z]/.test(registerForm.password))
const hasLowercase = computed(() => /[a-z]/.test(registerForm.password))
const hasNumbers = computed(() => /\d/.test(registerForm.password))

const isPasswordValid = computed(() => 
  hasMinLength.value && hasUppercase.value && hasLowercase.value && hasNumbers.value
)

const isFormValid = computed(() => 
  registerForm.email && 
  registerForm.username && 
  isPasswordValid.value && 
  registerForm.password === registerForm.confirmPassword &&
  registerForm.agreeTerms
)

const registerRules = {
  email: [
    { required: true, message: t('validation.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('validation.emailInvalid'), trigger: 'blur' }
  ],
  username: [
    { required: true, message: t('validation.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 20, message: t('validation.usernameLength'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('validation.passwordRequired'), trigger: 'blur' },
    { 
      validator: (rule: any, value: string, callback: Function) => {
        if (!isPasswordValid.value) {
          callback(new Error(t('validation.passwordInvalid')))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  confirmPassword: [
    { required: true, message: t('validation.confirmPasswordRequired'), trigger: 'blur' },
    { 
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== registerForm.password) {
          callback(new Error(t('validation.passwordMismatch')))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  agreeTerms: [
    { 
      validator: (rule: any, value: boolean, callback: Function) => {
        if (!value) {
          callback(new Error(t('validation.termsRequired')))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
  ]
}

// Handle registration
const handleRegister = async () => {
  try {
    await registerFormRef.value?.validate()
    
    const result = await authStore.register(
      registerForm.email,
      registerForm.password,
      registerForm.username
    )
    
    if (result.needsConfirmation) {
      // Redirect to login with email confirmation flow
      router.push({
        name: 'Login',
        state: {
          showEmailConfirmation: true,
          email: registerForm.email
        }
      })
    } else {
      // Registration complete, redirect to home
      ElMessage.success(t('auth.registrationSuccess'))
      router.push('/')
    }
    
  } catch (error) {
    console.error('Registration failed:', error)
  }
}

// Accept terms and close dialog
const acceptTerms = () => {
  registerForm.agreeTerms = true
  showTermsDialog.value = false
  ElMessage.success(t('auth.termsAccepted'))
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 480px;
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.logo-icon {
  color: #67c23a;
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

.register-form {
  padding: 0 20px 20px 20px;
}

.password-requirements {
  margin-top: 8px;
}

.requirement {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin: 2px 0;
  transition: color 0.3s;
}

.requirement.valid {
  color: #67c23a;
}

.requirement .el-icon {
  opacity: 0.3;
  transition: opacity 0.3s;
}

.requirement.valid .el-icon {
  opacity: 1;
}

.form-actions {
  margin-top: 24px;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
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

.login-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.login-link:hover {
  color: #337ecc;
}

.terms-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 0 16px;
  line-height: 1.6;
}

.terms-content h3 {
  color: #303133;
  margin-bottom: 16px;
}

.terms-content h4 {
  color: #606266;
  margin: 16px 0 8px 0;
  font-size: 14px;
}

.terms-content p {
  color: #909399;
  font-size: 13px;
  margin-bottom: 12px;
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

:deep(.el-checkbox__label) {
  font-size: 14px;
  line-height: 1.5;
}
</style>