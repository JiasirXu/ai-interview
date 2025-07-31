<template>
  <div class="main-layout">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <nav class="sidebar-nav">
        <!-- 个人中心 -->
        <div class="nav-group">
          <div 
            class="nav-item main-nav" 
            :class="{ active: isActiveGroup('/profile') }"
            @click="toggleGroup('/profile')"
          >
            <div class="nav-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <span class="nav-label">个人中心</span>
            <div class="nav-arrow" :class="{ expanded: expandedGroup === '/profile' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
          
          <!-- 个人中心子导航 -->
          <div class="sub-nav" v-show="expandedGroup === '/profile'">
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/profile/personal' }"
              @click="navigateTo('/profile/personal')"
            >
              <span class="nav-label">个人信息</span>
            </div>
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/profile/resume' }"
              @click="navigateTo('/profile/resume')"
            >
              <span class="nav-label">简历管理</span>
            </div>
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/profile/preference' }"
              @click="navigateTo('/profile/preference')"
            >
              <span class="nav-label">岗位偏好</span>
            </div>
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/profile/settings' }"
              @click="navigateTo('/profile/settings')"
            >
              <span class="nav-label">账号设置</span>
            </div>
          </div>
        </div>

        <!-- 模拟面试 -->
        <div class="nav-group">
          <div 
            class="nav-item main-nav" 
            :class="{ active: isActiveGroup('/interview') }"
            @click="toggleGroup('/interview')"
          >
            <div class="nav-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <span class="nav-label">模拟面试</span>
            <div class="nav-arrow" :class="{ expanded: expandedGroup === '/interview' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
          
          <!-- 模拟面试子导航 -->
          <div class="sub-nav" v-show="expandedGroup === '/interview'">
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/interview/main' }"
              @click="navigateTo('/interview/main')"
            >
              <span class="nav-label">面试界面</span>
            </div>
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/interview/preferences' }"
              @click="navigateTo('/interview/preferences')"
            >
              <span class="nav-label">偏好设置</span>
            </div>
          </div>
        </div>

        <!-- 测评报告 -->
        <div class="nav-group">
          <div 
            class="nav-item main-nav" 
            :class="{ active: isActiveGroup('/report') }"
            @click="toggleGroup('/report')"
          >
            <div class="nav-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                <path d="M14 2v6h6"/>
                <path d="M16 13H8"/>
                <path d="M16 17H8"/>
                <path d="M10 9H8"/>
              </svg>
            </div>
            <span class="nav-label">测评报告</span>
            <div class="nav-arrow" :class="{ expanded: expandedGroup === '/report' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
          
          <!-- 测评报告子导航 -->
          <div class="sub-nav" v-show="expandedGroup === '/report'">
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/report' }"
              @click="navigateTo('/report')"
            >
              <span class="nav-label">结果分析</span>
            </div>
          </div>
        </div>

        <!-- 优化建议 -->
        <div class="nav-group">
          <div 
            class="nav-item main-nav" 
            :class="{ active: isActiveGroup('/optimization') }"
            @click="toggleGroup('/optimization')"
          >
            <div class="nav-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"/>
              </svg>
            </div>
            <span class="nav-label">优化建议</span>
            <div class="nav-arrow" :class="{ expanded: expandedGroup === '/optimization' }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
          
          <!-- 优化建议子导航 -->
          <div class="sub-nav" v-show="expandedGroup === '/optimization'">
            <div 
              class="nav-item sub-nav-item" 
              :class="{ active: activeRoute === '/optimization' }"
              @click="navigateTo('/optimization')"
            >
              <span class="nav-label">题目解析</span>
            </div>
          </div>
        </div>
      </nav>

      <!-- 用户信息和退出按钮 -->
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <img v-if="currentUser?.avatar" :src="currentUser.avatar" alt="头像" class="avatar-img" />
            <div v-else class="avatar-placeholder">
              {{ userInitials }}
            </div>
          </div>
          <div class="user-details">
            <div class="user-name">{{ displayUserName }}</div>
            <div class="user-role">普通用户</div>
          </div>
        </div>
        <button class="logout-btn" @click="logout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          退出登录
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 当前激活路由
const activeRoute = computed(() => route.path)

// 展开的导航组
const expandedGroup = ref('')

// 页面标题（已删除显示）
const pageTitle = computed(() => {
  return ''
})

// 用户信息
const currentUser = computed(() => authStore.user)
const displayUserName = computed(() => {
  return authStore.user?.name || authStore.user?.username || '未登录'
})
const userInitials = computed(() => {
  const name = authStore.user?.name || authStore.user?.username || '用户'
  return name.charAt(0).toUpperCase()
})

// 检查是否是激活的组
const isActiveGroup = (groupPath) => {
  return activeRoute.value.startsWith(groupPath)
}

// 切换导航组
const toggleGroup = (groupPath) => {
  // 如果当前已经是展开状态，则收起
  if (expandedGroup.value === groupPath) {
    expandedGroup.value = ''
  } else {
    expandedGroup.value = groupPath
    // 如果是个人中心，默认跳转到个人信息
    if (groupPath === '/profile') {
      navigateTo('/profile/personal')
    }
    // 如果是模拟面试，默认跳转到面试界面
    else if (groupPath === '/interview') {
      navigateTo('/interview/main')
    }
    // 如果是测评报告，默认跳转到结果分析
    else if (groupPath === '/report') {
      navigateTo('/report')
    }
    // 如果是优化建议，默认跳转到题目解析
    else if (groupPath === '/optimization') {
      navigateTo('/optimization')
    }
  }
}

// 导航
const navigateTo = (path) => {
  router.push(path)
}

// 退出登录
const logout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    ElMessage.error('退出登录失败')
  }
}

// 监听路由变化，自动展开对应的导航组
watch(activeRoute, (newRoute) => {
  if (newRoute.startsWith('/profile')) {
    expandedGroup.value = '/profile'
  } else if (newRoute.startsWith('/interview')) {
    expandedGroup.value = '/interview'
  } else if (newRoute.startsWith('/optimization')) {
    expandedGroup.value = '/optimization'
  } else if (newRoute.startsWith('/report')) {
    expandedGroup.value = '/report'
  } else {
    expandedGroup.value = ''
  }
}, { immediate: true })

// 初始化
onMounted(() => {
  // 如果当前路径是根路径，默认跳转到个人信息
  if (route.path === '/') {
    router.push('/profile/personal')
  }
})
</script>

<style lang="scss" scoped>
.main-layout {
  display: flex;
  height: calc(100vh - 60px); // 减去顶部导航栏的高度
  overflow: hidden;
  background: $gray-50;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid $border-gray;
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar-nav {
  flex: 1;
  padding: 24px 0;
  overflow-y: auto;
}

.nav-group {
  margin-bottom: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  &:hover {
    background: $gray-100;
  }
  
  &.active {
    background: $interview-primary-lighter;
    color: $interview-primary;
  }
}

.main-nav {
  font-weight: 400;
  font-size: 16px;
  
  &.active {
    background: $interview-primary-lighter;
    color: $interview-primary;
    
    &::before {
      content: none;
    }
  }
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  color: $gray-600;
  
  .main-nav.active & {
    color: $interview-primary;
  }
}

.nav-label {
  flex: 1;
  color: $gray-800;
  
  .main-nav.active & {
    color: $interview-primary;
  }
  
  .sub-nav-item.active & {
    color: $interview-primary !important;
  }
}

.nav-arrow {
  width: 16px;
  height: 16px;
  color: $gray-400;
  transform: rotate(0deg);
  transition: transform 0.2s ease;
  
  &.expanded {
    transform: rotate(90deg);
  }
}

.sub-nav {
  padding-left: 32px; // Indent sub-menu to align with main nav text
  margin: 8px 0;
  background: none;
  border: none;
}

.sub-nav-item {
  font-size: 14px;
  color: $gray-600;
  padding: 10px 24px;
  margin-bottom: 4px;
  border-radius: 6px;
  font-weight: 400;
  
  &:hover {
    background: $gray-100;
  }
  
  &.active {
    background: $interview-primary-lighter;
    color: $interview-primary !important;
    font-weight: 400;
  }
}

.sidebar-footer {
  padding: 24px;
  border-top: 1px solid $border-gray;
  background: white;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 12px;
  background: $interview-primary-lighter;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-placeholder {
  color: $interview-primary;
  font-weight: 600;
  font-size: 16px;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: $gray-800;
  margin-bottom: 2px;
}

.user-role {
  font-size: 12px;
  color: $gray-500;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: $gray-100;
  border: 1px solid $border-gray;
  border-radius: 6px;
  color: $gray-600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  width: 100%;
  justify-content: center;
  
  &:hover {
    background: $gray-200;
    color: $gray-800;
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: $gray-50;
  
  // 确保内容与左侧导航栏对齐
  padding: 0;
  margin: 0;
}

// 页面标题样式已删除

// 添加一些变量定义以确保样式正确
$gray-50: #f9fafb;
$gray-100: #f3f4f6;
$gray-200: #e5e7eb;
$gray-400: #9ca3af;
$gray-500: #6b7280;
$gray-600: #4b5563;
$gray-800: #1f2937;
$border-gray: #e5e7eb;
$interview-primary: #722ED1;
$interview-primary-lighter: #f3f0ff;
</style>