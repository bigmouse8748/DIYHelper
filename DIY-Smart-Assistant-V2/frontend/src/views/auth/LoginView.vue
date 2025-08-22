<template>
  <div class="login-view">
    <h2 class="login-title">Text</h2>
    
    <el-form
      ref="formRef"
      :model="loginForm"
      :rules="rules"
      size="large"
      @submit.prevent="handleLogin"
    >
      <el-form-item prop="email">
        <el-input
          v-model="loginForm.email"
          placeholder="Email"
          prefix-icon="Message"
          type="email"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          placeholder="Password"
          prefix-icon="Lock"
          type="password"
          show-password
          @keyup.enter="handleLogin"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          style="width: 100%"
          :loading="authStore.loading"
          @click="handleLogin"
        >
          Text
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="login-footer">
      <p>
        Text
        <router-link to="/auth/register" class="auth-link">
          Text
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<InstanceType<typeof ElForm>>()

const loginForm = reactive({
  email: '',
  password: ''
})

const rules: FormRules = {
  email: [
    { required: true, message: t('auth.emailRequired'), trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('auth.passwordRequired'), trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    await authStore.login({
      email: loginForm.email,
      password: loginForm.password
    })
    
    ElMessage.success(t('auth.loginSuccess'))
    router.push({ name: 'dashboard' })
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}
</script>

<style scoped>
.login-view {
  width: 100%;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
}

.login-footer p {
  color: #606266;
  margin: 0;
}

.auth-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.auth-link:hover {
  color: #5a6fd8;
  text-decoration: underline;
}

.el-form-item {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
}
</style>