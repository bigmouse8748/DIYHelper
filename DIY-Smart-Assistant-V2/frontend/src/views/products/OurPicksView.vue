<template>
  <div class="our-picks">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="hero-title">Our Top Picks</h1>
          <p class="hero-subtitle">
            Carefully curated tools and products recommended by our experts for DIY enthusiasts
          </p>
          <div class="hero-stats">
            <div class="stat">
              <span class="stat-number">{{ totalProducts || 0 }}</span>
              <span class="stat-label">Curated Products</span>
            </div>
            <div class="stat">
              <span class="stat-number">98%</span>
              <span class="stat-label">Satisfaction Rate</span>
            </div>
            <div class="stat">
              <span class="stat-number">15K+</span>
              <span class="stat-label">Happy Customers</span>
            </div>
          </div>
        </div>
        <div class="hero-illustration">
          <el-icon class="hero-icon"><Star /></el-icon>
        </div>
      </div>
    </section>

    <!-- Filters Section -->
    <section class="filters-section">
      <div class="filters-container">
        <h2 class="filters-title">Find Your Perfect Tool</h2>
        <div class="filters-grid">
          <div class="filter-group">
            <label class="filter-label">Category</label>
            <el-select v-model="filters.category" placeholder="All Categories" @change="applyFilters">
              <el-option label="All Categories" value=""></el-option>
              <el-option label="Power Tools" value="power_tools"></el-option>
              <el-option label="Hand Tools" value="hand_tools"></el-option>
              <el-option label="Hardware" value="hardware"></el-option>
              <el-option label="Safety Equipment" value="safety"></el-option>
            </el-select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Price Range</label>
            <el-select v-model="filters.priceRange" placeholder="Any Price" @change="applyFilters">
              <el-option label="Any Price" value=""></el-option>
              <el-option label="Under $50" value="0-50"></el-option>
              <el-option label="$50 - $150" value="50-150"></el-option>
              <el-option label="$150 - $500" value="150-500"></el-option>
              <el-option label="Over $500" value="500+"></el-option>
            </el-select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Brand</label>
            <el-select v-model="filters.brand" placeholder="All Brands" @change="applyFilters">
              <el-option label="All Brands" value=""></el-option>
              <el-option label="Milwaukee" value="Milwaukee"></el-option>
              <el-option label="DeWalt" value="DeWalt"></el-option>
              <el-option label="Bosch" value="Bosch"></el-option>
              <el-option label="Makita" value="Makita"></el-option>
            </el-select>
          </div>
          
          <div class="filter-group">
            <label class="filter-label">Sort By</label>
            <el-select v-model="filters.sortBy" placeholder="Featured" @change="applyFilters">
              <el-option label="Featured" value="featured"></el-option>
              <el-option label="Price: Low to High" value="price_asc"></el-option>
              <el-option label="Price: High to Low" value="price_desc"></el-option>
              <el-option label="Rating" value="rating"></el-option>
              <el-option label="Newest" value="newest"></el-option>
            </el-select>
          </div>
          
          <div class="filter-actions">
            <el-button @click="clearFilters" text>Clear All</el-button>
          </div>
        </div>
      </div>
    </section>

    <!-- Products Grid -->
    <section class="products-section">
      <div class="products-container">
        <div class="section-header">
          <h2 class="section-title">Our Expert Recommendations</h2>
          <p class="section-subtitle">{{ totalProducts }} products found</p>
        </div>

        <div v-loading="loading" class="products-grid">
          <div 
            v-for="product in paginatedProducts" 
            :key="product.id"
            class="product-card"
            @click="viewProduct(product)"
          >
            <div class="product-image-container">
              <el-image 
                :src="product.image" 
                :alt="product.name"
                class="product-image"
                fit="cover"
                lazy
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              
              <!-- Product Badges -->
              <div class="product-badges">
                <el-tag v-if="product.featured" type="warning" size="small" class="badge">
                  <el-icon><Star /></el-icon>
                  Featured
                </el-tag>
                <el-tag v-if="product.sale" type="danger" size="small" class="badge">
                  Sale
                </el-tag>
              </div>
              
              <!-- Quick Actions -->
              <div class="product-actions">
                <el-button 
                  type="primary" 
                  circle 
                  size="small"
                  @click.stop="addToWishlist(product)"
                >
                  <el-icon><Star /></el-icon>
                </el-button>
                <el-button 
                  type="info" 
                  circle 
                  size="small"
                  @click.stop="shareProduct(product)"
                >
                  <el-icon><Share /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="product-content">
              <div class="product-brand">{{ product.brand }}</div>
              <h3 class="product-name">{{ product.name }}</h3>
              <div class="product-rating">
                <el-rate 
                  v-model="product.rating" 
                  disabled 
                  size="small"
                  :max="5"
                />
                <span class="rating-count">({{ product.reviews }})</span>
              </div>
              
              <div class="product-pricing">
                <div class="price-main">${{ product.price.toFixed(2) }}</div>
                <div v-if="product.originalPrice" class="price-original">
                  ${{ product.originalPrice.toFixed(2) }}
                </div>
              </div>
              
              <div class="product-description">
                {{ product.description }}
              </div>
              
              <div class="product-footer">
                <div class="product-tags">
                  <el-tag 
                    v-for="tag in product.tags.slice(0, 2)" 
                    :key="tag"
                    size="small"
                    type="info"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                
                <div class="product-links">
                  <el-button-group size="small">
                    <el-button 
                      v-for="link in product.purchaseLinks.slice(0, 2)" 
                      :key="link.retailer"
                      type="primary"
                      @click.stop="openPurchaseLink(link.url)"
                    >
                      {{ link.retailer }}
                    </el-button>
                  </el-button-group>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More / Pagination -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 48]"
            :total="totalProducts"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </section>

    <!-- Product Detail Modal -->
    <el-dialog
      v-model="productDetailVisible"
      :title="selectedProduct?.name"
      width="800px"
      class="product-detail-dialog"
    >
      <div v-if="selectedProduct" class="product-detail">
        <div class="detail-image">
          <el-image 
            :src="selectedProduct.image" 
            :alt="selectedProduct.name"
            fit="cover"
          />
        </div>
        <div class="detail-content">
          <div class="detail-brand">{{ selectedProduct.brand }}</div>
          <h2 class="detail-name">{{ selectedProduct.name }}</h2>
          <div class="detail-rating">
            <el-rate 
              v-model="selectedProduct.rating" 
              disabled 
              :max="5"
            />
            <span class="rating-text">{{ selectedProduct.rating }}/5 ({{ selectedProduct.reviews }} reviews)</span>
          </div>
          
          <div class="detail-price">
            <span class="price-current">${{ selectedProduct.price.toFixed(2) }}</span>
            <span v-if="selectedProduct.originalPrice" class="price-original">
              ${{ selectedProduct.originalPrice.toFixed(2) }}
            </span>
          </div>
          
          <div class="detail-description">
            <h4>Description</h4>
            <p>{{ selectedProduct.description }}</p>
          </div>
          
          <div class="detail-features">
            <h4>Key Features</h4>
            <ul>
              <li v-for="feature in selectedProduct.features" :key="feature">
                {{ feature }}
              </li>
            </ul>
          </div>
          
          <div class="detail-purchase">
            <h4>Where to Buy</h4>
            <div class="purchase-links">
              <el-button 
                v-for="link in selectedProduct.purchaseLinks" 
                :key="link.retailer"
                type="primary"
                @click="openPurchaseLink(link.url)"
              >
                Buy at {{ link.retailer }} - ${{ link.price.toFixed(2) }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Star,
  Picture,
  Share
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// State
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const productDetailVisible = ref(false)
const selectedProduct = ref<any>(null)

const filters = reactive({
  category: '',
  priceRange: '',
  brand: '',
  sortBy: 'featured'
})

// Products data from API
const products = ref([])
const totalProducts = ref(0)

// API function to fetch products
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      page_size: pageSize.value.toString(),
      sort_by: filters.sortBy,
      sort_order: 'desc'
    })

    // Add filters if selected
    if (filters.category) params.append('category', filters.category)
    if (filters.priceRange) {
      const [min, max] = filters.priceRange.split('-').map(Number)
      if (filters.priceRange === '500+') {
        params.append('min_price', '500')
      } else {
        params.append('min_price', min.toString())
        params.append('max_price', max.toString())
      }
    }
    if (filters.brand) params.append('search', filters.brand)

    const response = await api.get(`/api/v1/our-picks/public/products?${params}`)
    
    if (response.data.success) {
      // Transform API data to match frontend format
      products.value = response.data.products.map(product => ({
        id: product.id,
        name: product.title,
        brand: product.brand,
        category: product.category,
        price: product.price,
        originalPrice: product.original_price,
        rating: product.rating || 0,
        reviews: product.review_count || 0,
        featured: product.is_featured,
        sale: product.original_price && product.original_price > product.price,
        image: product.image_url || 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=400',
        description: product.description,
        tags: JSON.parse(product.suitable_projects || '["general"]'),
        features: [
          product.description.slice(0, 100) + '...',
          `Category: ${product.category}`,
          `Rating: ${product.rating}/5`,
          `${product.review_count} reviews`
        ],
        purchaseLinks: [
          { retailer: product.retailer, url: product.affiliate_link, price: product.price }
        ]
      }))
      totalProducts.value = response.data.total_count
    }
  } catch (error) {
    console.error('Error fetching products:', error)
    ElMessage.error('Failed to load products')
  } finally {
    loading.value = false
  }
}

// Computed properties (filtering/sorting now done by API)
const filteredProducts = computed(() => products.value)
const paginatedProducts = computed(() => products.value)

// Methods
const applyFilters = () => {
  currentPage.value = 1
  fetchProducts()
}

const clearFilters = () => {
  Object.assign(filters, {
    category: '',
    priceRange: '',
    brand: '',
    sortBy: 'featured'
  })
  currentPage.value = 1
  fetchProducts()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  fetchProducts()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchProducts()
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const viewProduct = (product: any) => {
  selectedProduct.value = product
  productDetailVisible.value = true
}

const addToWishlist = (product: any) => {
  ElMessage.success(`Added ${product.name} to your wishlist!`)
}

const shareProduct = (product: any) => {
  if (navigator.share) {
    navigator.share({
      title: product.name,
      text: `Check out this ${product.name} by ${product.brand}`,
      url: window.location.href
    })
  } else {
    ElMessage.info('Product sharing feature coming soon!')
  }
}

const openPurchaseLink = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

// Lifecycle
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.our-picks {
  min-height: 100vh;
  background: #f8f9fa;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
}

.hero-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 60px;
  align-items: center;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 20px 0;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 20px;
  margin: 0 0 40px 0;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-stats {
  display: flex;
  gap: 40px;
}

.stat {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.hero-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
}

.hero-icon {
  font-size: 150px;
  opacity: 0.3;
}

/* Filters Section */
.filters-section {
  background: white;
  padding: 40px 20px;
  border-bottom: 1px solid #e9ecef;
}

.filters-container {
  max-width: 1200px;
  margin: 0 auto;
}

.filters-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 24px 0;
  text-align: center;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  justify-content: center;
  align-items: end;
}

/* Products Section */
.products-section {
  padding: 60px 20px;
}

.products-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-title {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.section-subtitle {
  color: #606266;
  font-size: 16px;
  margin: 0;
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
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.product-image-container {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 48px;
}

.product-badges {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.badge {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9) !important;
}

.product-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.product-card:hover .product-actions {
  opacity: 1;
}

.product-content {
  padding: 20px;
}

.product-brand {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.rating-count {
  font-size: 12px;
  color: #909399;
}

.product-pricing {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.price-main {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.price-original {
  font-size: 14px;
  color: #909399;
  text-decoration: line-through;
}

.product-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.product-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* Product Detail Modal */
.product-detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.detail-image {
  position: sticky;
  top: 20px;
}

.detail-brand {
  font-size: 14px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.detail-name {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.detail-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.rating-text {
  color: #606266;
}

.detail-price {
  margin-bottom: 24px;
}

.price-current {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  margin-right: 12px;
}

.detail-description,
.detail-features,
.detail-purchase {
  margin-bottom: 24px;
}

.detail-description h4,
.detail-features h4,
.detail-purchase h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.detail-features ul {
  margin: 0;
  padding-left: 20px;
}

.detail-features li {
  margin-bottom: 8px;
  color: #606266;
}

.purchase-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-container {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-stats {
    justify-content: center;
    gap: 20px;
  }
  
  .hero-icon {
    font-size: 100px;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .product-detail {
    grid-template-columns: 1fr;
  }
  
  .detail-image {
    position: static;
  }
}
</style>