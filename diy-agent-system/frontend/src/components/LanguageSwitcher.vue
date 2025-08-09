<template>
  <el-dropdown @command="handleLanguageChange" class="language-switcher">
    <el-button type="text" class="language-button">
      <el-icon><Setting /></el-icon>
      {{ currentLanguage.nativeName }}
      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item 
          v-for="lang in supportedLanguages" 
          :key="lang.code"
          :command="lang.code"
          :class="{ 'is-active': currentLocale === lang.code }"
        >
          <span class="language-option">
            <span class="language-name">{{ lang.nativeName }}</span>
            <span class="language-code">{{ lang.name }}</span>
          </span>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Setting, ArrowDown } from '@element-plus/icons-vue'
import { switchLanguage, getCurrentLanguage, supportedLanguages } from '@/i18n'
import { ElMessage } from 'element-plus'

const { locale } = useI18n()

const currentLocale = computed(() => getCurrentLanguage())

const currentLanguage = computed(() => {
  return supportedLanguages.find(lang => lang.code === currentLocale.value) || supportedLanguages[0]
})

const handleLanguageChange = (langCode: string) => {
  if (langCode !== currentLocale.value) {
    switchLanguage(langCode)
    
    // 显示切换成功消息
    const message = langCode === 'zh' ? '语言已切换为中文' : 'Language switched to English'
    ElMessage.success(message)
  }
}
</script>

<style scoped>
.language-switcher {
  margin-left: 16px;
}

.language-button {
  color: #606266;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.language-button:hover {
  color: #409eff;
}

.language-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-width: 120px;
}

.language-name {
  font-weight: 500;
}

.language-code {
  color: #909399;
  font-size: 12px;
}

.el-dropdown-menu__item.is-active {
  background-color: #f0f9ff;
  color: #409eff;
}

.el-dropdown-menu__item.is-active .language-code {
  color: #409eff;
}
</style>