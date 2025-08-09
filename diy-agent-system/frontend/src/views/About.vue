<template>
  <div class="about">
    <div class="about-header">
      <h1>关于DIY智能助手</h1>
      <p class="subtitle">基于AI Agent架构的智能DIY项目分析平台</p>
    </div>

    <el-row :gutter="24">
      <el-col :xs="24" :md="12">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><MagicStick /></el-icon>
              <span>智能图像分析</span>
            </div>
          </template>
          <p>使用最新的AI视觉技术，智能识别DIY项目类型、所需材料和工具，为您提供专业的分析结果。</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>智能商品搜索</span>
            </div>
          </template>
          <p>自动搜索多个电商平台，找到最符合您需求的材料和工具，节省您的时间和精力。</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>质量智能评估</span>
            </div>
          </template>
          <p>基于多维度评估算法，分析产品质量、价格合理性、用户评价，为您推荐最优质的商品。</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>Agent协作架构</span>
            </div>
          </template>
          <p>采用模块化Agent架构，每个Agent专注于特定任务，协同工作提供最佳的分析结果。</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="tech-card">
      <template #header>
        <div class="card-header">
          <el-icon><Cpu /></el-icon>
          <span>技术架构</span>
        </div>
      </template>
      
      <div class="tech-content">
        <div class="tech-section">
          <h3>前端技术</h3>
          <div class="tech-tags">
            <el-tag>Vue 3</el-tag>
            <el-tag>TypeScript</el-tag>
            <el-tag>Element Plus</el-tag>
            <el-tag>Vite</el-tag>
            <el-tag>Pinia</el-tag>
          </div>
        </div>

        <div class="tech-section">
          <h3>后端技术</h3>
          <div class="tech-tags">
            <el-tag type="success">FastAPI</el-tag>
            <el-tag type="success">Python 3.11+</el-tag>
            <el-tag type="success">OpenAI API</el-tag>
            <el-tag type="success">Selenium</el-tag>
            <el-tag type="success">SQLite</el-tag>
          </div>
        </div>

        <div class="tech-section">
          <h3>Agent模块</h3>
          <div class="agent-list">
            <div class="agent-item">
              <el-icon><Document /></el-icon>
              <div>
                <h4>图像分析Agent</h4>
                <p>负责分析上传的图片，识别DIY项目内容</p>
              </div>
            </div>
            <div class="agent-item">
              <el-icon><Search /></el-icon>
              <div>
                <h4>商品搜索Agent</h4>
                <p>在多个电商平台搜索相关产品</p>
              </div>
            </div>
            <div class="agent-item">
              <el-icon><Star /></el-icon>
              <div>
                <h4>质量评估Agent</h4>
                <p>评估产品质量和性价比</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="contact-card">
      <template #header>
        <div class="card-header">
          <el-icon><Message /></el-icon>
          <span>联系我们</span>
        </div>
      </template>
      
      <div class="contact-content">
        <p>如果您有任何问题或建议，欢迎与我们联系：</p>
        <div class="contact-info">
          <div class="contact-item">
            <el-icon><Message /></el-icon>
            <span>反馈建议: support@diy-helper.com</span>
          </div>
          <div class="contact-item">
            <el-icon><Link /></el-icon>
            <span>GitHub: github.com/diy-agent-system</span>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {
  MagicStick,
  Search,
  Star,
  Connection,
  Cpu,
  Document,
  Message,
  Link
} from '@element-plus/icons-vue'
</script>

<style scoped>
.about {
  max-width: 1000px;
  margin: 0 auto;
}

.about-header {
  text-align: center;
  margin-bottom: 40px;
}

.about-header h1 {
  font-size: 2.5rem;
  background: linear-gradient(45deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 32px;
}

.feature-card {
  margin-bottom: 24px;
  height: 200px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.tech-card {
  margin-bottom: 24px;
}

.tech-content {
  display: grid;
  gap: 32px;
}

.tech-section h3 {
  margin-bottom: 16px;
  color: #303133;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.agent-list {
  display: grid;
  gap: 16px;
}

.agent-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.agent-item h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.agent-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.contact-card {
  margin-bottom: 24px;
}

.contact-content p {
  margin-bottom: 16px;
  color: #606266;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409eff;
}

@media (max-width: 768px) {
  .about-header h1 {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
}
</style>