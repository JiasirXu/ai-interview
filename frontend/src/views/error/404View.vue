<template>
  <div class="not-found-view">
    <div class="error-content">
      <div class="error-code">404</div>
      <div class="error-message">页面未找到</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style lang="scss" scoped>
.not-found-view {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  text-align: center;
  color: white;

  .error-code {
    font-size: 120px;
    font-weight: bold;
    margin-bottom: 20px;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  }

  .error-message {
    font-size: 32px;
    margin-bottom: 16px;
  }

  .error-description {
    font-size: 16px;
    margin-bottom: 32px;
    opacity: 0.8;
  }

  .error-actions {
    display: flex;
    gap: 16px;
    justify-content: center;
  }
}
</style> 