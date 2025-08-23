<template>
  <div class="product-management">
    <el-card>
      <template #header>
        <div class="header-section">
          <h2>Product Management</h2>
          <el-button 
            type="primary" 
            @click="showAddProductDialog"
            :icon="Plus"
          >
            Add Product
          </el-button>
        </div>
      </template>

      <!-- Search and Filter Section -->
      <div class="search-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="Search products..."
              @input="handleSearch"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select 
              v-model="categoryFilter" 
              placeholder="Category"
              @change="handleFilter"
              clearable
            >
              <el-option label="All Categories" value=""></el-option>
              <el-option label="Power Tools" value="power_tools"></el-option>
              <el-option label="Hand Tools" value="hand_tools"></el-option>
              <el-option label="Safety Equipment" value="safety"></el-option>
              <el-option label="Hardware" value="hardware"></el-option>
              <el-option label="Automotive" value="automotive"></el-option>
              <el-option label="Other" value="other"></el-option>
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select 
              v-model="retailerFilter" 
              placeholder="Retailer"
              @change="handleFilter"
              clearable
            >
              <el-option label="All Retailers" value=""></el-option>
              <el-option label="Amazon" value="amazon"></el-option>
              <el-option label="Home Depot" value="home_depot"></el-option>
              <el-option label="Lowes" value="lowes"></el-option>
              <el-option label="Walmart" value="walmart"></el-option>
              <el-option label="Other" value="other"></el-option>
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-switch
              v-model="featuredOnly"
              @change="handleFilter"
              active-text="Featured Only"
              inactive-text="All Products"
            />
          </el-col>
          <el-col :span="4">
            <el-button @click="refreshProducts" :icon="Refresh">Refresh</el-button>
          </el-col>
        </el-row>
      </div>

      <!-- Products Table -->
      <el-table 
        :data="products" 
        v-loading="loading"
        stripe
        class="products-table"
      >
        <el-table-column type="index" width="50" />
        
        <el-table-column label="Image" width="100">
          <template #default="scope">
            <el-image
              :src="getImageUrl(scope.row.image_url, scope.row.category)"
              style="width: 60px; height: 60px"
              fit="cover"
              :preview-src-list="scope.row.image_url ? [getImageUrl(scope.row.image_url, scope.row.category)] : []"
            >
              <template #error>
                <div class="image-slot">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column label="Product Info" min-width="300">
          <template #default="scope">
            <div class="product-info">
              <div class="product-title">{{ scope.row.title }}</div>
              <div class="product-brand">{{ scope.row.brand }}</div>
              <div class="product-category">
                <el-tag size="small">{{ formatCategory(scope.row.category) }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Price" width="120">
          <template #default="scope">
            <div class="price-info">
              <div class="current-price">${{ scope.row.price || 'N/A' }}</div>
              <div v-if="scope.row.original_price && scope.row.original_price > scope.row.price" 
                   class="original-price">
                ${{ scope.row.original_price }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Rating" width="120">
          <template #default="scope">
            <div v-if="scope.row.rating">
              <el-rate 
                :model-value="scope.row.rating" 
                disabled 
                size="small"
              />
              <div class="rating-text">{{ scope.row.rating }} ({{ scope.row.review_count || 0 }})</div>
            </div>
            <span v-else class="no-rating">No rating</span>
          </template>
        </el-table-column>

        <el-table-column label="Retailer" width="100">
          <template #default="scope">
            <el-tag :type="getRetailerTagType(scope.row.retailer)">
              {{ formatRetailer(scope.row.retailer) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="Status" width="120">
          <template #default="scope">
            <div class="status-tags">
              <el-tag v-if="scope.row.is_featured" type="warning" size="small">Featured</el-tag>
              <el-tag v-if="scope.row.in_stock" type="success" size="small">In Stock</el-tag>
              <el-tag v-else type="danger" size="small">Out of Stock</el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button @click="editProduct(scope.row)" type="primary" size="small">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button 
                @click="toggleFeatured(scope.row)" 
                :type="scope.row.is_featured ? 'warning' : 'info'" 
                size="small"
              >
                <el-icon><Star /></el-icon>
              </el-button>
              <el-button @click="viewProductLink(scope.row)" type="success" size="small">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button @click="deleteProduct(scope.row)" type="danger" size="small">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalProducts"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Product Dialog -->
    <el-dialog
      v-model="productDialogVisible"
      :title="editingProduct ? 'Edit Product' : 'Add Product'"
      width="800px"
      @close="resetProductForm"
    >
      <!-- Product Addition Method Tabs -->
      <el-tabs v-if="!editingProduct" v-model="activeTab" @tab-click="handleTabClick">
        <!-- Agent-based extraction -->
        <el-tab-pane label="Agent Analysis" name="agent">
          <div class="agent-section">
            <el-alert
              title="Automatic Product Analysis"
              description="Paste a product URL and our AI agent will automatically extract all product information."
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            />
            
            <el-form :model="agentForm" label-width="120px">
              <el-form-item label="Product URL" required>
                <el-input
                  v-model="agentForm.productUrl"
                  placeholder="https://www.amazon.com/dp/..."
                  :disabled="analyzing"
                />
              </el-form-item>
              
              <el-form-item label="Admin Notes">
                <el-input
                  v-model="agentForm.adminNotes"
                  type="textarea"
                  :rows="2"
                  placeholder="Optional notes about this product..."
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="analyzeProduct"
                  :loading="analyzing"
                  :disabled="!agentForm.productUrl"
                >
                  <el-icon><MagicStick /></el-icon>
                  Analyze Product
                </el-button>
              </el-form-item>
            </el-form>

            <!-- Analysis Result -->
            <div v-if="analysisResult" class="analysis-result">
              <el-divider content-position="left">Analysis Result</el-divider>
              
              <el-form :model="analysisResult" label-width="120px">
                <el-row :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="Product Title">
                      <el-input v-model="analysisResult.title" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="Brand">
                      <el-input v-model="analysisResult.brand" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Model">
                      <el-input v-model="analysisResult.model" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="Category">
                      <el-select v-model="analysisResult.category" style="width: 100%">
                        <el-option label="Power Tools" value="power_tools"></el-option>
                        <el-option label="Hand Tools" value="hand_tools"></el-option>
                        <el-option label="Safety Equipment" value="safety"></el-option>
                        <el-option label="Hardware" value="hardware"></el-option>
                        <el-option label="Automotive" value="automotive"></el-option>
                        <el-option label="Other" value="other"></el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Retailer">
                      <el-select v-model="analysisResult.retailer" style="width: 100%">
                        <el-option label="Amazon" value="amazon"></el-option>
                        <el-option label="Home Depot" value="home_depot"></el-option>
                        <el-option label="Lowes" value="lowes"></el-option>
                        <el-option label="Walmart" value="walmart"></el-option>
                        <el-option label="Other" value="other"></el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="Current Price">
                      <el-input-number 
                        v-model="analysisResult.price" 
                        :min="0" 
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Original Price">
                      <el-input-number 
                        v-model="analysisResult.original_price" 
                        :min="0" 
                        :precision="2"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="Description">
                  <el-input 
                    v-model="analysisResult.description" 
                    type="textarea" 
                    :rows="3"
                  />
                </el-form-item>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="Rating">
                      <el-rate v-model="analysisResult.rating" :max="5" />
                      <span class="rating-text">{{ analysisResult.rating || 'N/A' }}</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="Review Count">
                      <el-input-number 
                        v-model="analysisResult.review_count" 
                        :min="0"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="Image URL">
                  <el-input v-model="analysisResult.image_url" />
                </el-form-item>
                
                <el-form-item label="Image Preview" v-if="analysisResult.image_url">
                  <div class="image-preview">
                    <el-image 
                      :src="analysisResult.image_url"
                      style="width: 150px; height: 150px"
                      fit="cover"
                    >
                      <template #error>
                        <div class="image-placeholder">
                          <el-icon><Picture /></el-icon>
                        </div>
                      </template>
                    </el-image>
                  </div>
                </el-form-item>
                
                <el-form-item label="Affiliate Link">
                  <el-input v-model="analysisResult.affiliate_link" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- Manual Entry -->
        <el-tab-pane label="Manual Entry" name="manual">
          <div class="manual-section">
            <el-alert
              title="Manual Product Entry"
              description="Enter product information manually. All required fields must be filled."
              type="info"
              :closable="false"
              style="margin-bottom: 20px"
            />
            
            <el-form
              ref="manualFormRef"
              :model="productForm"
              :rules="productFormRules"
              label-width="120px"
            >
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item label="Product Title" prop="title">
                    <el-input 
                      v-model="productForm.title" 
                      placeholder="Enter the complete product title"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Brand" prop="brand">
                    <el-input 
                      v-model="productForm.brand" 
                      placeholder="Product brand name"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Model" prop="model">
                    <el-input 
                      v-model="productForm.model" 
                      placeholder="Model number or identifier"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Category" prop="category">
                    <el-select v-model="productForm.category" style="width: 100%" placeholder="Select category">
                      <el-option label="Power Tools" value="power_tools"></el-option>
                      <el-option label="Hand Tools" value="hand_tools"></el-option>
                      <el-option label="Safety Equipment" value="safety"></el-option>
                      <el-option label="Hardware" value="hardware"></el-option>
                      <el-option label="Automotive" value="automotive"></el-option>
                      <el-option label="Other" value="other"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Retailer" prop="retailer">
                    <el-select v-model="productForm.retailer" style="width: 100%" placeholder="Select retailer">
                      <el-option label="Amazon" value="amazon"></el-option>
                      <el-option label="Home Depot" value="home_depot"></el-option>
                      <el-option label="Lowes" value="lowes"></el-option>
                      <el-option label="Walmart" value="walmart"></el-option>
                      <el-option label="Other" value="other"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Current Price" prop="price">
                    <el-input-number 
                      v-model="productForm.price" 
                      :min="0" 
                      :precision="2"
                      style="width: 100%"
                      placeholder="0.00"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Original Price">
                    <el-input-number 
                      v-model="productForm.original_price" 
                      :min="0" 
                      :precision="2"
                      style="width: 100%"
                      placeholder="Original price (if on sale)"
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="Description">
                <el-input 
                  v-model="productForm.description" 
                  type="textarea" 
                  :rows="4"
                  placeholder="Detailed product description..."
                />
              </el-form-item>

              <el-form-item label="Image URL">
                <el-input 
                  v-model="productForm.image_url" 
                  placeholder="https://example.com/product-image.jpg"
                />
              </el-form-item>

              <el-form-item label="Affiliate Link" prop="affiliate_link">
                <el-input 
                  v-model="productForm.affiliate_link" 
                  placeholder="https://retailer.com/product-link"
                />
              </el-form-item>

              <el-form-item label="Featured Product">
                <el-switch
                  v-model="productForm.is_featured"
                  active-text="Yes"
                  inactive-text="No"
                />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Edit form (when editing existing product) -->
      <div v-if="editingProduct" class="edit-section">
        <el-alert
          title="Edit Product Information"
          description="Make any necessary changes to the product information. This is especially useful for updating images that weren't captured by the agent or correcting any information."
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />
        
        <el-form
          ref="editFormRef"
          :model="productForm"
          :rules="productFormRules"
          label-width="120px"
        >
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="Product Title" prop="title">
                <el-input 
                  v-model="productForm.title" 
                  placeholder="Enter the complete product title"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Brand" prop="brand">
                <el-input 
                  v-model="productForm.brand" 
                  placeholder="Product brand name"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Model" prop="model">
                <el-input 
                  v-model="productForm.model" 
                  placeholder="Model number or identifier"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Category" prop="category">
                <el-select v-model="productForm.category" style="width: 100%" placeholder="Select category">
                  <el-option label="Power Tools" value="power_tools"></el-option>
                  <el-option label="Hand Tools" value="hand_tools"></el-option>
                  <el-option label="Safety Equipment" value="safety"></el-option>
                  <el-option label="Hardware" value="hardware"></el-option>
                  <el-option label="Automotive" value="automotive"></el-option>
                  <el-option label="Other" value="other"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Retailer" prop="retailer">
                <el-select v-model="productForm.retailer" style="width: 100%" placeholder="Select retailer">
                  <el-option label="Amazon" value="amazon"></el-option>
                  <el-option label="Home Depot" value="home_depot"></el-option>
                  <el-option label="Lowes" value="lowes"></el-option>
                  <el-option label="Walmart" value="walmart"></el-option>
                  <el-option label="Other" value="other"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Current Price" prop="price">
                <el-input-number 
                  v-model="productForm.price" 
                  :min="0" 
                  :precision="2"
                  style="width: 100%"
                  placeholder="0.00"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Original Price">
                <el-input-number 
                  v-model="productForm.original_price" 
                  :min="0" 
                  :precision="2"
                  style="width: 100%"
                  placeholder="Original price (if on sale)"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Description">
            <el-input 
              v-model="productForm.description" 
              type="textarea" 
              :rows="4"
              placeholder="Detailed product description..."
            />
          </el-form-item>

          <el-form-item label="Image URL">
            <el-input 
              v-model="productForm.image_url" 
              placeholder="https://example.com/product-image.jpg"
            />
          </el-form-item>

          <el-form-item label="Current Image" v-if="productForm.image_url">
            <div class="image-preview">
              <el-image 
                :src="productForm.image_url"
                style="width: 150px; height: 150px"
                fit="cover"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>
          </el-form-item>

          <el-form-item label="Affiliate Link" prop="affiliate_link">
            <el-input 
              v-model="productForm.affiliate_link" 
              placeholder="https://retailer.com/product-link"
            />
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Featured Product">
                <el-switch
                  v-model="productForm.is_featured"
                  active-text="Yes"
                  inactive-text="No"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="In Stock">
                <el-switch
                  v-model="productForm.in_stock"
                  active-text="Yes"
                  inactive-text="No"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="productDialogVisible = false">Cancel</el-button>
          <el-button 
            type="primary" 
            @click="handleProductSave"
            :loading="saving"
            :disabled="!canSave"
          >
            {{ editingProduct ? 'Update Product' : (activeTab === 'agent' ? 'Create from Analysis' : 'Create Product') }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Refresh, Edit, Delete, Star, View, Picture, 
  MagicStick 
} from '@element-plus/icons-vue'
import axios from 'axios'
// import ManualProductForm from '@/components/admin/ManualProductForm.vue'
// import EditProductForm from '@/components/admin/EditProductForm.vue'

// API Base URL
const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/v1'

import { useAuthStore } from '@/stores/auth'

// Auth token
const authStore = useAuthStore()
const getAuthToken = () => authStore.accessToken

// Image utility function
const getImageUrl = (imageUrl: string, category: string = 'other') => {
  // If no image URL provided, return category-based placeholder
  if (!imageUrl || imageUrl.includes('placeholder') || imageUrl.includes('B0')) {
    return getCategoryPlaceholder(category)
  }
  
  // If image URL looks valid (starts with http/https and has proper extension)
  if (imageUrl.startsWith('http') && (imageUrl.includes('.jpg') || imageUrl.includes('.png') || imageUrl.includes('.jpeg'))) {
    return imageUrl
  }
  
  // Fallback to category placeholder
  return getCategoryPlaceholder(category)
}

// Category-based placeholder images
const getCategoryPlaceholder = (category: string) => {
  const placeholders = {
    'power_tools': 'https://images.unsplash.com/photo-1572981779307-38b8cabb2407?w=200&h=200&fit=crop',
    'hand_tools': 'https://images.unsplash.com/photo-1609013026095-fb5c540a7290?w=200&h=200&fit=crop',
    'safety': 'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=200&h=200&fit=crop',
    'hardware': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=200&h=200&fit=crop',
    'automotive': 'https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=200&h=200&fit=crop',
    'building_materials': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=200&h=200&fit=crop',
    'plumbing': 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=200&h=200&fit=crop',
    'electrical': 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=200&h=200&fit=crop',
    'garden_tools': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=200&h=200&fit=crop',
    'other': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=200&h=200&fit=crop'
  }
  return placeholders[category as keyof typeof placeholders] || placeholders['other']
}

// Product data and state
const products = ref<any[]>([])
const loading = ref(false)
const totalProducts = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// Search and filter state
const searchQuery = ref('')
const categoryFilter = ref('')
const retailerFilter = ref('')
const featuredOnly = ref(false)

// Dialog state
const productDialogVisible = ref(false)
const editingProduct = ref<any>(null)
const activeTab = ref('agent')
const saving = ref(false)

// Agent analysis state
const analyzing = ref(false)
const analysisResult = ref<any>(null)
const agentForm = reactive({
  productUrl: '',
  adminNotes: ''
})

// Manual/Edit form state
const productForm = reactive({
  title: '',
  brand: '',
  model: '',
  category: '',
  retailer: 'other',
  price: 0,
  original_price: null,
  rating: null,
  review_count: null,
  description: '',
  image_url: '',
  affiliate_link: '',
  is_featured: false,
  in_stock: true
})

// Form validation rules
const productFormRules = {
  title: [
    { required: true, message: 'Product title is required', trigger: 'blur' }
  ],
  category: [
    { required: true, message: 'Category is required', trigger: 'change' }
  ],
  retailer: [
    { required: true, message: 'Retailer is required', trigger: 'change' }
  ],
  affiliate_link: [
    { required: true, message: 'Affiliate link is required', trigger: 'blur' }
  ]
}

// Component refs
const manualFormRef = ref()
const editFormRef = ref()

// Computed properties
const canSave = computed(() => {
  if (editingProduct.value) {
    return productForm.title && productForm.category && productForm.retailer && productForm.affiliate_link
  }
  if (activeTab.value === 'agent') {
    return analysisResult.value && analysisResult.value.title
  }
  return productForm.title && productForm.category && productForm.retailer && productForm.affiliate_link
})

// Methods
const fetchProducts = async () => {
  try {
    loading.value = true
    
    const params = new URLSearchParams()
    params.append('page', currentPage.value.toString())
    params.append('page_size', pageSize.value.toString())
    
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (categoryFilter.value) params.append('category', categoryFilter.value)
    if (retailerFilter.value) params.append('retailer', retailerFilter.value)
    if (featuredOnly.value) params.append('is_featured', 'true')
    
    const response = await axios.get(`${API_BASE_URL}/our-picks/admin/products?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.data) {
      products.value = response.data.products || []
      totalProducts.value = response.data.total_count || 0
    }
  } catch (error) {
    console.error('Failed to fetch products:', error)
    ElMessage.error('Failed to load products')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProducts()
}

const handleFilter = () => {
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
}

const refreshProducts = () => {
  fetchProducts()
}

const showAddProductDialog = () => {
  editingProduct.value = null
  activeTab.value = 'agent'
  resetProductForm()
  productDialogVisible.value = true
}

const editProduct = (product: any) => {
  editingProduct.value = product
  
  // Populate form with existing product data
  Object.assign(productForm, {
    title: product.title || '',
    brand: product.brand || '',
    model: product.model || '',
    category: product.category || 'other',
    retailer: product.retailer || 'other',
    price: product.price || 0,
    original_price: product.original_price,
    rating: product.rating,
    review_count: product.review_count,
    description: product.description || '',
    image_url: product.image_url || '',
    affiliate_link: product.affiliate_link || '',
    is_featured: product.is_featured || false,
    in_stock: product.in_stock !== false
  })
  
  productDialogVisible.value = true
}

const deleteProduct = async (product: any) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${product.title}"?`,
      'Delete Product',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    await axios.delete(`${API_BASE_URL}/our-picks/admin/products/${product.id}`, {
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`
      }
    })
    
    ElMessage.success('Product deleted successfully')
    await fetchProducts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete product:', error)
      ElMessage.error('Failed to delete product')
    }
  }
}

const toggleFeatured = async (product: any) => {
  try {
    const newFeaturedStatus = !product.is_featured
    
    const updateData = new URLSearchParams()
    updateData.append('title', product.title)
    updateData.append('description', product.description || 'Product description')
    updateData.append('brand', product.brand || 'Unknown')
    updateData.append('category', product.category || 'other')
    updateData.append('retailer', product.retailer || 'other')
    updateData.append('affiliate_link', product.affiliate_link || 'https://example.com')
    updateData.append('is_featured', newFeaturedStatus.toString())
    
    await axios.put(`${API_BASE_URL}/our-picks/admin/products/${product.id}`, updateData, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    // Update local state
    product.is_featured = newFeaturedStatus
    ElMessage.success(`Product ${newFeaturedStatus ? 'featured' : 'unfeatured'} successfully`)
  } catch (error) {
    console.error('Failed to toggle featured status:', error)
    ElMessage.error('Failed to update featured status')
  }
}

const viewProductLink = (product: any) => {
  if (product.affiliate_link) {
    window.open(product.affiliate_link, '_blank')
  } else {
    ElMessage.warning('No affiliate link available for this product')
  }
}

const analyzeProduct = async () => {
  if (!agentForm.productUrl) {
    ElMessage.warning('Please enter a product URL')
    return
  }
  
  try {
    analyzing.value = true
    
    const formData = new FormData()
    formData.append('product_url', agentForm.productUrl)
    
    const response = await axios.post(`${API_BASE_URL}/our-picks/analyze`, formData, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      const data = response.data.extracted_data
      analysisResult.value = {
        title: data.title || '',
        brand: data.brand || '',
        model: data.model || '',
        category: data.category_prediction || 'other',
        retailer: data.merchant || 'other',
        price: data.sale_price || data.price || 0,
        original_price: data.original_price,
        rating: data.rating,
        review_count: data.review_count,
        description: data.description || '',
        image_url: data.images?.[0] || data.image_url || '',
        affiliate_link: agentForm.productUrl,
        is_featured: false,
        in_stock: true,
        analysis_id: response.data.analysis_id
      }
      
      ElMessage.success('Product analyzed successfully!')
    } else {
      throw new Error(response.data.error || 'Analysis failed')
    }
  } catch (error) {
    console.error('Product analysis failed:', error)
    ElMessage.error('Failed to analyze product. Please try manual entry.')
  } finally {
    analyzing.value = false
  }
}

const handleProductSave = async () => {
  try {
    saving.value = true
    
    if (editingProduct.value) {
      // Update existing product
      await updateExistingProduct()
    } else if (activeTab.value === 'agent' && analysisResult.value) {
      // Create from agent analysis
      await createFromAnalysis()
    } else {
      // Manual creation
      await createManualProduct()
    }
    
    productDialogVisible.value = false
    await fetchProducts()
    ElMessage.success(editingProduct.value ? 'Product updated successfully!' : 'Product created successfully!')
    
  } catch (error) {
    console.error('Failed to save product:', error)
    ElMessage.error('Failed to save product')
  } finally {
    saving.value = false
  }
}

const updateExistingProduct = async () => {
  const updateData = new URLSearchParams()
  updateData.append('title', productForm.title)
  updateData.append('description', productForm.description || 'Product description')
  updateData.append('brand', productForm.brand || '')
  updateData.append('model', productForm.model || '')
  updateData.append('category', productForm.category)
  updateData.append('retailer', productForm.retailer)
  updateData.append('price', productForm.price?.toString() || '0')
  updateData.append('original_price', productForm.original_price?.toString() || '')
  updateData.append('rating', productForm.rating?.toString() || '')
  updateData.append('review_count', productForm.review_count?.toString() || '')
  updateData.append('image_url', productForm.image_url || '')
  updateData.append('affiliate_link', productForm.affiliate_link)
  updateData.append('is_featured', productForm.is_featured.toString())
  
  await axios.put(`${API_BASE_URL}/our-picks/admin/products/${editingProduct.value.id}`, updateData, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

const createFromAnalysis = async () => {
  const createData = {
    analysis_id: analysisResult.value.analysis_id,
    title: analysisResult.value.title,
    brand: analysisResult.value.brand,
    category: analysisResult.value.category,
    affiliate_link: analysisResult.value.affiliate_link,
    admin_notes: agentForm.adminNotes
  }
  
  await axios.post(`${API_BASE_URL}/our-picks/create`, createData, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    }
  })
}

const createManualProduct = async () => {
  const updateData = new URLSearchParams()
  updateData.append('title', productForm.title)
  updateData.append('description', productForm.description || 'Manually added product')
  updateData.append('brand', productForm.brand || '')
  updateData.append('model', productForm.model || '')
  updateData.append('category', productForm.category)
  updateData.append('retailer', productForm.retailer)
  updateData.append('price', productForm.price?.toString() || '0')
  updateData.append('original_price', productForm.original_price?.toString() || '')
  updateData.append('rating', productForm.rating?.toString() || '')
  updateData.append('review_count', productForm.review_count?.toString() || '')
  updateData.append('image_url', productForm.image_url || '')
  updateData.append('affiliate_link', productForm.affiliate_link)
  updateData.append('is_featured', productForm.is_featured.toString())
  updateData.append('admin_notes', 'Manually created product')
  
  await axios.post(`${API_BASE_URL}/our-picks/manual-create`, updateData, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

const resetProductForm = () => {
  // Reset agent form
  agentForm.productUrl = ''
  agentForm.adminNotes = ''
  analysisResult.value = null
  
  // Reset product form
  Object.assign(productForm, {
    title: '',
    brand: '',
    model: '',
    category: '',
    retailer: 'other',
    price: 0,
    original_price: null,
    rating: null,
    review_count: null,
    description: '',
    image_url: '',
    affiliate_link: '',
    is_featured: false,
    in_stock: true
  })
}

const handleTabClick = () => {
  resetProductForm()
}

// Utility functions
const formatCategory = (category: string) => {
  if (!category) return 'Other'
  return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatRetailer = (retailer: string) => {
  if (!retailer) return 'Other'
  return retailer.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getRetailerTagType = (retailer: string) => {
  const types: { [key: string]: string } = {
    amazon: 'warning',
    home_depot: 'success',
    lowes: 'primary',
    walmart: 'info'
  }
  return types[retailer] || ''
}

// Lifecycle
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-management {
  padding: 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
}

.products-table {
  margin-bottom: 20px;
}

.product-info {
  .product-title {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
    line-height: 1.4;
  }
  
  .product-brand {
    color: #666;
    font-size: 12px;
    margin-bottom: 4px;
  }
}

.price-info {
  .current-price {
    font-weight: 600;
    color: #409eff;
  }
  
  .original-price {
    font-size: 12px;
    color: #999;
    text-decoration: line-through;
  }
}

.rating-text {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

.no-rating {
  color: #999;
  font-size: 12px;
}

.status-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.agent-section {
  .analysis-result {
    margin-top: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 8px;
  }
}

.image-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.image-slot, .image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 28px;
  color: #c0c4cc;
  width: 60px;
  height: 60px;
  background-color: #f5f7fa;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>