import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // ==================== 状态 ====================
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))
  const isLoading = ref(false)
  const loginHistory = ref([])
  
  // ==================== 计算属性 ====================
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userName = computed(() => user.value?.username || '')
  const userEmail = computed(() => user.value?.email || '')
  const userAvatar = computed(() => user.value?.avatar || '')
  
  // ==================== Token管理 ====================
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('access_token', newToken)
    } else {
      localStorage.removeItem('access_token')
    }
  }
  
  const setUser = (userInfo) => {
    user.value = userInfo
    if (userInfo) {
      localStorage.setItem('user_info', JSON.stringify(userInfo))
    } else {
      localStorage.removeItem('user_info')
    }
  }
  
  // ==================== 认证方法 ====================
  
  /**
   * 用户登录
   */
  const login = async (credentials) => {
    try {
      isLoading.value = true
      
      const response = await authApi.login(credentials)
      
      if (response.success) {
        // 保存token和用户信息
        setToken(response.access_token)
        setUser(response.user)
        
        // 启动token刷新定时器
        startTokenRefresh()
        
        return { success: true, message: response.message }
      } else {
        throw new Error(response.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
      throw new Error(error.response?.data?.message || error.message || '登录失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 用户注册
   */
  const register = async (userData) => {
    try {
      isLoading.value = true
      
      const response = await authApi.register(userData)
      
      if (response.success) {
        return { success: true, message: response.message, user: response.user }
      } else {
        throw new Error(response.message || '注册失败')
      }
    } catch (error) {
      console.error('注册失败:', error)
      throw new Error(error.response?.data?.message || error.message || '注册失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 用户登出
   */
  const logout = async () => {
    try {
      // 调用后端登出接口
      if (token.value) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('登出接口调用失败:', error)
    } finally {
      // 无论接口是否成功，都清除本地数据
      setToken('')
      setUser(null)
      loginHistory.value = []
      
      // 停止token刷新
      stopTokenRefresh()
      
      // 跳转到登录页
      window.location.href = '/login'
    }
  }
  
  /**
   * 验证token有效性
   */
  const verifyToken = async () => {
    if (!token.value) {
      return false
    }
    
    try {
      const response = await authApi.verifyToken()
      
      if (response.success) {
        // 更新用户信息
        setUser(response.user)
        return true
      } else {
        // token无效，清除数据
        await logout()
        return false
      }
    } catch (error) {
      console.error('Token验证失败:', error)
      await logout()
      return false
    }
  }
  
  /**
   * 刷新token
   */
  const refreshToken = async () => {
    if (!token.value) {
      console.warn('没有token可刷新')
      return false
    }
    
    try {
      console.log('尝试刷新token...')
      const response = await authApi.refreshToken()
      
      if (response.success) {
        console.log('Token刷新成功')
        setToken(response.access_token)
        return true
      } else {
        console.warn('Token刷新失败:', response.message)
        // 刷新失败，需要重新登录
        await logout()
        return false
      }
    } catch (error) {
      console.error('Token刷新失败:', error)
      // 如果是401错误，说明token确实过期了，需要重新登录
      if (error.response?.status === 401) {
        console.warn('Token已过期，需要重新登录')
        await logout()
      }
      return false
    }
  }
  
  /**
   * 修改密码
   */
  const changePassword = async (passwordData) => {
    try {
      isLoading.value = true
      
      const response = await authApi.changePassword(passwordData)
      
      if (response.success) {
        return { success: true, message: response.message }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('修改密码失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.message || '修改密码失败，请稍后重试' 
      }
    } finally {
      isLoading.value = false
    }
  }
  
  /**
   * 获取登录历史
   */
  const getLoginHistory = async () => {
    try {
      const response = await authApi.getLoginHistory()
      
      if (response.success) {
        loginHistory.value = response.data
        return { success: true, data: response.data }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('获取登录历史失败:', error)
      return { 
        success: false, 
        message: error.response?.data?.message || '获取登录历史失败' 
      }
    }
  }
  
  // ==================== Token自动刷新 ====================
  let refreshTimer = null
  
  const startTokenRefresh = () => {
    // 每20分钟刷新一次token（token有效期24小时）
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    
    refreshTimer = setInterval(async () => {
      if (token.value) {
        const success = await refreshToken()
        if (!success) {
          console.warn('Token自动刷新失败，用户需要重新登录')
        }
      }
    }, 20 * 60 * 1000) // 20分钟
  }
  
  const stopTokenRefresh = () => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
  
  // ==================== 初始化 ====================
  
  /**
   * 初始化认证状态
   */
  const initialize = async () => {
    if (token.value) {
      const isValid = await verifyToken()
      if (isValid) {
        startTokenRefresh()
      }
    }
  }
  
  // ==================== 工具方法 ====================
  
  /**
   * 检查是否需要登录
   */
  const requireAuth = () => {
    if (!isLoggedIn.value) {
      // 保存当前路由，登录后跳转回来
      const currentPath = window.location.pathname
      if (currentPath !== '/login' && currentPath !== '/register') {
        localStorage.setItem('redirect_after_login', currentPath)
      }
      
      return false
    }
    return true
  }
  
  /**
   * 登录后重定向
   */
  const handleLoginRedirect = () => {
    const redirectPath = localStorage.getItem('redirect_after_login')
    if (redirectPath) {
      localStorage.removeItem('redirect_after_login')
      window.location.href = redirectPath
    } else {
      window.location.href = '/dashboard'
    }
  }
  
  /**
   * 获取认证头
   */
  const getAuthHeader = () => {
    return token.value ? { Authorization: `Bearer ${token.value}` } : {}
  }
  
  // ==================== 返回 ====================
  return {
    // 状态
    token,
    user,
    isLoading,
    loginHistory,
    
    // 计算属性
    isLoggedIn,
    userName,
    userEmail,
    userAvatar,
    
    // 方法
    login,
    register,
    logout,
    verifyToken,
    refreshToken,
    changePassword,
    getLoginHistory,
    initialize,
    requireAuth,
    handleLoginRedirect,
    getAuthHeader,
    
    // Token管理
    setToken,
    setUser,
    startTokenRefresh,
    stopTokenRefresh
  }
}) 