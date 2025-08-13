<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header v-if="!hideNavigation">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="24"><Tools /></el-icon>
            <span class="logo-text">{{ $t('nav.logo') }}</span>
          </div>
          <div class="nav-right">
            <nav class="nav-menu">
              <router-link to="/" class="nav-link">{{ $t('nav.home') }}</router-link>
              <router-link to="/tool-identification" class="nav-link">{{ $t('nav.toolIdentification') }}</router-link>
              <router-link to="/projects" class="nav-link">{{ $t('nav.projects') }}</router-link>
              <router-link to="/about" class="nav-link">{{ $t('nav.about') }}</router-link>
            </nav>
            
            <!-- User menu or login -->
            <div class="user-section">
              <div v-if="authStore.isAuthenticated" class="user-menu">
                <el-dropdown trigger="click">
                  <span class="user-trigger">
                    <el-icon><User /></el-icon>
                    {{ authStore.currentUser?.username }}
                    <el-icon><ArrowDown /></el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="goToDashboard">
                        <el-icon><User /></el-icon>
                        {{ $t('nav.dashboard') }}
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleLogout" divided>
                        <el-icon><SwitchButton /></el-icon>
                        {{ $t('auth.logout') }}
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
              <div v-else class="auth-buttons">
                <el-button text @click="goToLogin">{{ $t('auth.login') }}</el-button>
                <el-button type="primary" @click="goToRegister">{{ $t('auth.register') }}</el-button>
              </div>
            </div>
            
            <LanguageSwitcher />
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main :class="{ 'no-header': hideNavigation }">
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer v-if="!hideNavigation">
        <div class="footer-content">
          <p>{{ $t('footer.copyright') }}</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Tools, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// Hide navigation on login/register pages
const hideNavigation = computed(() => route.meta?.hideNav === true)

// Methods
const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

const goToDashboard = () => {
  router.push('/dashboard')
}

const handleLogout = () => {
  authStore.logout()
  ElMessage.success(t('auth.logoutSuccess'))
  router.push('/')
}

// Initialize auth on app mount
onMounted(() => {
  authStore.initializeAuth()
})
</script>

<style scoped>
#app {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px !important;
}

.header-content {
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
  font-size: 20px;
  font-weight: 600;
}

.logo-text {
  background: linear-gradient(45deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-trigger:hover {
  background-color: #f5f7fa;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.el-main.no-header {
  padding-top: 0;
}

.nav-menu {
  display: flex;
  gap: 24px;
}

.nav-link {
  color: #606266;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-link:hover {
  color: #409eff;
  background-color: #f0f9ff;
}

.nav-link.router-link-active {
  color: #409eff;
  background-color: #f0f9ff;
}

.el-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
  max-width: 1200px;
  margin: 0 auto;
}

.el-footer {
  background-color: #f8f9fa;
  border-top: 1px solid #e4e7ed;
  height: 60px !important;
  display: flex;
  align-items: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  color: #909399;
  font-size: 14px;
}
</style>