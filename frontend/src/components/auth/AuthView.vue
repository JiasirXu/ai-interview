<template>
  <div class="auth-container">
    <!-- 背景图片 -->
    <div class="background-image">
      <img src="@/components/auth/img.jpg" alt="InterviewAI背景" class="bg-img" />
      <div class="bg-overlay"></div>
    </div>
    
    <!-- 右侧登录/注册卡片 -->
    <div class="auth-card">
      <div class="auth-content">
        <!-- 标题 -->
        <div class="auth-header">
          <h1 class="auth-title">InterviewAI</h1>
          <p class="auth-subtitle">智能面试助手，助你成就职业理想</p>
        </div>

        <!-- 登录表单 -->
        <div v-if="isLogin" class="auth-form">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            @submit.prevent="handleLogin"
          >
            <div class="form-item">
              <label class="form-label">账号</label>
              <el-form-item prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入账号"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <div class="input-icon">
                      <el-icon><User /></el-icon>
                    </div>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="form-item">
              <label class="form-label">密码</label>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  class="form-input"
                  show-password
                >
                  <template #prefix>
                    <div class="input-icon">
                      <el-icon><Lock /></el-icon>
                    </div>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="form-footer">
              <span class="switch-text">还没有账号？</span>
              <span class="switch-link" @click="switchToRegister">立即注册</span>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="submit-button"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form>
        </div>

        <!-- 注册表单 -->
        <div v-else class="auth-form">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            @submit.prevent="handleRegister"
          >
            <div class="form-item">
              <label class="form-label">用户名</label>
              <el-form-item prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入用户名"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <div class="input-icon">
                      <el-icon><User /></el-icon>
                    </div>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="form-item">
              <label class="form-label">邮箱</label>
              <el-form-item prop="email">
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  size="large"
                  class="form-input"
                >
                  <template #prefix>
                    <div class="input-icon">
                      <el-icon><Message /></el-icon>
                    </div>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="form-item">
              <label class="form-label">密码</label>
              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  class="form-input"
                  show-password
                >
                  <template #prefix>
                    <div class="input-icon">
                      <el-icon><Lock /></el-icon>
                    </div>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="form-footer">
              <span class="switch-text">已有账号？</span>
              <span class="switch-link" @click="switchToLogin">立即登录</span>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="submit-button"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { User, Message, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const loginFormRef = ref(null)
const registerFormRef = ref(null)

// 判断是否为登录模式
const isLogin = ref(true)

// 根据路由设置初始模式
onMounted(() => {
  if (route.path === '/register') {
    isLogin.value = false
  } else {
    isLogin.value = true
  }
})

// 登录表单
const loginForm = reactive({
  username: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: ''
})

// 登录验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 注册验证规则
const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ]
}

// 切换到登录
const switchToLogin = () => {
  isLogin.value = true
  router.push('/login')
  // 清除注册表单数据
  Object.assign(registerForm, {
    username: '',
    email: '',
    password: ''
  })
}

// 切换到注册
const switchToRegister = () => {
  isLogin.value = false
  router.push('/register')
  // 清除登录表单数据
  Object.assign(loginForm, {
    username: '',
    password: ''
  })
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await authStore.login(loginForm)
    
    ElMessage.success('登录成功')
    
    // 重定向到原来要访问的页面或个人信息页
    const redirect = route.query.redirect || '/profile/personal'
    router.push(redirect)
    
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    await authStore.register(registerForm)
    
    ElMessage.success('注册成功，请使用您的账号登录')
    
    // 切换到登录页面
    switchToLogin()
    
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.message || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.auth-container {
  position: relative;
  width: 1440px;
  height: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  background: #FFFFFF;
  overflow: hidden;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
  
  .bg-img {
    width: 1139px;
    height: 726px;
    object-fit: contain;
    position: absolute;
    top: 87px;
    left: 77px;
  }
  
  .bg-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
  }
}

.auth-card {
  position: relative;
  z-index: 10;
  width: 400px;
  height: auto;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.85) 100%);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-self: center;
  margin-left: auto;
  margin-right: 120px;
}

.auth-content {
  padding: 30px 25px;
}

.auth-header {
  text-align: center;
  margin-bottom: 25px;
  
  .auth-title {
    font-size: 30px;
    font-weight: 700;
    color: #722ED1;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 4px rgba(114, 46, 209, 0.15);
  }
  
  .auth-subtitle {
    font-size: 14px;
    color: #4B5563;
    margin: 0;
    font-weight: 400;
    letter-spacing: 0.2px;
  }
}

  .auth-form {
      .form-item {
    margin-bottom: 16px;
    border: none;
    
    .form-label {
      display: block;
      font-size: 14px;
      font-weight: 500;
      color: #374151;
      margin-bottom: 6px;
      letter-spacing: 0.2px;
    }
      
    .form-input {
      :deep(.el-input__wrapper) {
        border-radius: 8px;
        border: 1px solid rgba(209, 213, 219, 0.5);
        box-shadow: none;
        height: 42px;
        background: rgba(249, 250, 251, 0.7);
        padding: 0;
        
        &:hover {
          border-color: #722ED1;
          background: rgba(249, 250, 251, 0.8);
        }
        
        &.is-focus {
          border-color: #722ED1;
          background: rgba(249, 250, 251, 0.9);
          box-shadow: 0 0 0 2px rgba(114, 46, 209, 0.2);
        }
      }
      
      :deep(.el-input__inner) {
        height: 42px;
        line-height: 42px;
        font-size: 14px;
        padding-left: 10px;
        padding-right: 14px;
        background: transparent;
        color: #374151;
        font-weight: 500;
        
        &::placeholder {
          color: #9CA3AF;
          font-size: 14px;
          font-weight: 400;
        }
      }
      
      :deep(.el-input__prefix) {
        padding-left: 12px;
      }
      
      .input-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #9CA3AF;
        font-size: 18px;
        margin-right: 8px;
      }
      
      :deep(.el-input__suffix) {
        right: 12px;
        
        .el-icon {
          color: #9CA3AF;
          font-size: 16px;
        }
      }
    }
  }
  
  .form-footer {
    text-align: center;
    margin-top: 8px;
    margin-bottom: 0;
    font-size: 14px;
    
    .switch-text {
      color: #4B5563;
    }
    
    .switch-link {
      color: #722ED1;
      cursor: pointer;
      font-weight: 600;
      margin-left: 5px;
      transition: all 0.2s ease;
      
      &:hover {
        color: #5B21B6;
        text-decoration: underline;
      }
    }
  }
  
  .submit-button {
    width: 100%;
    height: 44px;
    border-radius: 8px;
    background: #722ED1;
    border: none;
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 8px;
    
    &:hover {
      background: #5B21B6;
    }
    
    &:active {
      background: #4C1D95;
    }
    
    &.is-loading {
      opacity: 0.8;
    }
  }
}

:deep(.el-form-item) {
  margin-bottom: 0;
  border: none;
  
  .el-form-item__content {
    border: none;
  }
}

:deep(.el-form-item__error) {
  font-size: 12px;
  color: #EF4444;
  margin-top: 5px;
}

@media (max-width: 1440px) {
  .auth-container {
    width: 100vw;
    height: 100vh;
  }
}

@media (min-width: 1448px) {
  .auth-container {
    width: 1440px;
    height: 900px;
  }
}

@media (max-width: 1280px) {
  .auth-card {
    margin-right: 80px;
    width: 400px;
    height: 484px;
  }
  
  .auth-content {
    padding: 30px 25px;
  }
}

@media (max-width: 1024px) {
  .auth-container {
    justify-content: center;
  }
  
  .auth-card {
    margin-right: 0;
    margin-left: 0;
    width: 400px;
    height: 484px;
  }
  
  .auth-content {
    padding: 30px 25px;
  }
}

@media (max-width: 768px) {
  .auth-container {
    justify-content: center;
  }
  
  .background-image {
    .bg-img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .auth-card {
    width: 90%;
    height: auto;
    margin: 0 auto;
    max-width: 400px;
  }
  
  .auth-content {
    padding: 30px 25px;
  }
  
  .auth-header {
    .auth-title {
      font-size: 30px;
    }
    
    .auth-subtitle {
      font-size: 15px;
    }
  }
}
</style>