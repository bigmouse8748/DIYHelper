<template>
  <div class="register-view">
    <h2 class="register-title">Create Account</h2>
    
    <el-form
      ref="formRef"
      :model="registerForm"
      :rules="rules"
      size="large"
      @submit.prevent="handleRegister"
    >
      <el-form-item prop="username">
        <el-input
          v-model="registerForm.username"
          placeholder="Username"
          prefix-icon="User"
        />
      </el-form-item>
      
      <el-form-item prop="email">
        <el-input
          v-model="registerForm.email"
          placeholder="Email"
          prefix-icon="Message"
          type="email"
        />
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input
          v-model="registerForm.password"
          placeholder="Password"
          prefix-icon="Lock"
          type="password"
          show-password
        />
      </el-form-item>
      
      <el-form-item prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          placeholder="Confirm Password"
          prefix-icon="Lock"
          type="password"
          show-password
          @keyup.enter="handleRegister"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button
          type="primary"
          size="large"
          style="width: 100%"
          :loading="authStore.loading"
          @click="handleRegister"
        >
          Sign Up
        </el-button>
      </el-form-item>
    </el-form>
    
    <div class="register-footer">
      <p>
        Already have an account?
        <router-link to="/auth/login" class="auth-link">
          Sign In
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

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, message: 'Username must be at least 3 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Email is required', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    await authStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    })
    
    ElMessage.success('Registration successful!')
    router.push({ name: 'dashboard' })
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}
</script>

<style scoped>
.register-view {
  width: 100%;
}

.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-weight: 600;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
}

.register-footer p {
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