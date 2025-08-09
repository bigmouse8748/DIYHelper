<template>
  <div class="home">
    <!-- 欢迎区域 -->
    <div class="hero-section">
      <h1 class="hero-title">{{ $t('home.title') }}</h1>
      <p class="hero-subtitle">{{ $t('home.subtitle') }}</p>
    </div>

    <!-- 主要功能区域 -->
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Camera /></el-icon>
          <span>{{ $t('home.uploadTitle') }}</span>
        </div>
      </template>

      <!-- 上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          v-model:file-list="fileList"
          :auto-upload="false"
          :multiple="true"
          :limit="4"
          accept="image/*"
          list-type="picture-card"
          :on-exceed="handleExceed"
          :before-upload="beforeUpload"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
        <div class="upload-tip">
          <el-text type="info" size="small">
            {{ $t('home.uploadTip') }}
          </el-text>
        </div>
      </div>

      <!-- 项目描述 -->
      <div class="form-section">
        <el-form :model="form" label-width="120px">
          <el-form-item :label="$t('home.projectDescription')">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              :placeholder="$t('home.projectDescriptionPlaceholder')"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item :label="$t('home.projectType')">
            <el-select
              v-model="form.projectType"
              :placeholder="$t('home.projectTypePlaceholder')"
              style="width: 100%"
            >
              <el-option :label="$t('home.projectTypes.woodworking')" value="woodworking" />
              <el-option :label="$t('home.projectTypes.electronics')" value="electronics" />
              <el-option :label="$t('home.projectTypes.crafts')" value="crafts" />
              <el-option :label="$t('home.projectTypes.homeDecor')" value="home_decor" />
              <el-option :label="$t('home.projectTypes.repair')" value="repair" />
              <el-option :label="$t('home.projectTypes.other')" value="other" />
            </el-select>
          </el-form-item>

          <el-form-item :label="$t('home.budgetRange')">
            <el-select
              v-model="form.budgetRange"
              :placeholder="$t('home.budgetRangePlaceholder')"
              style="width: 100%"
            >
              <el-option :label="$t('home.budgetRanges.under50')" value="under50" />
              <el-option :label="$t('home.budgetRanges[\'50to150\']')" value="50to150" />
              <el-option :label="$t('home.budgetRanges[\'150to300\']')" value="150to300" />
              <el-option :label="$t('home.budgetRanges[\'300to500\']')" value="300to500" />
              <el-option :label="$t('home.budgetRanges.over500')" value="over500" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>

      <!-- 分析按钮 -->
      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :loading="analyzing"
          :disabled="fileList.length === 0"
          @click="analyzeProject"
        >
          <el-icon v-if="!analyzing"><MagicStick /></el-icon>
          {{ analyzing ? $t('home.analyzing') : $t('home.analyzeButton') }}
        </el-button>
      </div>
    </el-card>

    <!-- 分析结果 -->
    <div v-if="analysisResult" class="results-section">
      <AnalysisResults :result="analysisResult" />
    </div>

    <!-- 加载状态 -->
    <div v-if="analyzing" class="loading-section">
      <el-card>
        <div class="loading-content">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <h3>{{ $t('home.loading.analyzing') }}</h3>
          <p>{{ loadingText }}</p>
          <el-progress :percentage="loadingProgress" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import type { UploadInstance, UploadProps, UploadUserFile } from 'element-plus'
import { Camera, Plus, MagicStick, Loading } from '@element-plus/icons-vue'
import AnalysisResults from '@/components/AnalysisResults.vue'
import { analyzeProject as apiAnalyzeProject } from '@/api/analysis'
import type { AnalysisResult } from '@/types'

const { t } = useI18n()

const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadUserFile[]>([])
const analyzing = ref(false)
const analysisResult = ref<AnalysisResult | null>(null)
const loadingText = ref('')
const loadingProgress = ref(0)

const form = reactive({
  description: '',
  projectType: '',
  budgetRange: ''
})

const handleExceed: UploadProps['onExceed'] = (files) => {
  ElMessage.warning(t('home.messages.maxImagesWarning', { count: files.length }))
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error(t('home.messages.imageTypeError'))
    return false
  }
  if (!isLt10M) {
    ElMessage.error(t('home.messages.imageSizeError'))
    return false
  }
  return true
}

const analyzeProject = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning(t('home.messages.uploadError'))
    return
  }

  analyzing.value = true
  loadingProgress.value = 0
  analysisResult.value = null

  try {
    // 模拟加载进度
    const progressSteps = [
      { text: t('home.loading.uploading'), progress: 20 },
      { text: t('home.loading.analyzing'), progress: 40 },
      { text: t('home.loading.searching'), progress: 60 },
      { text: t('home.loading.assessing'), progress: 80 },
      { text: t('home.loading.generating'), progress: 100 }
    ]

    for (const step of progressSteps) {
      loadingText.value = step.text
      loadingProgress.value = step.progress
      await new Promise(resolve => setTimeout(resolve, 1000))
    }

    // 调用API
    const result = await apiAnalyzeProject({
      images: fileList.value.map(file => file.raw!),
      description: form.description,
      projectType: form.projectType,
      budgetRange: form.budgetRange
    })

    analysisResult.value = result
    ElMessage.success(t('home.messages.analysisSuccess'))

    // 滚动到结果区域
    setTimeout(() => {
      const resultsEl = document.querySelector('.results-section')
      if (resultsEl) {
        resultsEl.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)

  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error(t('home.messages.analysisError'))
  } finally {
    analyzing.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 800px;
  margin: 0 auto;
}

.hero-section {
  text-align: center;
  margin-bottom: 40px;
}

.hero-title {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: #606266;
  line-height: 1.6;
}

.upload-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.upload-section {
  margin-bottom: 24px;
}

.upload-tip {
  margin-top: 12px;
  text-align: center;
}

.form-section {
  margin-bottom: 24px;
}

.action-section {
  text-align: center;
}

.loading-section {
  margin-top: 30px;
}

.loading-content {
  text-align: center;
  padding: 40px 20px;
}

.loading-icon {
  font-size: 48px;
  color: #409eff;
  animation: rotate 2s linear infinite;
  margin-bottom: 16px;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-content h3 {
  margin-bottom: 12px;
  color: #303133;
}

.loading-content p {
  color: #606266;
  margin-bottom: 20px;
}

.results-section {
  margin-top: 40px;
}

:deep(.el-upload--picture-card) {
  width: 120px;
  height: 120px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 120px;
  height: 120px;
}
</style>