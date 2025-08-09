<template>
  <div class="projects">
    <div class="page-header">
      <h1>我的项目</h1>
      <p>管理您的DIY项目分析历史</p>
    </div>

    <!-- 项目列表 -->
    <div class="projects-content">
      <el-empty
        description="暂无项目记录"
        :image-size="200"
      >
        <template #description>
          <p>您还没有分析过任何DIY项目</p>
        </template>
        <el-button type="primary" @click="$router.push('/')">
          开始分析项目
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这里可以实现项目历史记录功能
</script>

<style scoped>
.projects {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 12px;
}

.page-header p {
  color: #606266;
  font-size: 1.1rem;
}

.projects-content {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>