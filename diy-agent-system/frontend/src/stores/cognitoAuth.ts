/**
 * Cognito Authentication Store using AWS Amplify
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Amplify } from 'aws-amplify'
import { signIn, signUp, signOut, confirmSignUp, resetPassword, confirmResetPassword, fetchAuthSession, getCurrentUser, fetchUserAttributes, type SignInOutput } from 'aws-amplify/auth'
import { awsConfig, USER_GROUPS } from '@/aws-config'
import { ElMessage } from 'element-plus'
import router from '@/router'

// Configure Amplify
Amplify.configure(awsConfig)

export interface User {
  username: string
  email: string
  groups: string[]
  group: string // Primary group (highest permission)
  permissions: typeof USER_GROUPS.free
  attributes?: Record<string, any>
}

export const useCognitoAuthStore = defineStore('cognitoAuth', () => {
  // State
  const currentUser = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const isLoading = ref(false)
  const userGroups = ref<string[]>([])
  
  // Computed
  const userPermissions = computed(() => {
    if (!currentUser.value) return USER_GROUPS.free
    return USER_GROUPS[currentUser.value.group as keyof typeof USER_GROUPS] || USER_GROUPS.free
  })
  
  const isAdmin = computed(() => {
    return userGroups.value.includes('admin')
  })
  
  const isPremium = computed(() => {
    return userGroups.value.includes('premium') || userGroups.value.includes('admin')
  })
  
  const isPro = computed(() => {
    return userGroups.value.includes('pro') || isPremium.value
  })
  
  const canUseToolIdentification = computed(() => {
    return userPermissions.value.tool_identification
  })
  
  const dailyQuota = computed(() => {
    return userPermissions.value.daily_quota
  })
  
  // Actions
  async function register(email: string, password: string, username: string) {
    isLoading.value = true
    try {
      const { userId, isSignUpComplete, nextStep } = await signUp({
        username: email,
        password,
        options: {
          userAttributes: {
            email,
            preferred_username: username
          }
        }
      })
      
      if (nextStep.signUpStep === 'CONFIRM_SIGN_UP') {
        ElMessage.info('Please check your email for verification code')
        return { success: true, needsConfirmation: true, userId }
      }
      
      return { success: true, needsConfirmation: false, userId }
    } catch (error: any) {
      ElMessage.error(error.message || 'Registration failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function confirmEmail(email: string, code: string) {
    isLoading.value = true
    try {
      const { isSignUpComplete } = await confirmSignUp({
        username: email,
        confirmationCode: code
      })
      
      if (isSignUpComplete) {
        ElMessage.success('Email confirmed successfully! You can now log in.')
        return { success: true }
      }
      
      return { success: false }
    } catch (error: any) {
      ElMessage.error(error.message || 'Confirmation failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function login(email: string, password: string) {
    isLoading.value = true
    console.log('🔐 Starting login process for:', email)
    try {
      const result = await signIn({
        username: email,
        password
      })
      
      console.log('🎯 Login result:', {
        isSignedIn: result.isSignedIn,
        nextStep: result.nextStep
      })
      
      if (result.isSignedIn) {
        console.log('✅ Login successful, clearing old tokens and loading user data...')
        
        // Clear old tokens before loading new ones
        localStorage.removeItem('id_token')
        localStorage.removeItem('access_token')
        
        await loadUserData()
        
        // Double check auth state after loading
        console.log('🔍 Final auth state after login:', {
          isAuthenticated: isAuthenticated.value,
          isAdmin: isAdmin.value,
          currentUser: currentUser.value?.username,
          userGroups: userGroups.value
        })
        
        ElMessage.success('Login successful!')
        router.push('/')
        return { success: true }
      }
      
      return { success: false, nextStep: result.nextStep }
    } catch (error: any) {
      console.error('❌ Login failed:', error)
      ElMessage.error(error.message || 'Login failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function logout() {
    console.log('🚪 Manual logout initiated...')
    isLoading.value = true
    try {
      await signOut()
      clearAuthState()
      console.log('✅ Logout completed successfully')
      ElMessage.success('Logged out successfully')
      router.push('/')
    } catch (error: any) {
      console.error('❌ Logout failed:', error)
      ElMessage.error(error.message || 'Logout failed')
      // Clear state anyway on logout error
      clearAuthState()
    } finally {
      isLoading.value = false
    }
  }
  
  async function forgotPassword(email: string) {
    isLoading.value = true
    try {
      const { nextStep } = await resetPassword({
        username: email
      })
      
      if (nextStep.resetPasswordStep === 'CONFIRM_RESET_PASSWORD_WITH_CODE') {
        ElMessage.info('Password reset code sent to your email')
        return { success: true, codeDeliveryDetails: nextStep.codeDeliveryDetails }
      }
      
      return { success: false }
    } catch (error: any) {
      ElMessage.error(error.message || 'Password reset request failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function confirmPasswordReset(email: string, code: string, newPassword: string) {
    isLoading.value = true
    try {
      await confirmResetPassword({
        username: email,
        confirmationCode: code,
        newPassword
      })
      
      ElMessage.success('Password reset successfully!')
      return { success: true }
    } catch (error: any) {
      ElMessage.error(error.message || 'Password reset failed')
      throw error
    } finally {
      isLoading.value = false
    }
  }
  
  async function loadUserData() {
    try {
      console.log('📊 Loading user data from Cognito...')
      const user = await getCurrentUser()
      const attributes = await fetchUserAttributes()
      const session = await fetchAuthSession()
      
      console.log('👤 User info:', {
        username: user.username,
        email: attributes.email
      })
      
      // Extract groups from ID token
      const idToken = session.tokens?.idToken
      const groups = idToken?.payload['cognito:groups'] as string[] || []
      
      console.log('🏷️ User groups from token:', groups)
      
      // Determine primary group (highest permission)
      let primaryGroup = 'free'
      for (const group of ['admin', 'premium', 'pro', 'free']) {
        if (groups.includes(group)) {
          primaryGroup = group
          break
        }
      }
      
      console.log('🎯 Primary group determined:', primaryGroup)
      
      currentUser.value = {
        username: user.username,
        email: attributes.email || '',
        groups: groups,
        group: primaryGroup,
        permissions: USER_GROUPS[primaryGroup as keyof typeof USER_GROUPS],
        attributes
      }
      
      userGroups.value = groups
      isAuthenticated.value = true
      
      // Store tokens for API calls
      if (session.tokens?.idToken) {
        localStorage.setItem('id_token', session.tokens.idToken.toString())
      }
      if (session.tokens?.accessToken) {
        localStorage.setItem('access_token', session.tokens.accessToken.toString())
      }
      
      console.log('✅ User data loaded successfully:', {
        username: user.username,
        groups: groups,
        primaryGroup: primaryGroup,
        isAdmin: groups.includes('admin')
      })
      
    } catch (error) {
      console.error('❌ Failed to load user data:', error)
      clearAuthState()
    }
  }
  
  async function initializeAuth() {
    // Prevent multiple initializations
    if (isLoading.value) {
      console.log('🔄 Auth already initializing, waiting...')
      while (isLoading.value) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      return
    }

    isLoading.value = true
    console.log('🔄 Starting Cognito auth initialization...')
    
    try {
      // Try to get current session
      const session = await fetchAuthSession()
      
      console.log('📄 Session check:', { 
        hasTokens: !!session.tokens,
        hasIdToken: !!session.tokens?.idToken,
        hasAccessToken: !!session.tokens?.accessToken,
        credentials: !!session.credentials
      })
      
      if (session.tokens?.idToken) {
        console.log('✅ Valid session tokens found')
        
        // Load user data from session
        try {
          const user = await getCurrentUser()
          console.log('👤 Current user:', user.username)
          
          const attributes = await fetchUserAttributes()
          const email = attributes.email || ''
          
          // Extract groups from ID token
          const idToken = session.tokens.idToken
          const groups = (idToken.payload['cognito:groups'] as string[]) || []
          
          console.log('🏷️ User groups from token:', groups)
          
          // Determine primary group (highest permission)
          let primaryGroup = 'free'
          for (const group of ['admin', 'premium', 'pro', 'free']) {
            if (groups.includes(group)) {
              primaryGroup = group
              break
            }
          }
          
          console.log('🎯 Primary group:', primaryGroup)
          
          // Set user data
          currentUser.value = {
            username: user.username,
            email: email,
            groups: groups,
            group: primaryGroup,
            permissions: USER_GROUPS[primaryGroup as keyof typeof USER_GROUPS],
            attributes
          }
          
          userGroups.value = groups
          isAuthenticated.value = true
          
          // Store tokens
          localStorage.setItem('id_token', session.tokens.idToken.toString())
          if (session.tokens.accessToken) {
            localStorage.setItem('access_token', session.tokens.accessToken.toString())
          }
          
          console.log('✅ User authentication successful:', {
            username: user.username,
            email: email,
            groups: groups,
            isAdmin: groups.includes('admin')
          })
          
        } catch (userError) {
          console.error('❌ Failed to load user data:', userError)
          throw userError
        }
        
      } else {
        console.log('❌ No valid session tokens found')
        clearAuthState()
      }
      
    } catch (error) {
      console.log('❌ Auth initialization failed:', error)
      clearAuthState()
    } finally {
      isLoading.value = false
      console.log('🏁 Auth initialization complete:', {
        isAuthenticated: isAuthenticated.value,
        isAdmin: isAdmin.value,
        userGroups: userGroups.value,
        username: currentUser.value?.username || 'none'
      })
    }
  }
  
  function clearAuthState() {
    console.log('🧹 Clearing auth state')
    isAuthenticated.value = false
    currentUser.value = null
    userGroups.value = []
    localStorage.removeItem('id_token')
    localStorage.removeItem('access_token')
  }
  
  async function getIdToken(): Promise<string | null> {
    try {
      // Try to get current session first
      let session = await fetchAuthSession()
      
      // If no tokens or tokens expired, try to refresh
      if (!session.tokens?.idToken) {
        console.log('📱 No ID token, trying to refresh session...')
        session = await fetchAuthSession({ forceRefresh: true })
      }
      
      if (session.tokens?.idToken) {
        const token = session.tokens.idToken.toString()
        localStorage.setItem('id_token', token)
        return token
      }
      
      console.log('❌ No valid ID token available')
      return null
    } catch (error) {
      console.error('❌ Failed to get ID token:', error)
      // Don't clear auth state immediately, might be temporary network issue
      return null
    }
  }
  
  async function getAccessToken(): Promise<string | null> {
    try {
      const session = await fetchAuthSession()
      return session.tokens?.accessToken?.toString() || null
    } catch (error) {
      return null
    }
  }
  
  return {
    // State
    currentUser,
    isAuthenticated,
    isLoading,
    userGroups,
    
    // Computed
    userPermissions,
    isAdmin,
    isPremium,
    isPro,
    canUseToolIdentification,
    dailyQuota,
    
    // Actions
    register,
    confirmEmail,
    login,
    logout,
    forgotPassword,
    confirmPasswordReset,
    loadUserData,
    initializeAuth,
    clearAuthState,
    getIdToken,
    getAccessToken
  }
})