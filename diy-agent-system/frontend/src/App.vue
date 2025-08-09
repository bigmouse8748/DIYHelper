<template>
  <div id="app">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <div class="header-content">
          <div class="logo">
            <el-icon :size="24"><Tools /></el-icon>
            <span class="logo-text">{{ $t('nav.logo') }}</span>
          </div>
          <div class="nav-right">
            <nav class="nav-menu">
              <router-link to="/" class="nav-link">{{ $t('nav.home') }}</router-link>
              <router-link to="/projects" class="nav-link">{{ $t('nav.projects') }}</router-link>
              <router-link to="/about" class="nav-link">{{ $t('nav.about') }}</router-link>
            </nav>
            <LanguageSwitcher />
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main>
        <router-view />
      </el-main>

      <!-- 底部 -->
      <el-footer>
        <div class="footer-content">
          <p>{{ $t('footer.copyright') }}</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
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