<template>
  <div class="admin-product-management">
    <div class="page-header">
      <h1>{{ $t('admin.products.title') }}</h1>
      <p class="subtitle">{{ $t('admin.products.subtitle') }}</p>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        {{ $t('admin.products.addProduct') }}
      </el-button>
    </div>

    <!-- Add Product from URL Dialog -->
    <el-dialog 
      v-model="showAddDialog" 
      :title="$t('admin.products.addFromUrl')"
      width="500px"
      @close="resetForm"
    >
      <div class="url-input-section">
        <h4>{{ $t('admin.products.form.pasteUrl') }}</h4>
        <p class="section-description">{{ $t('admin.products.form.urlDescription') }}</p>
        
        <el-form :model="urlForm" :rules="urlRules" ref="urlFormRef">
          <el-form-item prop="product_url">
            <el-input 
              v-model="urlForm.product_url" 
              :placeholder="$t('admin.products.form.urlPlaceholder')"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 5 }"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="urlForm.is_featured">
              {{ $t('admin.products.form.isFeatured') }}
            </el-checkbox>
            <div class="form-hint">{{ $t('admin.products.form.featuredHint') }}</div>
          </el-form-item>
        </el-form>
        
        <div v-if="scrapingPreview" class="scraping-preview">
          <h5>{{ $t('admin.products.preview.title') }}</h5>
          
          <!-- Extraction Status -->
          <div v-if="extractionDetails" class="extraction-status">
            <div class="status-grid">
              <div class="status-item" :class="{ success: extractionDetails.title_extracted, warning: !extractionDetails.title_extracted }">
                <el-icon><Document /></el-icon>
                <span>Title: {{ extractionDetails.title_extracted ? 'Extracted' : 'Generic' }}</span>
              </div>
              <div class="status-item" :class="{ success: extractionDetails.price_extracted, warning: !extractionDetails.price_extracted }">
                <el-icon><Money /></el-icon>
                <span>Price: {{ extractionDetails.price_extracted ? 'Found' : 'Not found' }}</span>
              </div>
              <div class="status-item" :class="{ success: extractionDetails.image_extracted, warning: !extractionDetails.image_extracted }">
                <el-icon><Picture /></el-icon>
                <span>Image: {{ extractionDetails.image_extracted ? 'Found' : 'Not found' }}</span>
              </div>
              <div class="status-item" :class="{ success: extractionDetails.brand_extracted, warning: !extractionDetails.brand_extracted }">
                <el-icon><Star /></el-icon>
                <span>Brand: {{ extractionDetails.brand_extracted ? 'Extracted' : 'Not found' }}</span>
              </div>
            </div>
            <div class="extraction-method">
              <el-tag :type="extractionMethod === 'ai' ? 'success' : extractionMethod === 'basic' ? 'warning' : 'danger'" size="small">
                {{ extractionMethod === 'ai' ? '🤖 AI Extraction' : extractionMethod === 'basic' ? '📄 Basic Extraction' : '⚠️ Fallback Mode' }}
              </el-tag>
            </div>
          </div>
          
          <div class="preview-content">
            <div class="preview-image" v-if="scrapingPreview.image_url">
              <img :src="scrapingPreview.image_url" :alt="scrapingPreview.title" />
            </div>
            <div v-else class="preview-image-placeholder">
              <el-icon><Picture /></el-icon>
              <span>No image extracted</span>
            </div>
            <div class="preview-details">
              <h6>{{ scrapingPreview.title }}</h6>
              <p class="preview-description">{{ scrapingPreview.description }}</p>
              <div class="preview-meta">
                <el-tag v-if="scrapingPreview.brand" size="small">{{ scrapingPreview.brand }}</el-tag>
                <el-tag v-if="scrapingPreview.category" type="success" size="small">{{ scrapingPreview.category }}</el-tag>
                <el-tag v-if="scrapingPreview.merchant" type="warning" size="small">{{ scrapingPreview.merchant }}</el-tag>
                <el-tag v-if="scrapingPreview.project_types && scrapingPreview.project_types.length" type="info" size="small">
                  {{ scrapingPreview.project_types.join(', ') }}
                </el-tag>
              </div>
              <div v-if="scrapingPreview.sale_price || scrapingPreview.original_price" class="preview-price">
                <span v-if="scrapingPreview.sale_price" class="sale-price">${{ scrapingPreview.sale_price }}</span>
                <span v-if="scrapingPreview.original_price" class="original-price">${{ scrapingPreview.original_price }}</span>
              </div>
              <div v-else class="preview-price">
                <span class="no-price">Price not found - check on site</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAddDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button @click="previewProduct" :loading="previewing" v-if="!scrapingPreview">
          {{ $t('admin.products.preview.button') }}
        </el-button>
        <el-button type="primary" @click="saveProductFromUrl" :loading="saving" v-if="scrapingPreview">
          {{ $t('admin.products.create') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Edit Product Dialog (Simplified) -->
    <el-dialog 
      v-model="showEditDialog" 
      :title="$t('admin.products.editProduct')"
      width="600px"
      @close="resetEditForm"
    >
      <el-form :model="editForm" ref="editFormRef" label-width="120px">
        <el-form-item :label="$t('admin.products.form.title')">
          <el-input v-model="editForm.title" />
        </el-form-item>
        
        <el-form-item :label="$t('admin.products.form.description')">
          <el-input v-model="editForm.description" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item :label="$t('admin.products.form.originalPrice')">
              <el-input-number v-model="editForm.original_price" :min="0" :precision="2" :controls="false" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="$t('admin.products.form.salePrice')">
              <el-input-number v-model="editForm.sale_price" :min="0" :precision="2" :controls="false" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-checkbox v-model="editForm.is_featured">{{ $t('admin.products.form.isFeatured') }}</el-checkbox>
          <el-checkbox v-model="editForm.is_active" style="margin-left: 20px;">{{ $t('admin.products.form.isActive') }}</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveProductEdit" :loading="saving">
          {{ $t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Image Upload Dialog -->
    <el-dialog 
      v-model="showImageUploadDialog" 
      :title="$t('admin.products.imageUpload.title')"
      width="500px"
      @close="resetImageUpload"
    >
      <div class="image-upload-section">
        <div v-if="selectedProduct" class="current-product-info">
          <h4>{{ selectedProduct.title }}</h4>
          <div class="current-image" v-if="selectedProduct.image_url">
            <img :src="getImageUrl(selectedProduct.image_url)" :alt="selectedProduct.title" />
            <p>{{ $t('admin.products.imageUpload.currentImage') }}</p>
          </div>
          <div v-else class="no-current-image">
            <el-icon><Picture /></el-icon>
            <p>{{ $t('admin.products.imageUpload.noCurrentImage') }}</p>
          </div>
        </div>
        
        <el-divider>{{ $t('admin.products.imageUpload.uploadNew') }}</el-divider>
        
        <!-- Upload Method Selection -->
        <div class="upload-method-selection">
          <el-radio-group v-model="uploadMethod" @change="clearUploadData">
            <el-radio label="file">{{ $t('admin.products.imageUpload.uploadFile') }}</el-radio>
            <el-radio label="url">{{ $t('admin.products.imageUpload.uploadFromUrl') }}</el-radio>
          </el-radio-group>
        </div>
        
        <!-- File Upload Section -->
        <div v-show="uploadMethod === 'file'" class="file-upload-section">
          <el-upload
          ref="imageUpload"
          :auto-upload="false"
          :on-change="handleImageSelect"
          :before-upload="beforeImageUpload"
          :show-file-list="false"
          accept="image/*"
          drag
          class="image-uploader"
        >
          <div v-if="!selectedImageFile" class="upload-placeholder">
            <el-icon class="upload-icon"><Plus /></el-icon>
            <div class="upload-text">
              <p>{{ $t('admin.products.imageUpload.dragOrClick') }}</p>
              <p class="upload-hint">{{ $t('admin.products.imageUpload.supportedFormats') }}</p>
            </div>
          </div>
          <div v-else class="selected-image-preview">
            <img :src="selectedImagePreview" alt="Selected image" />
            <div class="image-actions">
              <el-button size="small" @click="clearSelectedImage">{{ $t('common.remove') }}</el-button>
            </div>
          </div>
        </el-upload>
        </div>
        
        <!-- URL Upload Section -->
        <div v-show="uploadMethod === 'url'" class="url-upload-section">
          <el-form :model="imageUrlForm" :rules="imageUrlRules" ref="imageUrlFormRef">
            <el-form-item prop="image_url">
              <el-input
                v-model="imageUrlForm.image_url"
                :placeholder="$t('admin.products.imageUpload.urlPlaceholder')"
                @input="handleUrlInput"
                clearable
              >
                <template #prefix>
                  <el-icon><Link /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
          
          <!-- URL Image Preview -->
          <div v-if="urlImagePreview" class="url-image-preview">
            <img :src="urlImagePreview" alt="URL Preview" @load="urlImageLoaded" @error="urlImageErrored" />
            <div class="image-actions">
              <el-button size="small" @click="clearUrlImage">{{ $t('common.remove') }}</el-button>
            </div>
          </div>
          
          <div v-if="urlImageError" class="url-error">
            <el-alert
              :title="$t('admin.products.imageUpload.errors.urlLoadFailed')"
              type="error"
              :closable="false"
              show-icon
            />
          </div>
        </div>
        
        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
          <el-progress :percentage="uploadProgress" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showImageUploadDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          @click="uploadProductImage" 
          :loading="uploading"
          :disabled="!canUpload"
        >
          {{ $t('admin.products.imageUpload.upload') }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Products Table -->
    <div class="products-section">
      <div class="section-header">
        <h2>{{ $t('admin.products.productList') }}</h2>
        <div class="filters">
          <el-select v-model="filterCategory" @change="loadProducts" :placeholder="$t('admin.products.filterByCategory')" clearable>
            <el-option 
              v-for="category in categories" 
              :key="category.value" 
              :label="category.label" 
              :value="category.value"
            />
          </el-select>
          <el-select v-model="filterMerchant" @change="loadProducts" :placeholder="$t('admin.products.filterByMerchant')" clearable>
            <el-option 
              v-for="merchant in merchants" 
              :key="merchant.value" 
              :label="merchant.label" 
              :value="merchant.value"
            />
          </el-select>
          <el-checkbox v-model="includeInactive" @change="loadProducts">{{ $t('admin.products.includeInactive') }}</el-checkbox>
        </div>
      </div>
      
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" :label="$t('admin.products.table.title')" min-width="200">
          <template #default="scope">
            <div class="product-title">
              <span>{{ scope.row.title }}</span>
              <div class="product-meta">
                <el-tag v-if="scope.row.is_featured" type="warning" size="small">{{ $t('admin.products.featured') }}</el-tag>
                <el-tag v-if="!scope.row.is_active" type="danger" size="small">{{ $t('admin.products.inactive') }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" :label="$t('admin.products.table.category')" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="merchant" :label="$t('admin.products.table.merchant')" width="120">
          <template #default="scope">
            <el-tag type="success" size="small">{{ scope.row.merchant }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('admin.products.table.price')" width="120">
          <template #default="scope">
            <div class="price-info">
              <span v-if="scope.row.sale_price" class="sale-price">${{ scope.row.sale_price }}</span>
              <span v-if="scope.row.original_price" class="original-price" :class="{ crossed: scope.row.sale_price }">
                ${{ scope.row.original_price }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('admin.products.table.analytics')" width="120">
          <template #default="scope">
            <div class="analytics">
              <div>{{ $t('admin.products.views') }}: {{ scope.row.view_count || 0 }}</div>
              <div>{{ $t('admin.products.clicks') }}: {{ scope.row.click_count || 0 }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('admin.products.table.actions')" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editProduct(scope.row)">{{ $t('common.edit') }}</el-button>
            <el-button size="small" type="warning" @click="showImageUpload(scope.row)">
              {{ $t('admin.products.addImage') }}
            </el-button>
            <el-popconfirm 
              :title="$t('admin.products.confirmDelete')"
              @confirm="deleteProduct(scope.row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">{{ $t('common.delete') }}</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="!loading && products.length === 0" class="empty-state">
        <el-empty :description="$t('admin.products.noProducts')">
          <el-button type="primary" @click="showAddDialog = true">{{ $t('admin.products.addFirstProduct') }}</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, Money, Picture, Star, Link } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const { t } = useI18n()
const authStore = useAuthStore()
const router = useRouter()

// Check admin access
if (!authStore.isAuthenticated || authStore.currentUser?.membership_level !== 'admin') {
  ElMessage.error(t('admin.accessDenied'))
  router.push('/dashboard')
}

// Reactive data
const loading = ref(false)
const saving = ref(false)
const previewing = ref(false)
const uploading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showImageUploadDialog = ref(false)
const editingProduct = ref(null)
const selectedProduct = ref(null)
const products = ref([])
const categories = ref([])
const merchants = ref([])
const scrapingPreview = ref(null)
const extractionDetails = ref(null)
const extractionMethod = ref('')

// Image upload data
const selectedImageFile = ref(null)
const selectedImagePreview = ref('')
const uploadProgress = ref(0)
const imageUpload = ref()
const uploadMethod = ref('file') // 'file' or 'url'

// URL upload data
const imageUrlForm = reactive({
  image_url: ''
})
const imageUrlFormRef = ref()
const urlImagePreview = ref('')
const urlImageValid = ref(false)
const urlImageError = ref(false)

// Filters
const filterCategory = ref('')
const filterMerchant = ref('')
const includeInactive = ref(true)

// Form data for URL input
const urlFormRef = ref()
const urlForm = reactive({
  product_url: '',
  is_featured: false
})

// Form data for editing
const editFormRef = ref()
const editForm = reactive({
  title: '',
  description: '',
  original_price: null,
  sale_price: null,
  is_featured: false,
  is_active: true
})

// Form validation rules
const urlRules = {
  product_url: [
    { required: true, message: t('admin.products.validation.urlRequired'), trigger: 'blur' },
    { type: 'url', message: t('admin.products.validation.urlInvalid'), trigger: 'blur' }
  ]
}

const imageUrlRules = {
  image_url: [
    { required: true, message: t('admin.products.imageUpload.validation.urlRequired'), trigger: 'blur' },
    { type: 'url', message: t('admin.products.imageUpload.validation.urlInvalid'), trigger: 'blur' }
  ]
}

// API base URL - use backend URL directly since proxy isn't working on port 3003
const API_BASE = import.meta.env.PROD ? 
  (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002') : 
  'http://localhost:8002' // Direct backend URL for development

// Computed properties
const canUpload = computed(() => {
  if (uploadMethod.value === 'file') {
    return selectedImageFile.value !== null
  } else {
    return urlImageValid.value && imageUrlForm.image_url.trim() !== ''
  }
})

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadCategories(),
    loadMerchants(),
    loadProducts()
  ])
})

// Methods
const loadProducts = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('access_token')
    
    const response = await axios.get(`${API_BASE}/api/admin/products`, {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        include_inactive: includeInactive.value
      }
    })
    
    if (response.data.success) {
      let productList = response.data.products
      
      // Apply filters
      if (filterCategory.value) {
        productList = productList.filter(p => p.category === filterCategory.value)
      }
      if (filterMerchant.value) {
        productList = productList.filter(p => p.merchant === filterMerchant.value)
      }
      
      products.value = productList
    }
  } catch (error) {
    console.error('Error loading products:', error)
    ElMessage.error(t('admin.products.errors.loadFailed'))
  } finally {
    loading.value = false
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

const resetForm = () => {
  editingProduct.value = null
  scrapingPreview.value = null
  extractionDetails.value = null
  extractionMethod.value = ''
  Object.assign(urlForm, {
    product_url: '',
    is_featured: false
  })
  if (urlFormRef.value) {
    urlFormRef.value.clearValidate()
  }
}

const resetEditForm = () => {
  editingProduct.value = null
  Object.assign(editForm, {
    title: '',
    description: '',
    original_price: null,
    sale_price: null,
    is_featured: false,
    is_active: true
  })
  if (editFormRef.value) {
    editFormRef.value.clearValidate()
  }
}

const previewProduct = async () => {
  if (!urlFormRef.value) return
  
  try {
    await urlFormRef.value.validate()
    previewing.value = true
    
    const token = localStorage.getItem('access_token')
    
    // Call the scraper endpoint to get preview
    const response = await axios.post(`${API_BASE}/api/admin/products/from-url`, {
      product_url: urlForm.product_url,
      is_featured: urlForm.is_featured
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      scrapingPreview.value = response.data.scraped_data
      extractionDetails.value = response.data.extraction_details
      extractionMethod.value = response.data.extraction_method
      
      // Show success message with extraction info
      const methodText = response.data.extraction_method === 'ai' ? 'AI extraction' : 
                        response.data.extraction_method === 'basic' ? 'Basic extraction' : 
                        response.data.extraction_method === 'google_shopping_search' ? 'Google Shopping search' :
                        response.data.extraction_method === 'web_search_ai' ? 'Web search + AI analysis' :
                        response.data.extraction_method?.includes('enhanced_with') ? 'Enhanced with search' :
                        'Fallback mode'
      ElMessage.success(`${t('admin.products.messages.previewSuccess')} (${methodText})`)
    }
  } catch (error) {
    console.error('Error previewing product:', error)
    ElMessage.error(t('admin.products.errors.previewFailed'))
  } finally {
    previewing.value = false
  }
}

const saveProductFromUrl = async () => {
  if (!scrapingPreview.value) return
  
  try {
    saving.value = true
    
    // Product is already created by the preview call
    ElMessage.success(t('admin.products.messages.createSuccess'))
    showAddDialog.value = false
    resetForm()
    await loadProducts()
  } catch (error) {
    console.error('Error saving product from URL:', error)
    ElMessage.error(t('admin.products.errors.createFailed'))
  } finally {
    saving.value = false
  }
}

const editProduct = (product) => {
  editingProduct.value = product
  Object.assign(editForm, {
    title: product.title,
    description: product.description || '',
    original_price: product.original_price,
    sale_price: product.sale_price,
    is_featured: product.is_featured,
    is_active: product.is_active
  })
  showEditDialog.value = true
}

const saveProductEdit = async () => {
  if (!editingProduct.value) return
  
  try {
    saving.value = true
    
    const token = localStorage.getItem('access_token')
    
    const response = await axios.put(
      `${API_BASE}/api/admin/products/${editingProduct.value.id}`, 
      editForm, 
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    
    if (response.data.success) {
      ElMessage.success(t('admin.products.messages.updateSuccess'))
      showEditDialog.value = false
      resetEditForm()
      await loadProducts()
    }
  } catch (error) {
    console.error('Error updating product:', error)
    ElMessage.error(t('admin.products.errors.updateFailed'))
  } finally {
    saving.value = false
  }
}

const deleteProduct = async (productId) => {
  try {
    const token = localStorage.getItem('access_token')
    
    const response = await axios.delete(`${API_BASE}/api/admin/products/${productId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (response.data.success) {
      ElMessage.success(t('admin.products.messages.deleteSuccess'))
      await loadProducts()
    }
  } catch (error) {
    console.error('Error deleting product:', error)
    ElMessage.error(t('admin.products.errors.deleteFailed'))
  }
}

// Image upload methods
const showImageUpload = (product) => {
  selectedProduct.value = product
  showImageUploadDialog.value = true
  resetImageUpload()
}

const resetImageUpload = () => {
  uploadMethod.value = 'file'
  selectedImageFile.value = null
  selectedImagePreview.value = ''
  uploadProgress.value = 0
  imageUrlForm.image_url = ''
  urlImagePreview.value = ''
  urlImageValid.value = false
  urlImageError.value = false
  if (imageUpload.value) {
    imageUpload.value.clearFiles()
  }
  if (imageUrlFormRef.value) {
    imageUrlFormRef.value.clearValidate()
  }
}

const handleImageSelect = (file) => {
  selectedImageFile.value = file.raw
  
  // Create preview URL
  const reader = new FileReader()
  reader.onload = (e) => {
    selectedImagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error(t('admin.products.imageUpload.errors.notImage'))
    return false
  }
  if (!isLt5M) {
    ElMessage.error(t('admin.products.imageUpload.errors.tooLarge'))
    return false
  }
  return true
}

const clearSelectedImage = () => {
  selectedImageFile.value = null
  selectedImagePreview.value = ''
  if (imageUpload.value) {
    imageUpload.value.clearFiles()
  }
}

// URL upload methods
const clearUploadData = () => {
  selectedImageFile.value = null
  selectedImagePreview.value = ''
  imageUrlForm.image_url = ''
  urlImagePreview.value = ''
  urlImageValid.value = false
  urlImageError.value = false
  if (imageUpload.value) {
    imageUpload.value.clearFiles()
  }
}

const handleUrlInput = () => {
  urlImageError.value = false
  if (imageUrlForm.image_url.trim()) {
    // Debounce URL validation
    setTimeout(() => {
      validateImageUrl()
    }, 500)
  } else {
    urlImagePreview.value = ''
    urlImageValid.value = false
  }
}

const validateImageUrl = () => {
  const url = imageUrlForm.image_url.trim()
  if (!url) {
    urlImagePreview.value = ''
    urlImageValid.value = false
    return
  }
  
  // Check if URL looks like an image
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
  const isImageUrl = imageExtensions.some(ext => url.toLowerCase().includes(ext)) || 
                     url.includes('unsplash.com') || 
                     url.includes('images.') ||
                     url.includes('img.')
  
  if (isImageUrl) {
    urlImagePreview.value = url
  } else {
    urlImageError.value = true
    urlImageValid.value = false
  }
}

const urlImageLoaded = () => {
  urlImageValid.value = true
  urlImageError.value = false
}

const urlImageErrored = () => {
  urlImageValid.value = false
  urlImageError.value = true
  urlImagePreview.value = ''
}

const clearUrlImage = () => {
  imageUrlForm.image_url = ''
  urlImagePreview.value = ''
  urlImageValid.value = false
  urlImageError.value = false
}

const uploadProductImage = async () => {
  if (!selectedProduct.value) {
    return
  }

  try {
    uploading.value = true
    uploadProgress.value = 0
    
    const token = localStorage.getItem('access_token')
    
    if (uploadMethod.value === 'file') {
      if (!selectedImageFile.value) return
      
      const formData = new FormData()
      formData.append('image', selectedImageFile.value)
      formData.append('product_id', selectedProduct.value.id.toString())

      const response = await axios.post(`${API_BASE}/api/admin/products/${selectedProduct.value.id}/upload-image`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }
      })
      
      if (response.data.success) {
        ElMessage.success(t('admin.products.imageUpload.success'))
        showImageUploadDialog.value = false
        resetImageUpload()
        await loadProducts()
      } else {
        ElMessage.error(t('admin.products.imageUpload.errors.uploadFailed'))
      }
    } else {
      // URL method
      if (!urlImageValid.value) return
      
      const response = await axios.post(`${API_BASE}/api/admin/products/${selectedProduct.value.id}/update-image-url`, {
        image_url: imageUrlForm.image_url.trim()
      }, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (response.data.success) {
        ElMessage.success(t('admin.products.imageUpload.success'))
        showImageUploadDialog.value = false
        resetImageUpload()
        await loadProducts()
      } else {
        ElMessage.error(t('admin.products.imageUpload.errors.uploadFailed'))
      }
    }
    
  } catch (error) {
    console.error('Error uploading image:', error)
    ElMessage.error(t('admin.products.imageUpload.errors.uploadFailed'))
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

// Helper function to get correct image URL
const getImageUrl = (imageUrl) => {
  if (!imageUrl) return ''
  
  // If it's already a full URL (starts with http), return as is
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  
  // If it's a relative URL, prepend the API base in production
  if (import.meta.env.PROD) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'
    return baseUrl + imageUrl
  }
  
  // In development, use the proxy
  return imageUrl
}
</script>

<style scoped>
.admin-product-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.subtitle {
  color: #606266;
  margin: 5px 0 0 0;
  font-size: 14px;
}

.products-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #303133;
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filters .el-select {
  width: 150px;
}

.product-title {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.product-meta {
  display: flex;
  gap: 5px;
}

.price-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sale-price {
  font-weight: bold;
  color: #e6a23c;
}

.original-price.crossed {
  text-decoration: line-through;
  color: #909399;
  font-size: 12px;
}

.analytics {
  font-size: 12px;
  color: #606266;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

/* URL Input Section */
.url-input-section {
  padding: 10px 0;
}

.url-input-section h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
}

.section-description {
  color: #606266;
  font-size: 14px;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

/* Scraping Preview */
.scraping-preview {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.scraping-preview h5 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.preview-content {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.preview-image {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.preview-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-details {
  flex: 1;
  min-width: 0;
}

.preview-details h6 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  word-break: break-word;
}

.preview-description {
  color: #606266;
  font-size: 12px;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.preview-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.preview-price {
  display: flex;
  gap: 8px;
  align-items: center;
}

.preview-price .sale-price {
  font-weight: bold;
  color: #e6a23c;
  font-size: 14px;
}

.preview-price .original-price {
  color: #909399;
  font-size: 12px;
  text-decoration: line-through;
}

.preview-price .no-price {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

/* Extraction Status Styles */
.extraction-status {
  margin-bottom: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-item.success {
  background: #f0f9ff;
  color: #059669;
  border: 1px solid #d1fae5;
}

.status-item.warning {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fed7aa;
}

.status-item .el-icon {
  font-size: 14px;
}

.extraction-method {
  text-align: center;
}

.preview-image-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
  font-size: 11px;
  text-align: center;
  flex-shrink: 0;
}

.preview-image-placeholder .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

/* Image Upload Dialog Styles */
.image-upload-section {
  padding: 10px 0;
}

.current-product-info h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.current-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.current-image img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.current-image p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.no-current-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  margin-bottom: 20px;
}

.no-current-image .el-icon {
  font-size: 32px;
  color: #c0c4cc;
}

.no-current-image p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.image-uploader {
  width: 100%;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  border: 2px dashed #c0c4cc;
  border-radius: 8px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-placeholder:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-icon {
  font-size: 32px;
  color: #c0c4cc;
  margin-bottom: 10px;
}

.upload-text {
  text-align: center;
}

.upload-text p {
  margin: 0 0 5px 0;
  color: #606266;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.selected-image-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border: 2px solid #409eff;
  border-radius: 8px;
  background: #f0f9ff;
}

.selected-image-preview img {
  max-width: 200px;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.image-actions {
  display: flex;
  gap: 10px;
}

.upload-progress {
  margin-top: 15px;
}

/* Upload Method Selection */
.upload-method-selection {
  margin-bottom: 20px;
  text-align: center;
}

.file-upload-section,
.url-upload-section {
  margin-top: 15px;
}

/* URL Upload Styles */
.url-upload-section .el-input {
  margin-bottom: 15px;
}

.url-image-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border: 2px solid #67c23a;
  border-radius: 8px;
  background: #f0f9ff;
  margin-top: 10px;
}

.url-image-preview img {
  max-width: 200px;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.url-error {
  margin-top: 10px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .filters {
    flex-wrap: wrap;
  }
  
  .preview-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .preview-image {
    width: 120px;
    height: 120px;
  }
  
  .selected-image-preview img {
    max-width: 150px;
    max-height: 150px;
  }
}
</style>