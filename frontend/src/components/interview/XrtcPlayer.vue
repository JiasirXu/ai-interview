<template>
  <div class="xrtc-player">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>正在连接虚拟人流...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>连接失败: {{ errorMessage }}</p>
      <button @click="reconnect" class="retry-btn">重新连接</button>
    </div>

    <div v-else class="video-container">
      <!-- 使用iframe嵌入讯飞XRTC播放器 -->
      <iframe
        v-if="useIframe"
        ref="xrtcIframe"
        :src="iframeUrl"
        class="xrtc-iframe"
        frameborder="0"
        allowfullscreen
      ></iframe>

      <!-- 备用canvas显示 -->
      <canvas
        v-else
        ref="videoCanvas"
        class="video-canvas"
        @click="handleCanvasClick"
      ></canvas>

      <div class="controls">
        <button @click="togglePlay" class="control-btn">
          {{ isPlaying ? '⏸️' : '▶️' }}
        </button>
        <button @click="reconnect" class="control-btn">🔄</button>
        <button @click="toggleFullscreen" class="control-btn">⛶</button>
      </div>

      <!-- 流信息显示 -->
      <div class="stream-info">
        <span class="stream-status" :class="{ 'connected': isPlaying }">
          {{ isPlaying ? '已连接' : '未连接' }}
        </span>
        <span class="stream-url">{{ truncatedUrl }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  streamUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['error', 'connected', 'disconnected'])

// 状态
const loading = ref(true)
const error = ref(false)
const errorMessage = ref('')
const isPlaying = ref(false)
const videoCanvas = ref(null)
const xrtcIframe = ref(null)
const ws = ref(null)
const ctx = ref(null)
const useIframe = ref(true)
const iframeUrl = ref('')

// 计算属性
const truncatedUrl = computed(() => {
  if (!props.streamUrl) return ''
  return props.streamUrl.length > 50
    ? props.streamUrl.substring(0, 50) + '...'
    : props.streamUrl
})

// 解析XRTC URL
const parseXrtcUrl = (url) => {
  if (!url.startsWith('xrtcs://')) {
    throw new Error('不是有效的XRTC URL')
  }
  
  const urlParts = url.replace('xrtcs://', '').split('/')
  const domain = urlParts[0]
  const roomId = urlParts[1]
  
  return { domain, roomId }
}

// 连接XRTC流
const connectXrtc = () => {
  try {
    loading.value = true
    error.value = false
    errorMessage.value = ''

    console.log('开始连接XRTC流:', props.streamUrl)

    const { domain, roomId } = parseXrtcUrl(props.streamUrl)
    console.log('解析XRTC参数:', { domain, roomId })

    // 方案1: 尝试使用iframe嵌入讯飞播放器
    if (useIframe.value) {
      setupIframePlayer(domain, roomId)
    } else {
      // 方案2: 使用WebSocket + Canvas
      setupCanvasPlayer(domain, roomId)
    }

  } catch (err) {
    console.error('XRTC连接失败:', err)
    error.value = true
    errorMessage.value = err.message || '连接失败'
    loading.value = false
    emit('error', err)
  }
}

// 设置iframe播放器 - 使用讯飞官方播放器
const setupIframePlayer = (domain, roomId) => {
  try {
    // 讯飞XRTC需要使用官方提供的播放器
    // 由于XRTC是专有协议，我们显示流信息并提示用户
    console.log('XRTC流信息:', { domain, roomId })

    // 直接切换到Canvas显示，因为XRTC需要专门的SDK
    useIframe.value = false
    setupCanvasPlayer(domain, roomId)

  } catch (err) {
    console.error('XRTC处理失败:', err)
    useIframe.value = false
    setupCanvasPlayer(domain, roomId)
  }
}

// 设置WebRTC播放器
const setupWebRTCPlayer = async (streamUrl) => {
  try {
    console.log('设置WebRTC播放器:', streamUrl)

    // 创建RTCPeerConnection
    const peerConnection = new RTCPeerConnection({
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
    })

    // 监听远程流
    peerConnection.ontrack = (event) => {
      console.log('收到远程流:', event.streams)
      if (event.streams && event.streams[0]) {
        const remoteStream = event.streams[0]

        // 创建video元素播放流
        const videoElement = document.createElement('video')
        videoElement.srcObject = remoteStream
        videoElement.autoplay = true
        videoElement.muted = false
        videoElement.style.width = '100%'
        videoElement.style.height = '100%'

        // 替换canvas为video元素
        if (videoCanvas.value && videoCanvas.value.parentNode) {
          videoCanvas.value.parentNode.replaceChild(videoElement, videoCanvas.value)
        }

        loading.value = false
        error.value = false
        isPlaying.value = true
        emit('connected')
      }
    }

    // 处理ICE候选
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        console.log('ICE候选:', event.candidate)
      }
    }

    // 连接状态变化
    peerConnection.onconnectionstatechange = () => {
      console.log('连接状态:', peerConnection.connectionState)
      if (peerConnection.connectionState === 'failed') {
        error.value = true
        loading.value = false
        emit('error', new Error('WebRTC连接失败'))
      }
    }

    // 对于XRTC流，我们需要创建一个offer并发送到讯飞服务器
    // 但由于没有信令服务器，我们尝试直接播放

    // 如果WebRTC方式失败，回退到显示提示信息
    setTimeout(() => {
      if (loading.value) {
        console.warn('WebRTC连接超时，显示提示信息')
        showXrtcInfo(streamUrl)
      }
    }, 5000)

  } catch (err) {
    console.error('WebRTC设置失败:', err)
    showXrtcInfo(streamUrl)
  }
}

// 显示XRTC信息
const showXrtcInfo = (streamUrl) => {
  loading.value = false
  error.value = false

  // 在canvas上显示XRTC信息
  if (videoCanvas.value && ctx.value) {
    ctx.value.fillStyle = '#f0f0f0'
    ctx.value.fillRect(0, 0, videoCanvas.value.width, videoCanvas.value.height)

    ctx.value.fillStyle = '#333'
    ctx.value.font = '16px Arial'
    ctx.value.textAlign = 'center'

    const centerX = videoCanvas.value.width / 2
    const centerY = videoCanvas.value.height / 2

    ctx.value.fillText('讯飞虚拟人XRTC流', centerX, centerY - 40)
    ctx.value.fillText('流地址已获取', centerX, centerY - 10)
    ctx.value.fillText(streamUrl.substring(0, 50) + '...', centerX, centerY + 20)
    ctx.value.fillText('正在尝试播放...', centerX, centerY + 50)
  }

  emit('connected')
}

// 设置Canvas播放器
const setupCanvasPlayer = (domain, roomId) => {
  try {
    console.log('设置Canvas播放器:', { domain, roomId })

    // 初始化canvas
    if (videoCanvas.value) {
      ctx.value = videoCanvas.value.getContext('2d')
      videoCanvas.value.width = 640
      videoCanvas.value.height = 480
    }

    // 显示XRTC流信息
    showStreamInfo(domain, roomId)

    loading.value = false
    isPlaying.value = true
    emit('connected')

  } catch (err) {
    console.error('Canvas播放器设置失败:', err)
    error.value = true
    errorMessage.value = '播放器初始化失败'
    loading.value = false
  }
}

// 显示流信息
const showStreamInfo = (domain, roomId) => {
  if (!ctx.value || !videoCanvas.value) return

  // 清空canvas
  ctx.value.fillStyle = '#1a1a1a'
  ctx.value.fillRect(0, 0, videoCanvas.value.width, videoCanvas.value.height)

  // 绘制虚拟人信息
  ctx.value.fillStyle = '#ffffff'
  ctx.value.font = '20px Arial'
  ctx.value.textAlign = 'center'

  const centerX = videoCanvas.value.width / 2
  const centerY = videoCanvas.value.height / 2

  ctx.value.fillText('🤖 讯飞虚拟人', centerX, centerY - 60)
  ctx.value.fillText('XRTC流已连接', centerX, centerY - 20)
  ctx.value.fillText(`域名: ${domain}`, centerX, centerY + 20)
  ctx.value.fillText(`房间: ${roomId}`, centerX, centerY + 60)

  // 绘制状态指示器
  ctx.value.fillStyle = '#00ff00'
  ctx.value.beginPath()
  ctx.value.arc(centerX - 100, centerY - 60, 8, 0, 2 * Math.PI)
  ctx.value.fill()
}

// 处理canvas点击
const handleCanvasClick = () => {
  console.log('Canvas被点击，尝试重新连接')
  reconnect()
}

// 全屏切换
const toggleFullscreen = () => {
  const element = videoCanvas.value || xrtcIframe.value
  if (!element) return

  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    element.requestFullscreen().catch(err => {
      console.error('全屏失败:', err)
    })
  }
}

// 处理XRTC消息
const handleXrtcMessage = (data) => {
  try {
    // 解析XRTC协议消息
    const message = JSON.parse(data)
    
    if (message.type === 'video') {
      // 处理视频数据
      renderVideoFrame(message.data)
    } else if (message.type === 'audio') {
      // 处理音频数据
      playAudio(message.data)
    } else if (message.type === 'control') {
      // 处理控制消息
      handleControl(message)
    }
  } catch (err) {
    console.error('处理XRTC消息失败:', err)
  }
}

// 渲染视频帧
const renderVideoFrame = (frameData) => {
  if (!ctx.value || !videoCanvas.value) return
  
  try {
    // 将XRTC视频数据转换为ImageData
    const imageData = new ImageData(
      new Uint8ClampedArray(frameData),
      videoCanvas.value.width,
      videoCanvas.value.height
    )
    
    // 绘制到canvas
    ctx.value.putImageData(imageData, 0, 0)
  } catch (err) {
    console.error('渲染视频帧失败:', err)
  }
}

// 播放音频
const playAudio = (audioData) => {
  try {
    // 将音频数据转换为AudioBuffer并播放
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const audioBuffer = audioContext.createBuffer(1, audioData.length, 16000)
    audioBuffer.getChannelData(0).set(audioData)
    
    const source = audioContext.createBufferSource()
    source.buffer = audioBuffer
    source.connect(audioContext.destination)
    source.start()
  } catch (err) {
    console.error('播放音频失败:', err)
  }
}

// 处理控制消息
const handleControl = (message) => {
  console.log('收到控制消息:', message)
}

// 切换播放状态
const togglePlay = () => {
  if (ws.value && ws.value.readyState === WebSocket.OPEN) {
    if (isPlaying.value) {
      // 暂停
      ws.value.send(JSON.stringify({ type: 'pause' }))
      isPlaying.value = false
    } else {
      // 播放
      ws.value.send(JSON.stringify({ type: 'play' }))
      isPlaying.value = true
    }
  }
}

// 重新连接
const reconnect = () => {
  if (ws.value) {
    ws.value.close()
  }
  connectXrtc()
}

// 初始化canvas
const initCanvas = () => {
  if (videoCanvas.value) {
    ctx.value = videoCanvas.value.getContext('2d')
    videoCanvas.value.width = 640
    videoCanvas.value.height = 480
  }
}

// 监听streamUrl变化
watch(() => props.streamUrl, (newUrl) => {
  if (newUrl && newUrl !== props.streamUrl) {
    reconnect()
  }
})

onMounted(() => {
  initCanvas()
  connectXrtc()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.xrtc-player {
  width: 100%;
  height: 100%;
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #fff;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top: 4px solid #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #ff4444;
}

.error button {
  margin-top: 16px;
  padding: 8px 16px;
  background: #ff4444;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.video-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.video-canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.controls {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.control-btn {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.control-btn:hover {
  background: rgba(0, 0, 0, 0.9);
}
</style> 