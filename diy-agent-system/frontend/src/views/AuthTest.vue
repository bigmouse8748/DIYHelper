<template>
  <div class="auth-test">
    <div class="page-header">
      <h1>🧪 认证系统测试</h1>
      <p>测试Cognito认证和权限系统</p>
    </div>

    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>当前认证状态</span>
          <el-button 
            type="primary" 
            @click="refreshAuth"
            :loading="authStore.isLoading"
          >
            刷新状态
          </el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="认证状态">
          <el-tag :type="authStore.isAuthenticated ? 'success' : 'danger'">
            {{ authStore.isAuthenticated ? '已认证' : '未认证' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户名">
          {{ authStore.currentUser?.username || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ authStore.currentUser?.email || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="用户组">
          <div v-if="authStore.userGroups.length > 0">
            <el-tag
              v-for="group in authStore.userGroups"
              :key="group"
              :type="getGroupTagType(group)"
              size="small"
              style="margin-right: 4px"
            >
              {{ group }}
            </el-tag>
          </div>
          <span v-else>无组</span>
        </el-descriptions-item>
        <el-descriptions-item label="主要组">
          <el-tag :type="getGroupTagType(authStore.currentUser?.group || 'free')">
            {{ authStore.currentUser?.group || 'free' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="管理员权限">
          <el-tag :type="authStore.isAdmin ? 'success' : 'info'">
            {{ authStore.isAdmin ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <el-icon><Key /></el-icon>
          <span>页面访问权限测试</span>
        </div>
      </template>

      <div class="permission-grid">
        <div class="permission-item">
          <h4>🏠 首页</h4>
          <p>所有人可访问</p>
          <el-button @click="testRoute('/')">访问首页</el-button>
        </div>

        <div class="permission-item">
          <h4>🛍️ Product Recommendations</h4>
          <p>所有人可访问</p>
          <el-button @click="testRoute('/products')">访问产品推荐</el-button>
        </div>

        <div class="permission-item">
          <h4>🔧 Tool Identification</h4>
          <p>需要登录 (free/pro/premium/admin)</p>
          <el-button 
            @click="testRoute('/tool-identification')"
            :disabled="!authStore.isAuthenticated"
          >
            访问工具识别
          </el-button>
        </div>

        <div class="permission-item">
          <h4>🤖 DIY Assistant</h4>
          <p>需要登录 (free/pro/premium/admin)</p>
          <el-button 
            @click="testRoute('/diy-assistant')"
            :disabled="!authStore.isAuthenticated"
          >
            访问DIY助手
          </el-button>
        </div>

        <div class="permission-item">
          <h4>📊 Dashboard</h4>
          <p>需要登录</p>
          <el-button 
            @click="testRoute('/dashboard')"
            :disabled="!authStore.isAuthenticated"
          >
            访问个人中心
          </el-button>
        </div>

        <div class="permission-item">
          <h4>⚙️ 产品管理</h4>
          <p>需要管理员权限</p>
          <el-button 
            @click="testRoute('/admin/products')"
            :disabled="!authStore.isAdmin"
          >
            访问产品管理
          </el-button>
        </div>

        <div class="permission-item">
          <h4>👥 用户管理</h4>
          <p>需要管理员权限</p>
          <el-button 
            @click="testRoute('/admin/users')"
            :disabled="!authStore.isAdmin"
          >
            访问用户管理
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <el-icon><Connection /></el-icon>
          <span>API测试</span>
        </div>
      </template>

      <div class="api-test-section">
        <el-button @click="testDebugAuth" :loading="testing">
          测试认证API
        </el-button>
        <el-button @click="testHealthCheck" :loading="testing">
          测试健康检查
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Setting, 
  Key, 
  Connection 
} from '@element-plus/icons-vue'
import { useCognitoAuthStore } from '@/stores/cognitoAuth'
import { debugAuth } from '@/api/debug'

const router = useRouter()
const authStore = useCognitoAuthStore()
const testing = ref(false)

const getGroupTagType = (group: string) => {
  switch (group) {
    case 'admin': return 'danger'
    case 'premium': return 'warning'
    case 'pro': return 'success'
    case 'free': return 'info'
    default: return ''
  }
}

const refreshAuth = async () => {
  try {
    await authStore.initializeAuth()
    ElMessage.success('认证状态已刷新')
  } catch (error: any) {
    ElMessage.error(`刷新失败: ${error.message}`)
  }
}

const testRoute = (path: string) => {
  try {
    router.push(path)
  } catch (error: any) {
    ElMessage.error(`路由跳转失败: ${error.message}`)
  }
}

const testDebugAuth = async () => {
  testing.value = true
  try {
    const result = await debugAuth()
    ElMessage.success(`API测试成功! Admin: ${result.is_admin}`)
  } catch (error: any) {
    ElMessage.error(`API测试失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    testing.value = false
  }
}

const testHealthCheck = async () => {
  testing.value = true
  try {
    const response = await fetch('http://localhost:8001/api/health')
    const result = await response.json()
    ElMessage.success('健康检查成功')
    console.log('Health check result:', result)
  } catch (error: any) {
    ElMessage.error(`健康检查失败: ${error.message}`)
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.auth-test {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.page-header p {
  color: #606266;
  font-size: 14px;
}

.test-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.card-header .el-button {
  margin-left: auto;
}

.permission-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.permission-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  text-align: center;
}

.permission-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.permission-item p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 12px;
}

.api-test-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>