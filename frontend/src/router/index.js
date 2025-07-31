import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 主布局组件
const MainLayout = () => import('../components/MainLayout.vue')

// Profile 子页面组件 - 直接使用原始组件
const PersonalInfo = () => import('../components/profile/PersonalInfo.vue')
const ResumeManagement = () => import('../components/profile/ResumeManagement.vue')
const JobPreference = () => import('../components/profile/JobPreference.vue')
const AccountSettings = () => import('../components/profile/AccountSettings.vue')

// Interview 子页面组件 - 使用同步导入避免路由错误
import InterviewMain from '../components/interview/InterviewMain.vue'
import InterviewPreferences from '../components/interview/InterviewPreferences.vue'

// 其他页面组件
const Report = () => import('../components/Report/Report.vue')
const Optimization = () => import('../components/Optimization/Optimization.vue')

// 认证相关页面
const AuthView = () => import('../components/auth/AuthView.vue')

// 错误页面
const NotFoundView = () => import('../views/error/404View.vue')

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/profile/personal'
  },
  // 认证路由
  {
    path: '/auth',
    name: 'Auth',
    component: AuthView,
    meta: { 
      title: '用户认证', 
      requiresAuth: false,
      hideForAuth: true // 已登录用户隐藏
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: AuthView,
    meta: { 
      title: '登录', 
      requiresAuth: false,
      hideForAuth: true // 已登录用户隐藏
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: AuthView,
    meta: { 
      title: '注册', 
      requiresAuth: false,
      hideForAuth: true // 已登录用户隐藏
    }
  },
  // 主应用路由 - 使用MainLayout布局
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      // 个人中心子路由
      {
        path: 'profile',
        redirect: '/profile/personal'
      },
      {
        path: 'profile/personal',
        name: 'PersonalInfo',
        component: PersonalInfo,
        meta: { 
          title: '个人信息', 
          requiresAuth: true 
        }
      },
      {
        path: 'profile/resume',
        name: 'ResumeManagement',
        component: ResumeManagement,
        meta: { 
          title: '简历管理', 
          requiresAuth: true 
        }
      },
      {
        path: 'profile/preference',
        name: 'JobPreference',
        component: JobPreference,
        meta: { 
          title: '岗位偏好', 
          requiresAuth: true 
        }
      },
      {
        path: 'profile/settings',
        name: 'AccountSettings',
        component: AccountSettings,
        meta: { 
          title: '账号设置', 
          requiresAuth: true 
        }
      },
      // 面试子路由
      {
        path: 'interview',
        redirect: '/interview/main'
      },
      {
        path: 'interview/main',
        name: 'InterviewMain',
        component: InterviewMain,
        meta: { 
          title: '面试界面', 
          requiresAuth: true 
        }
      },
      {
        path: 'interview/preferences',
        name: 'InterviewPreferences',
        component: InterviewPreferences,
        meta: { 
          title: '面试偏好', 
          requiresAuth: true 
        }
      },
      // 其他页面
      {
        path: 'report',
        name: 'Report',
        component: Report,
        meta: { 
          title: '测评报告', 
          requiresAuth: true 
        }
      },
      {
        path: 'optimization',
        name: 'Optimization',
        component: Optimization,
        meta: { 
          title: '优化建议', 
          requiresAuth: true 
        }
      }
    ]
  },
  // 错误页面
  {
    path: '/404',
    name: 'NotFound',
    component: NotFoundView,
    meta: { title: '页面不存在' }
  },
  // 匹配所有路径 - 必须放在最后
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 白名单路由（不需要认证）
const whiteList = ['/auth', '/login', '/register', '/404']

// 全局路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - InterviewAI`
  }
  

  
  // 获取认证状态
  const authStore = useAuthStore()
  
  // 初始化认证状态（仅在首次访问时）
  if (!authStore.user && localStorage.getItem('access_token')) {
    try {
      await authStore.initialize()
    } catch (error) {
      console.error('初始化认证状态失败:', error)
    }
  }
  
  const isLoggedIn = authStore.isLoggedIn
  const requiresAuth = to.meta.requiresAuth
  const hideForAuth = to.meta.hideForAuth
  
  // 如果页面需要认证但用户未登录
  if (requiresAuth && !isLoggedIn) {
    // 保存原始访问路径
    const redirectPath = to.fullPath
    if (redirectPath !== '/auth' && redirectPath !== '/login' && redirectPath !== '/register') {
      localStorage.setItem('redirect_after_login', redirectPath)
    }
    
    // 跳转到登录页
    next('/login')
    return
  }
  
  // 如果用户已登录且访问登录/注册页面，重定向到首页
  if (isLoggedIn && hideForAuth) {
    next('/profile/personal')
    return
  }
  
  // 检查用户权限（如果有角色控制）
  if (to.meta.roles && to.meta.roles.length > 0) {
    const userRole = authStore.user?.role
    if (!to.meta.roles.includes(userRole)) {
      next('/404')
      return
    }
  }
  
  next()
})

// 路由后置守卫
router.afterEach((to, from) => {
  // 记录页面访问
  console.log(`从 ${from.path} 跳转到 ${to.path}`)
  
  // 页面访问统计（可选）
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: to.path,
      page_title: to.meta.title
    })
  }
})

export default router

/* 
路由配置说明：
1. 使用Vue Router 4的API
2. 采用懒加载方式引入页面组件，提高首屏加载速度
3. 使用MainLayout作为主布局组件，包含左侧可展开导航栏
4. 配置嵌套路由结构：
   - /profile/* - 个人中心相关页面
   - /interview/* - 面试相关页面
   - /report - 测评报告
   - /optimization - 优化建议
5. 路由守卫用于全局处理页面切换逻辑和权限控制
6. 支持浏览器历史模式，URL更美观
7. 完整的认证流程：
   - requiresAuth: true 需要登录才能访问
   - hideForAuth: true 登录后隐藏（如登录页）
   - roles: [] 角色权限控制
8. 自动重定向：登录后跳转到原始访问页面
9. 页面结构：
   - /profile/personal - 个人信息
   - /profile/resume - 简历管理
   - /profile/preference - 岗位偏好
   - /profile/settings - 账号设置
   - /interview/main - 面试界面
   - /interview/preferences - 面试偏好
   - /report - 测评报告
   - /optimization - 优化建议
*/ 