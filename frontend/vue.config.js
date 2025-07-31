const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  // 基础配置
  transpileDependencies: true,
  lintOnSave: false,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    open: true,
    host: 'localhost',
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      },
      '/uploads': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/uploads': '/uploads'
        }
      }
    }
  },
  
  // 构建配置
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,
  
  // 路径别名
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  
  // CSS 预处理器配置
  css: {
    loaderOptions: {
      scss: {
        additionalData: `@use "@/styles/variables.scss" as *;`
      }
    }
  }
})

/*
Vue配置文件说明：
1. 配置开发服务器端口和API代理
2. 设置构建输出目录和静态资源目录
3. 配置路径别名 @ 指向 src 目录
4. 生产环境不生成 source map
5. 全局导入SCSS变量文件，所有组件可直接使用变量
*/ 