<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="120px"
    class="manual-product-form"
  >
    <el-row :gutter="20">
      <el-col :span="24">
        <el-form-item label="Product Title" prop="title">
          <el-input 
            v-model="formData.title" 
            placeholder="Enter the complete product title"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="Brand" prop="brand">
          <el-input 
            v-model="formData.brand" 
            placeholder="Product brand name"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Model" prop="model">
          <el-input 
            v-model="formData.model" 
            placeholder="Model number or identifier"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="Category" prop="category">
          <el-select v-model="formData.category" style="width: 100%" placeholder="Select category">
            <el-option label="Power Tools" value="power_tools"></el-option>
            <el-option label="Hand Tools" value="hand_tools"></el-option>
            <el-option label="Safety Equipment" value="safety"></el-option>
            <el-option label="Hardware" value="hardware"></el-option>
            <el-option label="Automotive" value="automotive"></el-option>
            <el-option label="Building Materials" value="building_materials"></el-option>
            <el-option label="Plumbing" value="plumbing"></el-option>
            <el-option label="Electrical" value="electrical"></el-option>
            <el-option label="Garden Tools" value="garden_tools"></el-option>
            <el-option label="Other" value="other"></el-option>
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Retailer" prop="retailer">
          <el-select v-model="formData.retailer" style="width: 100%" placeholder="Select retailer">
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
            v-model="formData.price" 
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
            v-model="formData.original_price" 
            :min="0" 
            :precision="2"
            style="width: 100%"
            placeholder="Original price (if on sale)"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="Description" prop="description">
      <el-input 
        v-model="formData.description" 
        type="textarea" 
        :rows="4"
        placeholder="Detailed product description..."
      />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="Rating">
          <el-rate v-model="formData.rating" :max="5" />
          <span class="rating-text">{{ formData.rating || 'No rating' }}</span>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Review Count">
          <el-input-number 
            v-model="formData.review_count" 
            :min="0"
            style="width: 100%"
            placeholder="Number of reviews"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-form-item label="Product Image URL">
      <el-input 
        v-model="formData.image_url" 
        placeholder="https://example.com/product-image.jpg"
      />
    </el-form-item>

    <el-form-item label="Image Preview" v-if="formData.image_url">
      <div class="image-preview">
        <el-image 
          :src="formData.image_url"
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
        v-model="formData.affiliate_link" 
        placeholder="https://retailer.com/product-link"
      />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="Featured Product">
          <el-switch
            v-model="formData.is_featured"
            active-text="Yes"
            inactive-text="No"
          />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="In Stock">
          <el-switch
            v-model="formData.in_stock"
            active-text="Yes"
            inactive-text="No"
          />
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Picture } from '@element-plus/icons-vue'

// Props and emits
const props = defineProps<{
  modelValue: any
  rules?: any
}>()

const emit = defineEmits<{
  'update:modelValue': [value: any]
}>()

// Form ref
const formRef = ref()

// Form data
const formData = ref(props.modelValue)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  formData.value = newValue
}, { deep: true })

// Watch for internal changes
watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

// Expose validation method
defineExpose({
  validate: () => formRef.value?.validate(),
  clearValidate: () => formRef.value?.clearValidate()
})
</script>

<style scoped>
.manual-product-form {
  max-width: 800px;
}

.rating-text {
  margin-left: 10px;
  font-size: 14px;
  color: #666;
}

.image-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.image-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 28px;
  color: #c0c4cc;
  width: 150px;
  height: 150px;
  background-color: #f5f7fa;
  border-radius: 8px;
}
</style>