import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// Element Plus UI库
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 全局样式
import './styles/main.css'

// 创建应用实例
const app = createApp(App)

// 创建Pinia实例
const pinia = createPinia()

// 注册插件
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('全局错误:', err)
  console.error('错误信息:', info)
}

// 挂载应用
app.mount('#app')

// 初始化认证状态
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.initialize().catch(err => {
  console.error('初始化认证状态失败:', err)
})

// 项目入口文件说明：
// 1. 创建Vue应用实例
// 2. 配置路由、状态管理、UI库
// 3. 初始化认证状态
// 4. 挂载到DOM元素上 