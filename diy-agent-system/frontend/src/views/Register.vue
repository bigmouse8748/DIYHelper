<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>{{ $t('auth.createAccount') }}</h1>
        <p>{{ $t('auth.registerSubtitle') }}</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        size="large"
      >
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            :placeholder="$t('auth.email')"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            :placeholder="$t('auth.username')"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            :placeholder="$t('auth.password')"
            :prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            :placeholder="$t('auth.confirmPassword')"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="registerForm.acceptTerms" :label="$t('auth.acceptTerms')" />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="register-button"
            :loading="authStore.isLoading"
            @click="handleRegister"
          >
            {{ $t('auth.register') }}
          </el-button>
        </el-form-item>

        <div class="form-footer">
          <span>{{ $t('auth.haveAccount') }}</span>
          <el-link type="primary" @click="goToLogin">
            {{ $t('auth.login') }}
          </el-link>
        </div>
      </el-form>

      <!-- Membership info -->
      <el-card class="membership-info" shadow="never">
        <div class="membership-content">
          <h3>{{ $t('membership.freeMembershipIncluded') }}</h3>
          <ul class="benefit-list">
            <li>
              <el-icon><Check /></el-icon>
              {{ $t('membership.freeFeatures.identifications') }}
            </li>
            <li>
              <el-icon><Check /></el-icon>
              {{ $t('membership.freeFeatures.history') }}
            </li>
            <li>
              <el-icon><Check /></el-icon>
              {{ $t('membership.freeFeatures.alternatives') }}
            </li>
          </ul>
          <p class="upgrade-hint">
            {{ $t('membership.upgradeHint') }}
          </p>
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
import { User, Lock, Message, Check } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const validatePasswordMatch = (rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error(t('auth.passwordMismatch')))
  } else {
    callback()
  }
}

const validateTerms = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error(t('auth.mustAcceptTerms')))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  email: [
    { required: true, message: t('auth.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('auth.emailInvalid'), trigger: 'blur' }
  ],
  username: [
    { required: true, message: t('auth.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 20, message: t('auth.usernameLength'), trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: t('auth.usernameInvalid'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.passwordRequired'), trigger: 'blur' },
    { min: 6, message: t('auth.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('auth.confirmPasswordRequired'), trigger: 'blur' },
    { validator: validatePasswordMatch, trigger: 'blur' }
  ],
  acceptTerms: [
    { validator: validateTerms, trigger: 'change' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    
    await authStore.registerUser(
      registerForm.email,
      registerForm.username,
      registerForm.password
    )
    
    ElMessage.success(t('auth.registerSuccess'))
    
    // Redirect to tool identification page
    router.push('/tool-identification')
  } catch (error: any) {
    ElMessage.error(error.message || t('auth.registerFailed'))
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 450px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.register-header p {
  color: #606266;
  font-size: 14px;
}

.register-form {
  margin-bottom: 24px;
}

.register-button {
  width: 100%;
  height: 44px;
}

.form-footer {
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.membership-info {
  margin-top: 24px;
  background: #f0f9ff;
}

.membership-content h3 {
  color: #303133;
  margin-bottom: 16px;
  font-size: 16px;
  text-align: center;
}

.benefit-list {
  list-style: none;
  padding: 0;
  margin: 0 0 16px 0;
}

.benefit-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  color: #606266;
  font-size: 14px;
}

.benefit-list .el-icon {
  color: #67c23a;
}

.upgrade-hint {
  text-align: center;
  color: #909399;
  font-size: 12px;
  margin: 0;
}
</style>