<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="not-found-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>
      <h1 class="not-found-title">404</h1>
      <p class="not-found-message">Page Not Found</p>
      <p class="not-found-description">
        The page you are looking for might have been removed, renamed, or temporarily unavailable.
      </p>
      <div class="not-found-actions">
        <el-button type="primary" @click="$router.push('/')">
          Go Home
        </el-button>
        <el-button @click="$router.back()">
          Go Back
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

.not-found-container {
  text-align: center;
  max-width: 400px;
}

.not-found-icon {
  margin-bottom: 20px;
}

.not-found-icon .el-icon {
  font-size: 80px;
  color: #f56c6c;
}

.not-found-title {
  font-size: 72px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 16px 0;
  line-height: 1;
}

.not-found-message {
  font-size: 24px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 16px 0;
}

.not-found-description {
  font-size: 16px;
  color: #909399;
  line-height: 1.6;
  margin: 0 0 40px 0;
}

.not-found-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>