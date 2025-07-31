import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建axios实例
const instance = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000',
  timeout: 90000, // 90秒超时，适应AI分析需要更长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求队列管理
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 添加认证token
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // 添加请求时间戳
    config.headers['X-Request-Time'] = new Date().toISOString()
    
    console.log('发送请求:', config.method?.toUpperCase(), config.url, config.data)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url, response.data)
    const { data } = response
    
    // 如果返回的状态码为200或201，说明接口请求成功，可以正常拿到数据
    if (response.status === 200 || response.status === 201) {
      return data
    }
    
    // 其他状态码都当作错误处理
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  async (error) => {
    console.error('响应错误:', error)
    
    const originalRequest = error.config
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权 - 尝试刷新token
          if (!originalRequest._retry) {
            // 如果正在刷新token，将请求加入队列
            if (isRefreshing) {
              return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject })
              }).then(token => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                return instance(originalRequest)
              }).catch(err => {
                return Promise.reject(err)
              })
            }
            
            originalRequest._retry = true
            isRefreshing = true
            
            const authStore = useAuthStore()
            
            try {
              console.log('检测到401错误，尝试刷新token...')
              // 尝试刷新token
              const success = await authStore.refreshToken()
              
              if (success) {
                console.log('Token刷新成功，重新发送请求')
                // 刷新成功，重新发送原请求
                processQueue(null, authStore.token)
                originalRequest.headers.Authorization = `Bearer ${authStore.token}`
                return instance(originalRequest)
              } else {
                console.log('Token刷新失败，清除认证信息')
                // 刷新失败，清除认证信息并跳转登录
                processQueue(error, null)
                await authStore.logout()
                return Promise.reject(error)
              }
            } catch (refreshError) {
              console.error('Token刷新过程中出错:', refreshError)
              // 刷新token失败
              processQueue(refreshError, null)
              await authStore.logout()
              return Promise.reject(refreshError)
            } finally {
              isRefreshing = false
            }
          }
          
          // 如果已经重试过，直接登出
          console.log('Token刷新重试失败，强制登出')
          const authStore = useAuthStore()
          await authStore.logout()
          ElMessage.error('登录已过期，请重新登录')
          break
          
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 422:
          // 参数验证错误
          console.error('422错误详情:', {
            url: error.config.url,
            method: error.config.method,
            data: error.config.data,
            headers: error.config.headers,
            response: data
          })
          
          if (data?.errors && Array.isArray(data.errors)) {
            data.errors.forEach(err => {
              console.error('验证错误:', err)
              ElMessage.error(err.message || err)
            })
          } else {
            console.error('422错误响应:', data)
            ElMessage.error(data?.message || '请求参数错误')
          }
          break
          
        case 429:
          ElMessage.error('请求过于频繁，请稍后重试')
          break
          
        case 500:
          ElMessage.error('服务器内部错误')
          break
          
        case 502:
          ElMessage.error('网关错误')
          break
          
        case 503:
          ElMessage.error('服务暂时不可用')
          break
          
        default:
          ElMessage.error(data?.message || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // 网络错误
      if (error.code === 'ECONNABORTED') {
        ElMessage.error('请求超时，请检查网络连接')
      } else {
        ElMessage.error('网络错误，请检查网络连接')
      }
    } else {
      // 请求配置错误
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 封装请求方法，支持通用配置
const request = (config) => {
  return instance(config)
}

// 便捷方法
request.get = (url, config = {}) => {
  return request({
    method: 'get',
    url,
    ...config
  })
}

request.post = (url, data, config = {}) => {
  return request({
    method: 'post',
    url,
    data,
    ...config
  })
}

request.put = (url, data, config = {}) => {
  return request({
    method: 'put',
    url,
    data,
    ...config
  })
}

request.delete = (url, config = {}) => {
  return request({
    method: 'delete',
    url,
    ...config
  })
}

request.patch = (url, data, config = {}) => {
  return request({
    method: 'patch',
    url,
    data,
    ...config
  })
}

// 文件上传专用方法
request.upload = (url, formData, config = {}) => {
  return request({
    method: 'post',
    url,
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      ...config.headers
    },
    ...config
  })
}

// 下载文件专用方法
request.download = (url, config = {}) => {
  return request({
    method: 'get',
    url,
    responseType: 'blob',
    ...config
  })
}

export default request 