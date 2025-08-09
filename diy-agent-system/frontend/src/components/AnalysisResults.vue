<template>
  <div class="analysis-results">
    <!-- 项目分析结果 -->
    <el-card v-if="result.imageAnalysis" class="result-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>{{ $t('results.projectAnalysis') }}</span>
        </div>
      </template>

      <div class="analysis-content">
        <div class="project-info">
          <h3>{{ analysis.project_name }}</h3>
          <p class="project-desc">{{ analysis.description }}</p>
          
          <div class="project-meta">
            <el-tag :type="getDifficultyType(analysis.difficulty_level)">
              {{ $t('results.difficulty.label') }}: {{ getDifficultyText(analysis.difficulty_level) }}
            </el-tag>
            <el-tag type="info">
              <el-icon><Clock /></el-icon>
              {{ $t('results.estimatedTime') }}: {{ analysis.estimated_time }}
            </el-tag>
          </div>
        </div>

        <!-- 材料和工具 -->
        <div class="materials-tools">
          <div class="materials-section">
            <h4><el-icon><ShoppingBag /></el-icon> {{ $t('results.materialsNeeded') }}</h4>
            <div v-if="analysis.materials.length > 0" class="items-list">
              <div v-for="(material, index) in analysis.materials" :key="index" class="item-card">
                <div class="item-name">{{ material.name }}</div>
                <div v-if="material.specification" class="item-spec">{{ $t('results.specification') }}: {{ material.specification }}</div>
                <div v-if="material.quantity" class="item-quantity">{{ $t('results.quantity') }}: {{ material.quantity }}</div>
                <div v-if="material.estimated_price_range" class="item-price">
                  {{ $t('results.estimatedPrice') }}: {{ material.estimated_price_range }}
                </div>
              </div>
            </div>
            <el-empty v-else :description="$t('results.noMaterials')" />
          </div>

          <div class="tools-section">
            <h4><el-icon><Tools /></el-icon> {{ $t('results.toolsNeeded') }}</h4>
            <div v-if="analysis.tools.length > 0" class="items-list">
              <div v-for="(tool, index) in analysis.tools" :key="index" class="item-card">
                <div class="item-name">{{ tool.name }}</div>
                <div v-if="tool.necessity" class="item-necessity">
                  <el-tag :type="getNecessityType(tool.necessity)" size="small">
                    {{ $t(`results.necessity.${getNecessityKey(tool.necessity)}`) }}
                  </el-tag>
                </div>
              </div>
            </div>
            <el-empty v-else :description="$t('results.noTools')" />
          </div>
        </div>

        <!-- 安全注意事项 -->
        <div v-if="analysis.safety_notes.length > 0" class="safety-section">
          <h4><el-icon><Warning /></el-icon> {{ $t('results.safetyNotes') }}</h4>
          <ul class="safety-list">
            <li v-for="(note, index) in analysis.safety_notes" :key="index">{{ note }}</li>
          </ul>
        </div>

        <!-- 制作步骤 -->
        <div v-if="analysis.steps.length > 0" class="steps-section">
          <h4><el-icon><List /></el-icon> {{ $t('results.buildingSteps') }}</h4>
          <el-steps direction="vertical" :active="analysis.steps.length">
            <el-step v-for="(step, index) in analysis.steps" :key="index" :title="`${$t('results.stepLabel')} ${index + 1}`" :description="step" />
          </el-steps>
        </div>
      </div>
    </el-card>

    <!-- 产品推荐 -->
    <div v-if="result.productRecommendations.length > 0" class="products-section">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <el-icon><ShoppingCart /></el-icon>
            <span>{{ $t('results.smartRecommendations') }}</span>
          </div>
        </template>

        <div v-for="(group, index) in result.productRecommendations" :key="index" class="product-group">
          <div class="group-header">
            <h4>{{ group.material }}</h4>
            <div class="group-meta">
              <el-tag v-if="group.avg_quality_score" type="success">
                {{ $t('results.averageRating') }}: {{ group.avg_quality_score.toFixed(1) }}
              </el-tag>
              <el-text type="info">{{ $t('results.productsFound', { count: group.total_assessed }) }}</el-text>
            </div>
          </div>

          <div class="products-grid">
            <div
              v-for="(product, pIndex) in group.products.slice(0, 6)"
              :key="pIndex"
              class="product-card"
            >
              <div class="product-image">
                <img
                  :src="product.image_url || '/placeholder.jpg'"
                  :alt="product.title"
                  @error="handleImageError"
                />
                <div class="quality-badge">
                  <el-tag
                    :type="getQualityTagType(product.recommendation_level)"
                    size="small"
                  >
                    {{ $t(`results.recommendations.${product.recommendation_level}`) || product.recommendation_level }}
                  </el-tag>
                </div>
              </div>
              
              <div class="product-info">
                <div class="product-title" :title="product.title">
                  {{ product.title }}
                </div>
                <div class="product-price">{{ product.price }}</div>
                <div class="product-platform">{{ product.platform }}</div>
                
                <div v-if="product.quality_score" class="product-rating">
                  <el-rate
                    :model-value="product.quality_score"
                    disabled
                    show-score
                    :max="5"
                    :score-template="`{value}${$t('results.scoreUnit')}`"
                  />
                </div>

                <div v-if="product.quality_reasons" class="quality-reasons">
                  <el-tooltip
                    effect="dark"
                    :content="product.quality_reasons.join('；')"
                    placement="top"
                  >
                    <el-button type="info" size="small" text>
                      <el-icon><InfoFilled /></el-icon>
                      {{ $t('results.assessmentDetails') }}
                    </el-button>
                  </el-tooltip>
                </div>

                <div class="product-actions">
                  <el-button
                    type="primary"
                    size="small"
                    @click="openProductLink(product.product_url)"
                  >
                    {{ $t('results.viewProduct') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 总体建议 -->
    <el-card v-if="result.overallRecommendations" class="result-card">
      <template #header>
        <div class="card-header">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ $t('results.shoppingTips') }}</span>
        </div>
      </template>

      <div class="recommendations-content">
        <div class="stats-section">
          <el-statistic :title="$t('results.totalProductsAssessed')" :value="result.overallRecommendations.total_products_assessed" />
          <el-statistic
            :title="$t('results.averageQualityScore')"
            :value="result.overallRecommendations.average_quality_score"
            :precision="1"
            :suffix="$t('results.scoreUnit')"
          />
        </div>

        <div class="tips-section">
          <h4>{{ $t('results.shoppingTips') }}</h4>
          <ul class="tips-list">
            <li v-for="(tip, index) in result.overallRecommendations.shopping_tips" :key="index">
              {{ tip }}
            </li>
          </ul>
        </div>

        <div v-if="result.overallRecommendations.best_products.length > 0" class="best-products">
          <h4>{{ $t('results.bestRecommendations') }}</h4>
          <div class="best-products-list">
            <div
              v-for="(item, index) in result.overallRecommendations.best_products"
              :key="index"
              class="best-product-item"
            >
              <div class="material-name">{{ item.material }}</div>
              <div class="product-summary">
                <span class="product-name">{{ item.product.title }}</span>
                <span class="product-platform">{{ item.product.platform }}</span>
                <el-button
                  type="primary"
                  size="small"
                  text
                  @click="openProductLink(item.product.product_url)"
                >
                  {{ $t('results.viewProduct') }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 分析元数据 -->
    <el-card class="result-card metadata-card">
      <div class="metadata-content">
        <el-descriptions :title="$t('results.analysisInfo')" :column="2" size="small">
          <el-descriptions-item :label="$t('results.totalTime')">
            {{ result.metadata.totalTime.toFixed(1) }}{{ $t('common.seconds') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('results.agentsUsed')">
            {{ result.metadata.agentsUsed.join(', ') }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import {
  Document,
  ShoppingBag,
  Tools,
  Warning,
  List,
  Clock,
  ShoppingCart,
  TrendCharts,
  InfoFilled
} from '@element-plus/icons-vue'
import type { AnalysisResult } from '@/types'

interface Props {
  result: AnalysisResult
}

const props = defineProps<Props>()
const { t } = useI18n()

const analysis = computed(() => props.result.imageAnalysis?.comprehensive_analysis || {
  project_name: 'Unknown Project',
  description: '',
  materials: [],
  tools: [],
  difficulty_level: 'medium',
  estimated_time: 'Unknown',
  safety_notes: [],
  steps: []
})

const getDifficultyType = (level: string) => {
  switch (level) {
    case 'simple': return 'success'
    case 'medium': return 'warning'
    case 'hard': return 'danger'
    default: return 'info'
  }
}

const getDifficultyText = (level: string) => {
  return t(`results.difficulty.${level}`, level)
}

const getNecessityType = (necessity: string) => {
  switch (necessity) {
    case 'Essential':
    case '必需': return 'danger'
    case 'Recommended': 
    case '推荐': return 'warning'
    case 'Optional':
    case '可选': return 'info'
    default: return 'info'
  }
}

const getNecessityKey = (necessity: string) => {
  switch (necessity) {
    case 'Essential':
    case '必需': return 'essential'
    case 'Recommended':
    case '推荐': return 'recommended'
    case 'Optional':
    case '可选': return 'optional'
    default: return 'optional'
  }
}

const getQualityTagType = (level?: string) => {
  switch (level) {
    case 'Professional Choice':
    case 'Highly Recommended':
    case '强烈推荐': return 'success'
    case 'Best Value':
    case 'Safety Essential':
    case 'Recommended':
    case '推荐': return ''
    case 'Good Choice':
    case '一般推荐': return 'warning'
    case '谨慎考虑': return 'danger'
    case '不推荐': return 'info'
    default: return 'info'
  }
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = '/placeholder.jpg'
}

const openProductLink = (url: string) => {
  if (url && url !== '#') {
    window.open(url, '_blank')
  } else {
    ElMessage.warning(t('results.productUnavailable'))
  }
}
</script>

<style scoped>
.analysis-results {
  space-y: 24px;
}

.result-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.analysis-content {
  space-y: 24px;
}

.project-info h3 {
  margin-bottom: 12px;
  color: #303133;
}

.project-desc {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.project-meta {
  display: flex;
  gap: 12px;
}

.materials-tools {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .materials-tools {
    grid-template-columns: 1fr;
  }
}

.materials-section h4,
.tools-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #303133;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item-card {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.item-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.item-spec,
.item-quantity,
.item-price {
  font-size: 14px;
  color: #606266;
}

.safety-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e6a23c;
  margin-bottom: 12px;
}

.safety-list {
  color: #606266;
  padding-left: 20px;
}

.safety-list li {
  margin-bottom: 8px;
}

.steps-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #303133;
}

.product-group {
  margin-bottom: 32px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.group-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.product-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.product-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.product-image {
  position: relative;
  height: 200px;
  background: #f5f7fa;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.quality-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}

.product-info {
  padding: 12px;
}

.product-title {
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.product-price {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.product-platform {
  color: #909399;
  font-size: 12px;
  margin-bottom: 8px;
}

.product-rating {
  margin-bottom: 8px;
}

.quality-reasons {
  margin-bottom: 12px;
}

.product-actions {
  display: flex;
  justify-content: space-between;
}

.recommendations-content {
  space-y: 24px;
}

.stats-section {
  display: flex;
  gap: 48px;
}

.tips-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.tips-list {
  color: #606266;
  padding-left: 20px;
}

.tips-list li {
  margin-bottom: 8px;
}

.best-products h4 {
  margin-bottom: 12px;
  color: #303133;
}

.best-products-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.best-product-item {
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.material-name {
  font-weight: 600;
  margin-bottom: 4px;
  color: #409eff;
}

.product-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-name {
  flex: 1;
  color: #303133;
}

.product-platform {
  color: #909399;
  font-size: 12px;
}

.metadata-card {
  background: #fafafa;
}

.metadata-content {
  color: #606266;
}
</style>