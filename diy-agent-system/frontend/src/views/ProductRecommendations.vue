<template>
  <div class="product-recommendations">
    <div class="page-header">
      <div class="header-content">
        <h1>{{ $t('products.title') }}</h1>
        <p class="subtitle">{{ $t('products.subtitle') }}</p>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <!-- Search Section -->
      <div class="search-section">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('products.filters.searchPlaceholder')"
          @input="debounceSearch"
          @clear="clearSearch"
          clearable
          size="large"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- Category Filters -->
      <div class="category-section">
        <span class="filter-label">{{ $t('common.filter') }}:</span>
        <el-button-group>
          <el-button 
            :type="activeCategory === '' ? 'primary' : 'default'"
            @click="setCategory('')"
            size="small"
          >
            {{ $t('products.filters.all') }}
          </el-button>
          <el-button 
            v-for="category in categories" 
            :key="category.value"
            :type="activeCategory === category.value ? 'primary' : 'default'"
            @click="setCategory(category.value)"
            size="small"
          >
            {{ category.label }}
          </el-button>
        </el-button-group>
      </div>
      
      <!-- Advanced Filters -->
      <div class="advanced-filters">
        <div class="filter-row">
          <el-select 
            v-model="activeProjectType" 
            :placeholder="$t('products.filters.allProjectTypes')"
            @change="() => loadProducts(false)"
            clearable
            size="small"
            class="filter-select"
          >
            <el-option 
              v-for="projectType in projectTypes" 
              :key="projectType.value"
              :label="projectType.label" 
              :value="projectType.value"
            />
          </el-select>
          
          <el-select 
            v-model="activeMerchant" 
            :placeholder="$t('products.filters.allMerchants')"
            @change="() => loadProducts(false)"
            clearable
            size="small"
            class="filter-select"
          >
            <el-option 
              v-for="merchant in merchants" 
              :key="merchant.value"
              :label="merchant.label" 
              :value="merchant.value"
            />
          </el-select>
          
          <el-checkbox v-model="featuredOnly" @change="() => loadProducts(false)" class="featured-checkbox">
            {{ $t('products.filters.featuredOnly') }}
          </el-checkbox>
        </div>
        
        <!-- View Toggle -->
        <div class="view-controls">
          <span class="view-label">{{ $t('common.view') }}:</span>
          <el-button-group>
            <el-button 
              :type="viewMode === 'grid' ? 'primary' : 'default'"
              @click="viewMode = 'grid'"
              :icon="Grid"
              size="small"
            >
              {{ $t('products.gridView') }}
            </el-button>
            <el-button 
              :type="viewMode === 'list' ? 'primary' : 'default'"
              @click="viewMode = 'list'"
              :icon="List"
              size="small"
            >
              {{ $t('products.listView') }}
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <!-- Products Grid -->
    <div class="products-section" v-loading="loading">
      <div v-if="!loading && products.length === 0" class="empty-state">
        <el-empty :description="$t('products.noProducts')">
          <div class="empty-actions">
            <el-button @click="() => loadProducts(false)">{{ $t('products.refresh') }}</el-button>
          </div>
        </el-empty>
      </div>
      
      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="products-grid">
        <div 
          v-for="product in products" 
          :key="product.id"
          class="product-card"
          @click="trackView(product.id)"
        >
          <div class="product-image">
            <img 
              :src="product.image_url || getDefaultImage(product.category)" 
              :alt="product.title"
              @error="handleImageError"
            />
            <div v-if="product.is_featured" class="featured-badge">
              <el-tag type="warning" size="small">{{ $t('products.featured') }}</el-tag>
            </div>
            <div v-if="product.discount_percentage" class="discount-badge">
              <el-tag type="danger" size="small">-{{ product.discount_percentage }}%</el-tag>
            </div>
          </div>
          
          <div class="product-content">
            <h3 class="product-title">{{ product.title }}</h3>
            
            <div class="product-meta">
              <div class="brand-info" v-if="product.brand">
                <span class="brand">{{ product.brand }}</span>
                <span v-if="product.model" class="model">{{ product.model }}</span>
              </div>
              
              <div class="rating" v-if="product.rating">
                <el-rate 
                  v-model="product.rating" 
                  disabled 
                  show-score 
                  text-color="#ff9900"
                  score-template="{value}"
                  size="small"
                />
                <span v-if="product.rating_count" class="rating-count">
                  ({{ product.rating_count }})
                </span>
              </div>
              
              <div class="project-types" v-if="product.project_types && product.project_types.length">
                <el-tag 
                  v-for="type in product.project_types" 
                  :key="type" 
                  size="small" 
                  class="project-type-tag"
                >
                  {{ getProjectTypeLabel(type) }}
                </el-tag>
              </div>
            </div>
            
            <div class="product-price">
              <span v-if="product.sale_price" class="sale-price">${{ product.sale_price }}</span>
              <span 
                v-if="product.original_price" 
                :class="['original-price', { 'crossed': product.sale_price }]"
              >
                ${{ product.original_price }}
              </span>
              <span v-if="!product.sale_price && !product.original_price" class="no-price">
                {{ $t('products.priceOnSite') }}
              </span>
            </div>
            
            <div class="product-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="visitStore(product)"
                class="visit-btn"
              >
                {{ $t('products.buyNow') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- List View -->
      <div v-else class="products-list">
        <div 
          v-for="product in products" 
          :key="product.id"
          class="product-list-item"
          @click="trackView(product.id)"
        >
          <div class="product-thumbnail">
            <img 
              :src="product.thumbnail_url || product.image_url || getDefaultImage(product.category)" 
              :alt="product.title"
              @error="handleImageError"
            />
            <div v-if="product.is_featured" class="featured-badge">
              <el-tag type="warning" size="small">{{ $t('products.featured') }}</el-tag>
            </div>
            <div v-if="product.discount_percentage" class="discount-badge">
              <el-tag type="danger" size="small">-{{ product.discount_percentage }}%</el-tag>
            </div>
          </div>
          
          <div class="product-details">
            <div class="product-header">
              <h3 class="product-title">{{ product.title }}</h3>
              <div class="product-price">
                <span v-if="product.sale_price" class="sale-price">${{ product.sale_price }}</span>
                <span 
                  v-if="product.original_price" 
                  :class="['original-price', { 'crossed': product.sale_price }]"
                >
                  ${{ product.original_price }}
                </span>
                <span v-if="!product.sale_price && !product.original_price" class="no-price">
                  {{ $t('products.priceOnSite') }}
                </span>
              </div>
            </div>
            
            <div class="product-info">
              <div class="brand-info" v-if="product.brand">
                <span class="brand">{{ product.brand }}</span>
                <span v-if="product.model" class="model">{{ product.model }}</span>
              </div>
              
              <div class="rating" v-if="product.rating">
                <el-rate 
                  v-model="product.rating" 
                  disabled 
                  show-score 
                  text-color="#ff9900"
                  score-template="{value}"
                  size="small"
                />
                <span v-if="product.rating_count" class="rating-count">
                  ({{ product.rating_count }})
                </span>
              </div>
              
              <div class="project-types" v-if="product.project_types && product.project_types.length">
                <el-tag 
                  v-for="type in product.project_types" 
                  :key="type" 
                  size="small" 
                  class="project-type-tag"
                >
                  {{ getProjectTypeLabel(type) }}
                </el-tag>
              </div>
              
              <p v-if="product.description" class="product-description">{{ product.description }}</p>
            </div>
            
            <div class="product-actions">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="visitStore(product)"
                class="visit-btn"
              >
                {{ $t('products.buyNow') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Load More Button -->
      <div v-if="products.length > 0 && products.length >= pageSize" class="load-more">
        <el-button @click="loadMore" :loading="loadingMore">
          {{ $t('products.loadMore') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, List, Search } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const { t } = useI18n()

// Reactive data
const loading = ref(false)
const loadingMore = ref(false)
const products = ref([])
const categories = ref([])
const merchants = ref([])
const projectTypes = ref([])
const viewMode = ref('grid') // 'grid' or 'list'

// Filters
const activeCategory = ref('')
const activeMerchant = ref('')
const activeProjectType = ref('')
const featuredOnly = ref(false)
const searchQuery = ref('')

// Search debouncing
let searchTimeout: NodeJS.Timeout | null = null

// Pagination
const pageSize = ref(12)
const currentPage = ref(1)

// API base URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadMerchants(), 
    loadProjectTypes(),
    loadProducts(false)
  ])
})

// Add loading flag and request tracking to prevent duplicate calls
let isLoadingProducts = false
let currentRequestId = 0

// Methods
const loadProducts = async (append = false) => {
  // Prevent duplicate calls
  if (isLoadingProducts && !append) {
    console.log('Already loading products, skipping duplicate call')
    return
  }
  
  // Generate unique request ID
  const requestId = ++currentRequestId
  
  try {
    isLoadingProducts = true
    
    if (!append) {
      loading.value = true
      currentPage.value = 1
      console.log(`[${requestId}] Loading products with filters:`, {
        category: activeCategory.value,
        merchant: activeMerchant.value,
        project_type: activeProjectType.value,
        featured_only: featuredOnly.value
      })
    } else {
      loadingMore.value = true
    }
    
    const response = await axios.get(`${API_BASE}/api/products`, {
      params: {
        category: activeCategory.value || undefined,
        merchant: activeMerchant.value || undefined,
        project_type: activeProjectType.value || undefined,
        featured_only: featuredOnly.value,
        search: searchQuery.value.trim() || undefined
      }
    })
    
    // Check if this is still the latest request
    if (requestId !== currentRequestId) {
      console.log(`[${requestId}] Ignoring stale response, current request: ${currentRequestId}`)
      return
    }
    
    if (response.data.success) {
      if (append) {
        products.value = [...products.value, ...response.data.products]
        console.log(`[${requestId}] Appended ${response.data.products.length} products, total now:`, products.value.length)
      } else {
        products.value = response.data.products
        console.log(`[${requestId}] Replaced with ${response.data.products.length} products`)
      }
    }
  } catch (error) {
    // Only show error if this is still the current request
    if (requestId === currentRequestId) {
      console.error(`[${requestId}] Error loading products:`, error)
      ElMessage.error(t('products.errors.loadFailed'))
    }
  } finally {
    // Only update loading state if this is still the current request
    if (requestId === currentRequestId) {
      loading.value = false
      loadingMore.value = false
      isLoadingProducts = false
    }
  }
}

const loadCategories = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/products/categories`)
    if (response.data.success) {
      categories.value = response.data.categories
    }
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadMerchants = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/products/merchants`)
    if (response.data.success) {
      merchants.value = response.data.merchants
    }
  } catch (error) {
    console.error('Error loading merchants:', error)
  }
}

const loadProjectTypes = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/products/project-types`)
    if (response.data.success) {
      projectTypes.value = response.data.project_types
    }
  } catch (error) {
    console.error('Error loading project types:', error)
  }
}

const setCategory = (category: string) => {
  activeCategory.value = category
  loadProducts(false)
}

const loadMore = () => {
  currentPage.value++
  loadProducts(true)
}

const trackView = async (productId: number) => {
  try {
    await axios.post(`${API_BASE}/api/products/${productId}/view`)
  } catch (error) {
    // Silently fail - analytics tracking is not critical
    console.debug('Failed to track view:', error)
  }
}

const visitStore = async (product: any) => {
  try {
    // Track click
    await axios.post(`${API_BASE}/api/products/${product.id}/click`)
    
    // Open product URL in new tab
    window.open(product.product_url, '_blank', 'noopener,noreferrer')
  } catch (error) {
    // Still open the link even if tracking fails
    window.open(product.product_url, '_blank', 'noopener,noreferrer')
  }
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement
  target.src = '/placeholder-product.jpg' // Fallback image
}

const getDefaultImage = (category: string) => {
  const defaultImages = {
    tools: 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400&h=300&fit=crop',
    materials: 'https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=400&h=300&fit=crop',
    safety: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=300&fit=crop',
    accessories: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop',
    other: 'https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?w=400&h=300&fit=crop'
  }
  return defaultImages[category] || defaultImages.other
}

const getProjectTypeLabel = (projectType: string) => {
  const labelMap = {
    woodworking: 'Woodworking',
    plumbing: 'Plumbing',
    electrical: 'Electrical', 
    automotive: 'Automotive',
    metalworking: 'Metalworking',
    painting: 'Painting',
    general: 'General DIY',
    outdoor: 'Outdoor & Garden',
    home_improvement: 'Home Improvement',
    crafts: 'Arts & Crafts'
  }
  return labelMap[projectType] || projectType
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const debounceSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadProducts(false)
  }, 500) // Debounce search by 500ms
}

const clearSearch = () => {
  searchQuery.value = ''
  loadProducts(false)
}
</script>

<style scoped>
.product-recommendations {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
}

.header-content h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(45deg, #409eff, #67c23a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #606266;
  font-size: 1.1rem;
  margin: 0;
}

.filter-bar {
  margin-bottom: 30px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.search-section {
  margin-bottom: 20px;
}

.search-input {
  max-width: 500px;
}

.search-input .el-input__wrapper {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.category-section {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-label, .view-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
  white-space: nowrap;
}

.advanced-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-select {
  min-width: 140px;
}

.featured-checkbox {
  margin-left: 8px;
}

.view-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  white-space: nowrap;
}

.view-toggle {
  margin-left: 0;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.product-card:hover .product-image img {
  transform: scale(1.05);
}

.featured-badge {
  position: absolute;
  top: 10px;
  left: 10px;
}

.discount-badge {
  position: absolute;
  top: 10px;
  right: 10px;
}

.product-content {
  padding: 20px;
}

.product-title {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-meta {
  margin-bottom: 12px;
}

.brand-info {
  margin-bottom: 8px;
}

.brand {
  font-weight: 600;
  color: #409eff;
}

.model {
  color: #909399;
  font-size: 14px;
  margin-left: 8px;
}

.rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-count {
  color: #909399;
  font-size: 12px;
}

.product-description {
  margin-bottom: 16px;
}

.product-description p {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sale-price {
  font-size: 1.25rem;
  font-weight: bold;
  color: #e6a23c;
}

.original-price {
  font-size: 14px;
  color: #606266;
}

.original-price.crossed {
  text-decoration: line-through;
  color: #c0c4cc;
}

.price-tbd {
  font-size: 14px;
  color: #909399;
  font-style: italic;
}

.product-actions {
  text-align: center;
}

.purchase-btn {
  width: 100%;
  height: 44px;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-actions {
  margin-top: 20px;
}

.load-more {
  text-align: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .product-recommendations {
    padding: 15px;
  }
  
  .filter-bar {
    padding: 16px;
  }
  
  .search-input {
    max-width: 100%;
  }
  
  .category-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .advanced-filters {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .filter-select {
    min-width: auto;
    width: 100%;
  }
  
  .view-controls {
    justify-content: center;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }
  
  .header-content h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}

/* View Toggle Styles */
.view-toggle {
  margin-left: 16px;
}

/* List View Styles */
.products-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.product-list-item {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  gap: 16px;
}

.product-list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.product-thumbnail {
  position: relative;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

.product-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.product-header .product-title {
  flex: 1;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.product-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-description {
  color: #606266;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

.project-types {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.project-type-tag {
  font-size: 0.75rem;
  border-radius: 4px;
}

@media (max-width: 480px) {
  .category-section .el-button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .category-section .el-button-group .el-button {
    margin: 0;
    border-radius: 6px;
    flex: 1;
    min-width: auto;
  }
  
  .product-list-item {
    flex-direction: column;
    text-align: center;
  }
  
  .product-thumbnail {
    width: 100px;
    height: 100px;
    align-self: center;
  }
  
  .product-header {
    flex-direction: column;
    gap: 8px;
  }
}
</style>