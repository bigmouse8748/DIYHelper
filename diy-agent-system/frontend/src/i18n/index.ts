import { createI18n } from 'vue-i18n'
import en from '../locales/en'
import zh from '../locales/zh'

// 获取浏览器语言设置
const getDefaultLocale = () => {
  const browserLang = navigator.language.split('-')[0]
  return ['zh', 'en'].includes(browserLang) ? browserLang : 'en'
}

// 从localStorage获取用户偏好语言
const getUserLocale = () => {
  return localStorage.getItem('locale') || getDefaultLocale()
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API 模式
  locale: getUserLocale(), // 默认语言
  fallbackLocale: 'en', // 回退语言
  globalInjection: true, // 全局注入 $t 函数
  messages: {
    en,
    zh
  }
})

// 切换语言的辅助函数
export const switchLanguage = (locale: string) => {
  i18n.global.locale.value = locale as any
  localStorage.setItem('locale', locale)
  document.documentElement.setAttribute('lang', locale)
}

// 获取当前语言
export const getCurrentLanguage = () => {
  return i18n.global.locale.value
}

// 支持的语言列表
export const supportedLanguages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'zh', name: 'Chinese', nativeName: '中文' }
]

export default i18n