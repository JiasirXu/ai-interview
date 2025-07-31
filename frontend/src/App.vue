<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <div class="app-header">
      <h1 class="app-title">InterviewAI</h1>
    </div>
    
    <!-- 主内容区域 -->
    <div class="app-content">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 根组件样式 */
#app {
  min-height: 100vh;
  background: #f5f5f7;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏 */
.app-header {
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.app-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #722ED1;
  letter-spacing: 0.5px;
}

/* 主内容区域 */
.app-content {
  flex: 1;
  margin-top: 60px; /* 为固定的顶部导航栏留出空间 */
}
</style> 