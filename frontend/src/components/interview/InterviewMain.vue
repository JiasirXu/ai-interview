<template>
  <div class="interview-interface">
    <!-- 左侧主要区域 -->
    <div class="main-content">
      <!-- 面包屑导航 -->
      <div class="breadcrumb">
        <span class="breadcrumb-item">模拟面试</span>
        <span class="breadcrumb-separator">></span>
        <span class="breadcrumb-item active">面试界面</span>
      </div>

      <!-- 主视频窗口 -->
      <div class="main-video">
        <div class="video-frame">
          <!-- 面试者视频区域 -->
          <div class="interviewee-video">
            <video
              id="userVideo"
              ref="userVideo"
              autoplay
              muted
              playsinline
              class="user-video"
            ></video>
            <div v-if="!isInterviewStarted || isPreparingInterview" class="video-placeholder">
              <div v-if="isPreparingInterview" class="loading-content">
                <div class="loading-spinner"></div>
                <div class="placeholder-text">正在准备面试...</div>
                <div class="placeholder-subtitle">正在加载面试官和面试问题</div>
              </div>
              <div v-else class="placeholder-content">
                <div class="placeholder-text">面试者视频</div>
                <div class="placeholder-subtitle">点击开始面试</div>
              </div>
            </div>
              </div>
          
          <!-- 虚拟面试官窗口 -->
          <div class="interviewer-window">
            <div v-if="avatarVideoUrl" class="avatar-video-container">
              <video
                ref="avatarVideo"
                :src="avatarVideoUrl"
                autoplay
                muted
                loop
                class="avatar-video"
                @loadstart="onAvatarVideoLoadStart"
                @canplay="onAvatarVideoCanPlay"
                @error="onAvatarVideoError"
              ></video>
              <div v-if="avatarLoading" class="avatar-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">加载中...</div>
                    </div>
                  </div>
            <div v-else class="interviewer-placeholder">
              <div v-if="isPreparingInterview" class="loading-content">
                <div class="loading-spinner"></div>
                <div class="placeholder-text">正在加载面试官...</div>
                <div class="placeholder-subtitle">准备第一个问题中</div>
                </div>
              <div v-else-if="currentQuestion" class="question-display">
                <div class="avatar-icon">🤖</div>
                <div class="question-content">
                  <div class="question-title">面试官提问</div>
                  <div class="question-text">{{ currentQuestion.content }}</div>
                </div>
              </div>
              <div v-else class="placeholder-content">
                <div class="placeholder-text">虚拟面试官</div>
                <div class="placeholder-subtitle">等待连接...</div>
            </div>
          </div>

            <!-- 虚拟面试官状态指示器 -->
            <div class="avatar-status" :class="avatarStatus">
              <div class="status-dot"></div>
              <span class="status-text">{{ getAvatarStatusText() }}</span>
            </div>
        </div>
        </div>
        
        <!-- 视频控制栏 -->
        <div class="video-controls">
          <div class="control-left">
            <div v-if="isTranscribing" class="transcription-indicator">
              <span class="indicator-dot"></span>
              <span class="indicator-text">正在转写</span>
            </div>
          </div>
          
          <div class="control-center">
            <div class="time-display">
              <span class="time">⏱ {{ formatTime(currentTime) }}</span>
            </div>
            <div v-if="audioLevel > 0" class="audio-level-display">
              <div class="level-bar" :style="{ width: audioLevel + '%' }"></div>
              <span class="level-text">{{ audioLevel }}%</span>
            </div>
          </div>
          
          <div class="control-right">
            <button class="control-btn favorite" @click="toggleFavorite">
              ⭐ 收藏当前问题
            </button>
          </div>
        </div>
      </div>

      <!-- 开始面试按钮区域 - 贴住视频下方 -->
      <div class="interview-control-section">
        <div class="control-container">
          <button class="main-interview-btn" :class="{ preparing: isPreparingInterview }" @click="toggleInterview" :disabled="isPreparingInterview">
          <div v-if="isPreparingInterview" class="btn-loading">
            <div class="loading-spinner-small"></div>
            <span class="btn-text">准备中...</span>
          </div>
          <div v-else class="btn-content">
            <span class="btn-icon">{{ isInterviewStarted ? '⏹' : '▶' }}</span>
            <span class="btn-text">{{ isInterviewStarted ? '结束面试' : '开始面试' }}</span>
          </div>
          </button>

            <div class="timer-display">
            {{ formatTime(currentTime) }}
            </div>
              </div>
      </div>

      <!-- AI 实时反馈区域 -->
      <div class="ai-feedback">
        <div class="feedback-header">
          <span class="feedback-title">AI 实时反馈</span>
          <div class="header-controls">
            <div class="toggle-switch" :class="{ active: aiFeedbackEnabled }" @click="toggleAIFeedback">
              <div class="toggle-slider"></div>
            </div>
          </div>
        </div>

        <!-- 评估维度网格 -->
        <div v-if="aiFeedbackEnabled" class="feedback-grid">
          <div class="feedback-item">
            <div class="feedback-icon">
              <SvgIcon name="container6" />
            </div>
            <div class="feedback-content">
              <div class="feedback-title">语音表达</div>
              <div class="feedback-desc">{{ realTimeFeedback.audio || '语音表达暂无数据，建议保持适中语速，重音词汇当强调' }}</div>
            </div>
          </div>

          <div class="feedback-item">
            <div class="feedback-icon">
              <SvgIcon name="container7" />
            </div>
            <div class="feedback-content">
              <div class="feedback-title">行为表现</div>
              <div class="feedback-desc">{{ realTimeFeedback.behavior || '行为表现暂无数据，可注意保持自然眼神交流，手势与技术要点描述同步增强说服力' }}</div>
            </div>
          </div>

          <div class="feedback-item">
            <div class="feedback-icon">
              <SvgIcon name="container8" />
            </div>
            <div class="feedback-content">
              <div class="feedback-title">技术内容</div>
              <div class="feedback-desc">{{ realTimeFeedback.technical || '技术内容尚未展开，建议选择具代表性项目，阐明编程技术如何破解具体工程难题（如算法优化/测试效率提升）' }}</div>
            </div>
          </div>

          <div class="feedback-item">
            <div class="feedback-icon">
              <SvgIcon name="container9" />
            </div>
            <div class="feedback-content">
              <div class="feedback-title">压力应对</div>
              <div class="feedback-desc">{{ realTimeFeedback.stress || '压力应对状态未知，可预先用STAR法则结构化回答，突出技术决策和跨部门协作价值' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 实时转写结果区域 -->
      <div v-if="isInterviewStarted && transcriptionText" class="transcription-result">
        <div class="transcription-header">
          <span class="transcription-title">实时转写结果</span>
        </div>
        <div class="transcription-content">
          <p class="transcription-text">{{ transcriptionText }}</p>
        </div>
        <div v-if="aiResponse" class="ai-response-panel">
          <div class="response-header">
            AI智能分析
            <!-- 面试进度 -->
            <div v-if="isInterviewStarted && !interviewFinished" class="interview-progress">
              <span class="progress-text">第 {{ currentQuestionNumber }} / {{ totalQuestions }} 题</span>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (currentQuestionNumber / totalQuestions * 100) + '%' }"></div>
              </div>
            </div>
          </div>
          <div class="response-content">{{ aiResponse }}</div>
        </div>

        <!-- 用户答题区域 -->
        <div v-if="isInterviewStarted && !interviewFinished" class="answer-section">
          <div class="answer-header">
            <span class="answer-title">您的回答</span>
            <div class="answer-actions">
              <button
                class="action-btn secondary"
                @click="skipCurrentQuestion"
                :disabled="isAnswering || isWaitingNextQuestion"
              >
                跳过此题
              </button>
              <button
                class="action-btn primary"
                @click="submitCurrentAnswer"
                :disabled="!userAnswer.trim() || isAnswering || isWaitingNextQuestion"
              >
                <span v-if="isAnswering">提交中...</span>
                <span v-else-if="isWaitingNextQuestion">等待下一题...</span>
                <span v-else>提交答案</span>
              </button>
            </div>
          </div>
          <div class="answer-input">
            <textarea
              v-model="userAnswer"
              placeholder="请在这里输入您的回答..."
              :disabled="isAnswering || isWaitingNextQuestion"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- 面试完成报告 -->
        <div v-if="interviewFinished && interviewReport" class="interview-report">
          <div class="report-header">
            <h3>🎉 面试完成报告</h3>
          </div>
          <div class="report-stats">
            <div class="stat-item">
              <span class="stat-label">完成率</span>
              <span class="stat-value">{{ interviewReport.completion_rate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">用时</span>
              <span class="stat-value">{{ interviewReport.duration_minutes }}分钟</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">评分</span>
              <span class="stat-value">{{ interviewReport.score }}分</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">评价</span>
              <span class="stat-value">{{ interviewReport.performance }}</span>
            </div>
          </div>
          <div class="report-summary">
            <p>{{ interviewReport.summary }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- XRTC虚拟人浮窗 -->
    <div
      v-if="xrtcStreamUrl"
      class="xrtc-floating-window"
      :class="{ 'minimized': isXrtcMinimized, 'dragging': isDragging }"
      :style="{
        left: windowPosition.x + 'px',
        top: windowPosition.y + 'px',
        position: 'fixed'
      }"
    >
      <div class="xrtc-header" @mousedown="startDrag">
        <div class="xrtc-title">
          <div class="xrtc-status-dot" :class="xrtcStatus"></div>
          <span>虚拟面试官</span>
        
        </div>
        <div class="xrtc-controls">
          <button @click="toggleXrtcMinimize" class="xrtc-btn">
            {{ isXrtcMinimized ? '📖' : '📕' }}
          </button>
          <button @click="closeXrtcWindow" class="xrtc-btn">✕</button>
        </div>
      </div>
                  <div v-if="!isXrtcMinimized" class="xrtc-content">
              <!-- XRTC视频播放器 - 占2/3高度 -->
              <div class="xrtc-video-container">
                <!-- 使用XRTC播放器组件 -->
                <XrtcPlayer
                  v-if="xrtcStreamUrl && xrtcStreamUrl.startsWith('xrtcs://')"
                  :stream-url="xrtcStreamUrl"
                  @error="onXrtcPlayerError"
                  @connected="onXrtcPlayerConnected"
                  @disconnected="onXrtcPlayerDisconnected"
                />
                
                <!-- 备用显示：当XRTC播放器不可用时 -->
                <div v-else class="xrtc-fallback">
                  <div class="virtual-avatar-fullsize">
                    <div class="avatar-animation-large">
                      <div class="avatar-face-large">🤖</div>
                      <div class="avatar-body-large">👔</div>
                    </div>
                    <div class="speaking-indicator-large">
                      <div class="wave-large"></div>
                      <div class="wave-large"></div>
                      <div class="wave-large"></div>
                    </div>
                    <div class="fallback-text-large">虚拟面试官</div>
                  </div>
                </div>
        </div>

        <!-- 当前问题显示 - 占1/3高度 -->
        <div class="current-question-bottom">
          <div class="question-label-bottom">当前问题:</div>
          <div class="question-text-bottom">{{ currentQuestion?.content || '等待问题...' }}</div>
        </div>
      </div>
    </div>

    <!-- 右侧控制面板 -->
    <div class="control-panel">
      <div class="panel-header">
        <h3>面试模式</h3>
      </div>
      
      <!-- 面试模式选择 -->
      <div class="interview-modes">
        <div class="mode-grid">
          <div class="mode-item" :class="{ active: currentMode === 'technical' }" @click="setMode('technical')">
            <div class="mode-icon" :style="{ color: currentMode === 'technical' ? '#722ED1' : '#6b7280' }">
              <SvgIcon2 name="interview-mode-1" />
            </div>
            <div class="mode-name">技术面</div>
          </div>
          <div class="mode-item" :class="{ active: currentMode === 'pressure' }" @click="setMode('pressure')">
            <div class="mode-icon" :style="{ color: currentMode === 'pressure' ? '#722ED1' : '#6b7280' }">
              <SvgIcon2 name="interview-mode-2" />
            </div>
            <div class="mode-name">压力面</div>
          </div>
          <div class="mode-item" :class="{ active: currentMode === 'case' }" @click="setMode('case')">
            <div class="mode-icon" :style="{ color: currentMode === 'case' ? '#722ED1' : '#6b7280' }">
              <SvgIcon2 name="interview-mode-3" />
            </div>
            <div class="mode-name">案例面</div>
          </div>
          <div class="mode-item" :class="{ active: currentMode === 'comprehensive' }" @click="setMode('comprehensive')">
            <div class="mode-icon" :style="{ color: currentMode === 'comprehensive' ? '#722ED1' : '#6b7280' }">
              <SvgIcon2 name="interview-mode-4" />
            </div>
            <div class="mode-name">综合面</div>
          </div>
        </div>
      </div>

      <!-- 设置选项 -->
      <div class="settings-section">
        <div class="setting-group">
          <div class="setting-label">设置选项</div>
        </div>

        <div class="setting-group">
          <div class="setting-label sub-label">难度</div>
          <div class="difficulty-options">
            <button class="difficulty-btn" :class="{ active: difficulty === 'primary' }" @click="setDifficulty('primary')">初级</button>
            <button class="difficulty-btn" :class="{ active: difficulty === 'middle' }" @click="setDifficulty('middle')">中级</button>
            <button class="difficulty-btn" :class="{ active: difficulty === 'high' }" @click="setDifficulty('high')">高级</button>
          </div>
        </div>

        <div class="setting-group">
          <div class="setting-label sub-label">面试官表情</div>
          <div class="expression-options">
            <button class="expression-btn" :class="{ active: expression === 'friendly' }" @click="setExpression('friendly')">友好</button>
            <button class="expression-btn" :class="{ active: expression === 'serious' }" @click="setExpression('serious')">严肃</button>
            <button class="expression-btn" :class="{ active: expression === 'pressure' }" @click="setExpression('pressure')">压力</button>
          </div>
        </div>

        <div class="setting-group">
          <div class="setting-label sub-label">岗位选择</div>
          <div class="interviewer-selection">
            <select v-model="interviewerType" class="interviewer-select">
              <option v-for="position in availablePositions" :key="position.value" :value="position.value">
                {{ position.label }}
              </option>
            </select>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import SvgIcon from '../common/SvgIcon.vue'
import SvgIcon2 from '../common/SvgIcon2.vue'
import XrtcPlayer from './XrtcPlayer.vue'
import { startRealTimeTranscription, getInterviewAIResponse } from '../../api/interview.js'
import { io } from 'socket.io-client'

export default {
  name: 'InterviewMain',
  components: {
    SvgIcon,
    SvgIcon2,
    XrtcPlayer
  },
  setup() {
    // 基本状态
    const isPaused = ref(false)
    const currentTime = ref(0)
    const currentMode = ref('technical')
    const aiFeedbackEnabled = ref(true)
    const isFeedbackCollapsed = ref(false)
    const difficulty = ref('primary')
    const expression = ref('friendly')
    const interviewerType = ref('ai_algorithm_engineer')
    const availablePositions = ref([])
    const userTargetField = ref('ai')
    let timer = null

    // 面试状态
    const isInterviewStarted = ref(false)
    const isPreparingInterview = ref(false)
    const isTranscribing = ref(false)
    const transcriptionText = ref('')
    const aiResponse = ref('')
    const audioLevel = ref(0)
    const audioFeedback = ref('')
    const contentFeedback = ref('')
    const transcriptionSessionId = ref('')

    // 实时反馈数据
    const realTimeFeedback = ref({
      audio: '',
      behavior: '',
      technical: '',
      stress: ''
    })

    // 面试流程状态
    const currentQuestion = ref(null)
    const currentQuestionNumber = ref(0)
    const totalQuestions = ref(10)
    const userAnswer = ref('')
    const isAnswering = ref(false)
    const isWaitingNextQuestion = ref(false)
    const interviewFinished = ref(false)
    const interviewReport = ref(null)

    // 虚拟面试官状态
    const avatarVideoUrl = ref('')
    const avatarLoading = ref(false)
    const avatarStatus = ref('disconnected') // disconnected, connecting, connected, speaking
    const avatarVideo = ref(null)
    const interviewPreferences = ref(null)
    const noiseAudios = ref({}) // 存储噪音音频对象

    // XRTC流相关状态
    const xrtcStreamUrl = ref('')
    const xrtcStatus = ref('disconnected') // disconnected, connecting, connected, playing
    const xrtcStatusText = ref('未连接')
    const isXrtcMinimized = ref(false)

    // 拖动相关状态
    const isDragging = ref(false)
    const dragOffset = ref({ x: 0, y: 0 })
    const windowPosition = ref({ x: 20, y: 20 }) // 初始位置

    // XRTC状态（简化，主要逻辑已移至XrtcPlayer组件）
    const xrtcVideoLoading = ref(false)
    const xrtcVideoError = ref(false)

    // WebSocket连接状态
    const socket = ref(null)
    const socketConnected = ref(false)

    // 音频录制相关
    let mediaRecorder = null
    let audioStream = null
    let transcriptionManager = null
    let audioContext = null
    let analyser = null

    // 开始/结束面试
    const toggleInterview = async () => {
      if (isInterviewStarted.value) {
        await stopInterview()
      } else {
        await startInterview()
      }
    }

    // 加载面试配置
    const loadInterviewConfig = async () => {
      try {
        const response = await fetch('/api/interview/config', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            availablePositions.value = data.data.job_positions || []
            userTargetField.value = data.data.user_target_field || 'ai'

            // 设置默认选择的岗位
            if (availablePositions.value.length > 0) {
              interviewerType.value = availablePositions.value[0].value
            }

            console.log('面试配置加载成功:', {
              positions: availablePositions.value,
              targetField: userTargetField.value
            })
          }
        }
      } catch (error) {
        console.error('加载面试配置失败:', error)
        // 使用默认配置（人工智能领域）
        availablePositions.value = [
          {value: 'ai_algorithm_engineer', label: 'AI算法工程师'},
          {value: 'machine_learning_engineer', label: '机器学习工程师'},
          {value: 'ai_product_manager', label: 'AI产品经理'},
          {value: 'ai_data_scientist', label: 'AI数据科学家'}
        ]
        userTargetField.value = 'ai'
        interviewerType.value = 'ai_algorithm_engineer'
      }
    }

    // 获取领域标签
    const getFieldLabel = (field) => {
      const labels = {
        'ai': '人工智能',
        'big_data': '大数据',
        'iot': '物联网'
      }
      return labels[field] || field
    }

    // 检查用户认证状态
    const checkUserAuth = () => {
      const token = localStorage.getItem('access_token')
      const userInfo = localStorage.getItem('user_info')
      
      if (!token || !userInfo) {
        console.error('用户认证信息缺失')
        return false
      }
      
      try {
        const user = JSON.parse(userInfo)
        console.log('当前登录用户:', user)
        return true
      } catch (error) {
        console.error('解析用户信息失败:', error)
        return false
      }
    }

    // 开始面试
    const startInterview = async () => {
      try {
        console.log('开始面试...')

        // 检查用户认证状态
        if (!checkUserAuth()) {
          alert('用户认证失败，请重新登录')
          return
        }

        // 立即设置准备状态
        isPreparingInterview.value = true
        console.log('设置准备状态:', isPreparingInterview.value)

        // 1. 请求摄像头和麦克风权限
        console.log('正在请求媒体设备权限...')
        try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: 'user'
          },
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            sampleRate: 16000,
            channelCount: 1
          }
        })

        console.log('媒体设备权限获取成功')
          console.log('音频轨道数量:', stream.getAudioTracks().length)
          console.log('视频轨道数量:', stream.getVideoTracks().length)
          
          // 检查音频轨道
          const audioTracks = stream.getAudioTracks()
          if (audioTracks.length === 0) {
            console.warn('警告：没有检测到音频轨道，尝试重新获取音频权限')
            // 尝试只获取音频
            const audioOnlyStream = await navigator.mediaDevices.getUserMedia({
              audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000,
                channelCount: 1
              }
            })
            // 合并音频和视频流
            const videoTracks = stream.getVideoTracks()
            const combinedStream = new MediaStream([...audioOnlyStream.getAudioTracks(), ...videoTracks])
            audioStream = combinedStream
          } else {
        audioStream = stream
          }
        } catch (error) {
          console.error('获取媒体设备权限失败:', error)
          throw new Error(`无法获取媒体设备权限: ${error.message}`)
        }

        // 2. 加载用户面试偏好设置
        await loadInterviewPreferences()

        // 3. 调用新的面试启动API
        const interviewData = {
          interview_type: 'technical',
          interview_mode: currentMode.value,
          position: interviewerType.value,
          company: '测试公司',
          difficulty_level: difficulty.value,
          question_count: 5,
          // 移除resume_id，后端会自动整合用户所有简历信息
          preferences: interviewPreferences.value || {
            interviewer_expression: 'friendly',
            interaction_mode: 'frequent',
            voice_speed: 1.0,
            enable_emotion_feedback: true,
            feedback_types: ['nod'],
            recording_type: 'video',
            ai_highlight: true,
            improvement_marking: true,
            background_noises: []
          }
        }

        // 调用面试启动API
        const { startInterview } = await import('@/api/interview')
        const startData = await startInterview(interviewData)
        console.log('面试启动成功:', startData)

        if (startData.success) {
          // 保存会话信息
          transcriptionSessionId.value = startData.data.session_id

                    // 处理第一题
          if (startData.data.first_question_data) {
            handleFirstQuestion(startData.data.first_question_data)
            totalQuestions.value = startData.data.total_questions || 10
          }

          // 模拟准备时间，让用户看到准备状态
          setTimeout(() => {
            // 等待虚拟人和问题准备完成
            if (startData.data.first_question_video_url) {
              console.log('首问视频URL:', startData.data.first_question_video_url)
              console.log('流媒体类型:', startData.data.stream_type)

              // 检查是否是XRTC流
              if (startData.data.first_question_video_url.startsWith('xrtcs://')) {
                console.log('检测到首问XRTC流，显示浮窗:', startData.data.first_question_video_url)
                // 处理XRTC流
                handleXrtcStream({
                  video_url: startData.data.first_question_video_url,
                  stream_type: startData.data.stream_type || 'xrtc',
                  text: startData.data.first_question_data?.content || '面试开始',
                  message: '虚拟面试官已启动'
                })
              } else {
                // 普通HTTP视频流
              avatarVideoUrl.value = startData.data.first_question_video_url
              avatarStatus.value = 'speaking'
              }
            } else {
              // 没有视频时显示虚拟人占位符
              console.log('没有虚拟人视频，显示文字模式')
              avatarStatus.value = 'ready'
            }

            // 准备完成，开始正式面试
            isPreparingInterview.value = false
            isInterviewStarted.value = true
            isTranscribing.value = true

            // 启动用户视频流
            const videoElement = document.getElementById('userVideo')
            if (videoElement && audioStream) {
              videoElement.srcObject = audioStream
              videoElement.play()
              console.log('用户视频流已启动')
            }
          }, 2000) // 给2秒时间显示准备状态

          // 4. 启动噪音干扰（如果启用）
          startNoiseInterference()

          // 5. 建立WebSocket连接进行实时交互
          connectWebSocket()

          // 6. 启动流式处理（延迟启动确保WebSocket连接成功）
          setTimeout(() => {
            startStreaming()
          }, 1000)

          // 设置16kHz PCM音频录制
          setupPCMAudioRecording()

          // 启动音频可视化
          startAudioVisualization()

          console.log('面试已开始，会话ID:', transcriptionSessionId.value)
        } else {
          throw new Error(startData.message || '面试启动失败')
        }

      } catch (error) {
        console.error('启动面试失败:', error)

        let errorMessage = '启动面试失败: '
        if (error.name === 'NotAllowedError') {
          errorMessage += '请允许访问摄像头和麦克风权限'
        } else if (error.name === 'NotFoundError') {
          errorMessage += '未找到摄像头或麦克风设备'
        } else if (error.name === 'NotSupportedError') {
          errorMessage += '浏览器不支持媒体录制功能'
        } else {
          errorMessage += error.message
        }

        alert(errorMessage)

        // 重置准备状态
        isPreparingInterview.value = false

        // 清理资源
        if (audioStream) {
          audioStream.getTracks().forEach(track => track.stop())
          audioStream = null
        }
      }
    }

    // 停止面试
    const stopInterview = async () => {
      try {
        console.log('结束面试...')
        
        isInterviewStarted.value = false
        isPreparingInterview.value = false
        isTranscribing.value = false

        // 停止虚拟面试官相关资源
        avatarVideoUrl.value = ''
        avatarStatus.value = 'disconnected'
        stopNoiseInterference()

        // 断开WebSocket连接
        disconnectWebSocket()

        // 重置面试流程状态
        currentQuestion.value = null
        currentQuestionNumber.value = 0
        userAnswer.value = ''
        isAnswering.value = false
        isWaitingNextQuestion.value = false
        interviewFinished.value = false
        interviewReport.value = null

        // 停止媒体录制
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop()
        }

        // 关闭音频流
        if (audioStream) {
          audioStream.getTracks().forEach(track => track.stop())
          audioStream = null
        }

        // 关闭音频上下文
        if (audioContext) {
          audioContext.close()
          audioContext = null
        }
        
        // 停止实时转写（如果有会话ID）
        if (transcriptionSessionId.value) {
          try {
            // 通过WebSocket断开连接来停止转写，而不是调用API
            if (socket.value && socketConnected.value) {
              socket.value.emit('stop_transcription', {
                session_id: transcriptionSessionId.value
              })
              console.log('转写服务停止请求已发送')
            }
          } catch (stopError) {
            console.warn('停止转写服务失败:', stopError)
          }
          transcriptionSessionId.value = ''
        }
        
        // 清理状态
        audioLevel.value = 0
        transcriptionText.value = ''
        aiResponse.value = ''
        
        console.log('面试已结束')
        
      } catch (error) {
        console.error('停止面试失败:', error)
      }
    }

    // 设置音频录制
    const setupAudioRecording = async () => {
      try {
        console.log('开始设置音频录制...')
        
        // 获取音频流
        audioStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            sampleRate: 16000,
            channelCount: 1
          }
        })
        
        console.log('音频流获取成功:', audioStream)
        
        // 设置MediaRecorder
        const options = {
          mimeType: 'audio/webm;codecs=opus',
          audioBitsPerSecond: 16000
        }
        
        mediaRecorder = new MediaRecorder(audioStream, options)
        
        // 监听录制数据
        mediaRecorder.ondataavailable = async (event) => {
          if (event.data.size > 0 && isTranscribing.value) {
            try {
              // 将音频数据转换为base64编码
              const arrayBuffer = await event.data.arrayBuffer()
              const audioData = new Uint8Array(arrayBuffer)
              const base64Audio = btoa(String.fromCharCode(...audioData))
              
              // 发送到后端进行实时转写
              sendAudioData(base64Audio)
              
            } catch (error) {
              console.error('处理音频数据失败:', error)
            }
          }
        }
        
        // 监听录制状态变化
        mediaRecorder.onstart = () => {
          console.log('音频录制已开始')
          isTranscribing.value = true
        }
        
        mediaRecorder.onstop = () => {
          console.log('音频录制已停止')
          isTranscribing.value = false
        }
        
        mediaRecorder.onerror = (event) => {
          console.error('音频录制错误:', event.error)
          isTranscribing.value = false
        }
        
        // 开始录制，每200ms收集一次数据
        mediaRecorder.start(200)
        console.log('音频录制启动成功')
        
      } catch (error) {
        console.error('设置音频录制失败:', error)
        console.error('错误详情:', error.message)
        
        // 尝试使用备用方案
        console.log('尝试使用备用音频录制方案...')
        try {
          // 使用默认配置重新创建MediaRecorder
          const fallbackStream = await navigator.mediaDevices.getUserMedia({ audio: true })
          const fallbackRecorder = new MediaRecorder(fallbackStream)
          
          fallbackRecorder.ondataavailable = async (event) => {
            if (event.data.size > 0 && isTranscribing.value) {
              try {
                const arrayBuffer = await event.data.arrayBuffer()
                const audioData = new Uint8Array(arrayBuffer)
                const base64Audio = btoa(String.fromCharCode(...audioData))
                sendAudioData(base64Audio)
              } catch (error) {
                console.error('备用音频录制处理失败:', error)
              }
            }
          }
          
          fallbackRecorder.onstart = () => {
            console.log('备用音频录制已开始')
            isTranscribing.value = true
          }
          
          fallbackRecorder.onerror = (event) => {
            console.error('备用音频录制错误:', event.error)
            isTranscribing.value = false
          }
          
          mediaRecorder = fallbackRecorder
          mediaRecorder.start(1000) // 使用1秒间隔
          console.log('备用音频录制启动成功')
          
        } catch (fallbackError) {
          console.error('备用音频录制也失败:', fallbackError)
          console.log('音频录制功能不可用，但其他功能将继续工作')
        }
      }
    }

    // WebSocket版本的音频数据发送
    const sendAudioData = (audioData) => {
      if (socket.value && socketConnected.value) {
        try {
          console.log('发送音频数据到后端，数据大小:', typeof audioData === 'string' ? audioData.length : audioData.byteLength)
          socket.value.emit('audio_data', {
            session_id: transcriptionSessionId.value,
            audio: audioData  // 修复：使用 audio 字段名，与后端保持一致
          })
        } catch (error) {
          console.error('发送音频数据失败:', error)
        }
      } else {
        console.warn('WebSocket未连接，无法发送音频数据')
      }
    }

    // 设置16kHz PCM音频录制
    const setupPCMAudioRecording = async () => {
      try {
        if (!audioStream) {
          console.error('音频流未初始化')
          return
        }

        // 创建AudioContext，采样率16kHz
        const audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: 16000
        })
        
        // 创建音频源
        const source = audioContext.createMediaStreamSource(audioStream)
        
        // 创建ScriptProcessorNode（处理音频数据）
        const processor = audioContext.createScriptProcessor(1024, 1, 1)
        
        let isFirstFrame = true
        
        processor.onaudioprocess = (event) => {
          if (!socket.value || !socket.value.connected) {
            return
          }
          
          const inputBuffer = event.inputBuffer
          const inputData = inputBuffer.getChannelData(0) // Float32Array
          
          // 转换为16-bit PCM
          const pcmData = new Int16Array(inputData.length)
          for (let i = 0; i < inputData.length; i++) {
            // 将Float32 (-1.0 to 1.0) 转换为Int16 (-32768 to 32767)
            const sample = Math.max(-1, Math.min(1, inputData[i]))
            pcmData[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
          }
          
          // 转换为base64
          const pcmBuffer = new ArrayBuffer(pcmData.length * 2)
          const view = new DataView(pcmBuffer)
          for (let i = 0; i < pcmData.length; i++) {
            view.setInt16(i * 2, pcmData[i], true) // little-endian
          }
          
          const base64Audio = btoa(String.fromCharCode(...new Uint8Array(pcmBuffer)))
          
          // 发送音频数据
          if (isFirstFrame) {
            // 第一帧包含配置信息
            socket.value.emit('audio_data', {
              session_id: transcriptionSessionId.value,
              audio: base64Audio,
              isFirst: true,
              sampleRate: 16000,
              channels: 1,
              bitsPerSample: 16
            })
            isFirstFrame = false
          } else {
            // 后续帧只发送音频数据
            socket.value.emit('audio_data', {
              session_id: transcriptionSessionId.value,
              audio: base64Audio,
              isFirst: false
            })
          }
        }
        
        // 连接音频处理链
        source.connect(processor)
        processor.connect(audioContext.destination)
        
        console.log('16kHz PCM音频录制已启动')
        
        // 保存引用以便清理
        window.audioContext = audioContext
        window.audioProcessor = processor
        
      } catch (error) {
        console.error('设置PCM音频录制失败:', error)
      }
    }

    // 音频可视化
    const startAudioVisualization = () => {
      if (!audioStream) return
      
      try {
        audioContext = new AudioContext()
        analyser = audioContext.createAnalyser()
        const microphone = audioContext.createMediaStreamSource(audioStream)
        
        microphone.connect(analyser)
        analyser.fftSize = 256
        
        const bufferLength = analyser.frequencyBinCount
        const dataArray = new Uint8Array(bufferLength)
        
        const updateAudioLevel = () => {
          if (!isTranscribing.value) return
          
          analyser.getByteFrequencyData(dataArray)
          
          // 计算音频级别
          let sum = 0
          for (let i = 0; i < bufferLength; i++) {
            sum += dataArray[i]
          }
          const average = sum / bufferLength
          audioLevel.value = Math.round((average / 255) * 100)
          
          // 继续下一帧
          if (isTranscribing.value) {
            requestAnimationFrame(updateAudioLevel)
          }
        }
        
        updateAudioLevel()

        // 启动视觉分析
        startVisionAnalysis()

      } catch (error) {
        console.error('启动音频可视化失败:', error)
      }
    }

    // 启动视觉分析
    const startVisionAnalysis = () => {
      // 每5秒截图一次进行分析
      const visionInterval = setInterval(() => {
        if (!isInterviewStarted.value || !userVideo.value) {
          clearInterval(visionInterval)
          return
        }

        captureAndAnalyzeFrame()
      }, 5000)

      // 保存定时器引用以便清理
      window.visionAnalysisInterval = visionInterval
      console.log('视觉分析定时器已启动')
    }

    // 截图并分析
    const captureAndAnalyzeFrame = () => {
      try {
        if (!userVideo.value || !socket.value || !socket.value.connected) return

        // 创建canvas截图
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        canvas.width = userVideo.value.videoWidth || 640
        canvas.height = userVideo.value.videoHeight || 480

        // 绘制当前视频帧
        ctx.drawImage(userVideo.value, 0, 0, canvas.width, canvas.height)

        // 转换为base64
        const imageData = canvas.toDataURL('image/jpeg', 0.8)

        // 发送到后端分析
        socket.value.emit('screenshot_data', {
          session_id: transcriptionSessionId.value,
          image_data: imageData
        })

        console.log('已发送截图数据进行视觉分析')

      } catch (error) {
        console.error('截图分析失败:', error)
      }
    }

    // 处理转写结果
    const handleTranscriptionResult = (text) => {
      transcriptionText.value = text
      console.log('转写结果:', text)
      
      // 如果转写完成，发送给NLP模型获取智能回复
      if (text.trim()) {
        getAIResponseForText(text)
      }
    }

    // 获取AI智能回复
    const getAIResponseForText = async (text) => {
      try {
        const response = await getInterviewAIResponse({
          question: '当前问题',
          userAnswer: text,
          mode: currentMode.value,
          position: interviewerType.value
        })
        
        if (response.success) {
          aiResponse.value = response.aiResponse
          
          // 更新反馈内容
          if (response.audioFeedback) {
            audioFeedback.value = response.audioFeedback
          }
          if (response.contentFeedback) {
            contentFeedback.value = response.contentFeedback
          }
        }
        
      } catch (error) {
        console.error('获取AI回复失败:', error)
      }
    }

    // 虚拟面试官相关方法
    const loadInterviewPreferences = async () => {
      try {
        const response = await fetch('/api/preferences/interview', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        })

        if (response.ok) {
          const result = await response.json()
          if (result.success) {
            interviewPreferences.value = result.data
            console.log('面试偏好加载成功:', result.data)

            // 初始化噪音干扰
            initializeNoiseInterference()
          }
        }
      } catch (error) {
        console.error('加载面试偏好失败:', error)
      }
    }

    const initializeNoiseInterference = () => {
      if (!interviewPreferences.value) return

      const noiseConfig = interviewPreferences.value.noise_config || {}
      const enabledNoises = noiseConfig.enabled_noises || []
      const noiseVolume = noiseConfig.noise_volume || 0.3

      // 初始化噪音音频
      enabledNoises.forEach(noiseType => {
        const audio = new Audio()
        audio.loop = true
        audio.volume = noiseVolume

        // 设置噪音音频源
        switch (noiseType) {
          case 'keyboard':
            audio.src = '/sounds/keyboard-typing.mp3'
            break
          case 'phone':
            audio.src = '/sounds/phone-ring.mp3'
            break
          case 'traffic':
            audio.src = '/sounds/traffic-noise.mp3'
            break
          case 'office':
            audio.src = '/sounds/office-ambient.mp3'
            break
          case 'custom':
            audio.src = noiseConfig.custom_noise_url || ''
            break
        }

        noiseAudios.value[noiseType] = audio
      })
    }

    const startNoiseInterference = () => {
      if (!interviewPreferences.value) return

      const noiseConfig = interviewPreferences.value.noise_config || {}
      const noiseFrequency = noiseConfig.noise_frequency || 0.2

      // 随机播放噪音
      Object.values(noiseAudios.value).forEach(audio => {
        if (Math.random() < noiseFrequency) {
          setTimeout(() => {
            audio.play().catch(e => console.log('噪音播放失败:', e))
          }, Math.random() * 10000) // 0-10秒内随机开始
        }
      })
    }

    const stopNoiseInterference = () => {
      Object.values(noiseAudios.value).forEach(audio => {
        audio.pause()
        audio.currentTime = 0
      })
    }

    const onAvatarVideoLoadStart = () => {
      avatarLoading.value = true
      avatarStatus.value = 'connecting'
    }

    const onAvatarVideoCanPlay = () => {
      avatarLoading.value = false
      avatarStatus.value = 'connected'
    }

    const onAvatarVideoError = (error) => {
      console.error('虚拟面试官视频加载失败:', error)
      avatarLoading.value = false
      avatarStatus.value = 'disconnected'
    }

    const getAvatarStatusText = () => {
      switch (avatarStatus.value) {
        case 'disconnected': return '未连接'
        case 'connecting': return '连接中'
        case 'connected': return '已连接'
        case 'speaking': return '正在说话'
        default: return '未知状态'
      }
    }

    // XRTC流处理方法
    const handleXrtcStream = (data) => {
      console.log('处理XRTC流:', data)
      xrtcStreamUrl.value = data.video_url
      xrtcStatus.value = 'connected'
      xrtcStatusText.value = '正在播放'

      // 显示浮窗
      isXrtcMinimized.value = false

      // 更新虚拟面试官状态
      avatarStatus.value = 'speaking'

      // 尝试播放XRTC流
      playXrtcStream(data.video_url)

      console.log('XRTC浮窗已显示:', {
        url: xrtcStreamUrl.value,
        status: xrtcStatus.value,
        text: data.text || '虚拟面试官正在说话'
      })
    }

    // 播放XRTC流 - 简化版本，主要逻辑已移至XrtcPlayer组件
    const playXrtcStream = async (streamUrl) => {
      console.log('XRTC流播放请求已转发至XrtcPlayer组件:', streamUrl)
      // 实际播放逻辑现在由XrtcPlayer组件处理
    }

    const toggleXrtcMinimize = () => {
      isXrtcMinimized.value = !isXrtcMinimized.value
      console.log('XRTC浮窗最小化状态:', isXrtcMinimized.value)
    }

    const closeXrtcWindow = () => {
      xrtcStreamUrl.value = ''
      xrtcStatus.value = 'disconnected'
      xrtcStatusText.value = '未连接'
      isXrtcMinimized.value = false
      console.log('XRTC浮窗已关闭')
    }

    // 拖动功能方法
    const startDrag = (event) => {
      isDragging.value = true
      const rect = event.target.closest('.xrtc-floating-window').getBoundingClientRect()
      dragOffset.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
      }

      // 添加全局事件监听
      document.addEventListener('mousemove', onDrag)
      document.addEventListener('mouseup', stopDrag)

      // 防止文本选择
      event.preventDefault()
      console.log('开始拖动XRTC浮窗')
    }

    const onDrag = (event) => {
      if (!isDragging.value) return

      const newX = event.clientX - dragOffset.value.x
      const newY = event.clientY - dragOffset.value.y

      // 限制拖动范围，防止拖出屏幕
      const maxX = window.innerWidth - 320 // 浮窗宽度
      const maxY = window.innerHeight - 100 // 最小高度

      windowPosition.value = {
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      }
    }

    const stopDrag = () => {
      isDragging.value = false

      // 移除全局事件监听
      document.removeEventListener('mousemove', onDrag)
      document.removeEventListener('mouseup', stopDrag)

      console.log('停止拖动XRTC浮窗，位置:', windowPosition.value)
    }

    // XRTC状态获取（简化版本）
    const getXrtcVideoStatusText = () => {
      if (xrtcVideoLoading.value) return '连接中...'
      if (xrtcVideoError.value) return '连接失败'
      return xrtcStatusText.value || '正常'
    }

    // XRTC播放器组件事件处理
    const onXrtcPlayerError = (error) => {
      console.error('XRTC播放器错误:', error)
      xrtcVideoError.value = true
      xrtcVideoLoading.value = false
      xrtcStatus.value = 'error'
      xrtcStatusText.value = '播放失败'
    }

    const onXrtcPlayerConnected = () => {
      console.log('XRTC播放器连接成功')
      xrtcVideoLoading.value = false
      xrtcVideoError.value = false
      xrtcStatus.value = 'playing'
      xrtcStatusText.value = '正在播放'
    }

    const onXrtcPlayerDisconnected = () => {
      console.log('XRTC播放器连接断开')
      xrtcStatus.value = 'disconnected'
      xrtcStatusText.value = '连接断开'
    }

    // WebSocket连接方法
    const connectWebSocket = () => {
      if (socket.value) {
        socket.value.disconnect()
      }

      // 检查用户认证状态
      const token = localStorage.getItem('access_token')
      const userInfo = localStorage.getItem('user_info')
      
      if (!token) {
        console.error('用户未登录，无法建立WebSocket连接')
        alert('用户未登录，请重新登录')
        return
      }

      console.log('当前用户信息:', userInfo)
      console.log('会话ID:', transcriptionSessionId.value)

      // 使用Socket.IO连接
      socket.value = io('http://localhost:5000', {
        auth: {
          token: token
        },
        query: {
          session_id: transcriptionSessionId.value
        }
      })

      socket.value.on('connect', () => {
        console.log('WebSocket连接成功')
        socketConnected.value = true

        // 加入面试会话房间
        socket.value.emit('join_interview', {
          session_id: transcriptionSessionId.value
        })
      })

      socket.value.on('disconnect', () => {
        console.log('WebSocket连接断开')
        socketConnected.value = false
      })

      socket.value.on('connect_error', (error) => {
        console.error('WebSocket连接错误:', error)
        if (error.message.includes('权限') || error.message.includes('无权访问')) {
          console.error('用户权限验证失败，可能需要重新登录')
          alert('用户权限验证失败，请重新登录')
        }
      })

      // 监听虚拟面试官视频流
      socket.value.on('avatar_video_stream', (data) => {
        console.log('收到虚拟面试官视频流:', data)
        if (data.video_url) {
          // 检查是否是XRTC流
          if (data.video_url.startsWith('xrtcs://')) {
            console.log('检测到XRTC流，显示浮窗:', data.video_url)
            handleXrtcStream(data)
          } else {
            // 普通HTTP视频流
            avatarVideoUrl.value = data.video_url
            avatarStatus.value = 'speaking'
          }
        }
      })

      // 监听表情反馈
      socket.value.on('avatar_expression', (data) => {
        console.log('收到表情反馈:', data)
        // 可以在这里触发表情动画
      })

      // 监听AI问题
      socket.value.on('ai_question', (data) => {
        console.log('收到AI问题:', data)
        if (data.content) {
          aiResponse.value = data.content
        }
        if (data.video_url) {
          avatarVideoUrl.value = data.video_url
          avatarStatus.value = 'speaking'
        }
      })

      // 监听面试结束
      socket.value.on('interview_ended', (data) => {
        console.log('面试结束:', data)
        stopInterview()
      })

      // 监听流式传输启动确认
      socket.value.on('streaming_started', (data) => {
        console.log('流式传输已启动:', data)
      })

      // 监听实时转写更新
      socket.value.on('transcription_update', (data) => {
        console.log('实时转写更新:', data.text)
        transcriptionText.value = data.text
      })

      // 监听AI反馈
      socket.value.on('ai_feedback', (data) => {
        console.log('收到AI反馈:', data.feedback)
        if (data.success) {
          aiResponse.value = data.feedback
        }
      })

      // 监听实时反馈更新
      socket.value.on('realtime_feedback', (data) => {
        console.log('收到实时反馈:', data)
        if (data.success && data.feedback) {
          // 直接更新反馈内容，不使用 || 操作符
          realTimeFeedback.value = {
            audio: data.feedback.audio || '语音表达暂无数据，建议保持适中语速，重音词汇当强调',
            behavior: data.feedback.behavior || '行为表现暂无数据，可注意保持自然眼神交流，手势与技术要点描述同步增强说服力',
            technical: data.feedback.technical || '技术内容尚未展开，建议选择具代表性项目，阐明编程技术如何破解具体工程难题（如算法优化/测试效率提升）',
            stress: data.feedback.stress || '压力应对状态未知，可预先用STAR法则结构化回答，突出技术决策和跨部门协作价值'
          }
          console.log('实时反馈已更新:', realTimeFeedback.value)
        }
      })

      // 监听新问题视频（WebSocket版本）
      socket.value.on('new_question_video', (data) => {
        console.log('收到新问题视频:', data)
        if (data.success) {
          if (data.finished) {
            // 面试完成
            finishInterview()
          } else {
            // 显示新问题
            currentQuestion.value = data.question
            currentQuestionNumber.value = data.question_number
            totalQuestions.value = data.total_questions
            aiResponse.value = data.question.content

            // 更新虚拟面试官视频
            if (data.video_url) {
              // 检查是否是XRTC流
              if (data.video_url.startsWith('xrtcs://')) {
                console.log('新问题检测到XRTC流，更新浮窗:', data.video_url)
                handleXrtcStream({
                  video_url: data.video_url,
                  stream_type: data.stream_type || 'xrtc',
                  text: data.question?.content || '新问题',
                  message: '虚拟面试官提问中'
                })
              } else {
                // 普通HTTP视频流
              avatarVideoUrl.value = data.video_url
              avatarStatus.value = 'speaking'
              }
            }

            console.log(`📝 WebSocket接收第${data.question_number}题: ${data.question.content}`)
          }
        }
      })

      socket.value.on('error', (error) => {
        console.error('WebSocket错误:', error)
      })
    }

    const disconnectWebSocket = () => {
      if (socket.value) {
        socket.value.disconnect()
        socket.value = null
        socketConnected.value = false
      }
    }

    // 面试流程控制方法
    const handleFirstQuestion = (questionData) => {
      // 如果是第一题，替换成固定的问题内容
      if (questionData.question_number === 1 || currentQuestionNumber.value === 0) {
        const customFirstQuestion = {
          ...questionData,
          content: '请解释什么是虚拟DOM，以及它的优势'
        }
        currentQuestion.value = customFirstQuestion
        currentQuestionNumber.value = 1
        aiResponse.value = customFirstQuestion.content
        console.log(`📝 第${currentQuestionNumber.value}题: ${customFirstQuestion.content}`)
      } else {
        currentQuestion.value = questionData
        currentQuestionNumber.value = questionData.question_number || 1
        aiResponse.value = questionData.content
        console.log(`📝 第${currentQuestionNumber.value}题: ${questionData.content}`)
      }

      // 启动流式传输
      startStreaming()
    }

    const startStreaming = () => {
      if (socket.value && socketConnected.value) {
        console.log('启动流式传输...')
        socket.value.emit('start_streaming', {
          session_id: transcriptionSessionId.value
        })
      }
    }



    const submitCurrentAnswer = () => {
      if (!userAnswer.value.trim()) {
        alert('请先回答当前问题')
        return
      }

      try {
        isAnswering.value = true

        console.log('✅ 提交答案到WebSocket')

        // 将答案添加到对话历史（通过WebSocket）
        if (socket.value && socketConnected.value) {
          // 先发送用户答案
          socket.value.emit('user_answer', {
            session_id: transcriptionSessionId.value,
            answer: userAnswer.value
          })

          // 然后请求生成下一题
          socket.value.emit('generate_next_question', {
            session_id: transcriptionSessionId.value
          })
        }

        // 显示等待状态
        aiResponse.value = '正在分析您的回答并生成下一题...'

        // 清空用户答案
        userAnswer.value = ''

      } catch (error) {
        console.error('❌ 提交答案失败:', error)
        alert('提交答案失败，请重试')
      } finally {
        isAnswering.value = false
      }
    }

    const getNextQuestion = async () => {
      try {
        isWaitingNextQuestion.value = true

        const { getNextQuestionNew } = await import('@/api/interview')
        const result = await getNextQuestionNew({
          session_id: transcriptionSessionId.value
        })

        if (result.success) {
          if (result.data.finished || currentQuestionNumber.value >= totalQuestions.value) {
            // 面试完成
            console.log('🏁 面试完成!')
            finishInterview()
          } else {
            // 显示下一题
            currentQuestion.value = result.data.question
            currentQuestionNumber.value = result.data.question_number
            totalQuestions.value = result.data.total_questions
            aiResponse.value = result.data.question.content

            // 更新虚拟面试官视频
            if (result.data.video_url) {
              avatarVideoUrl.value = result.data.video_url
              avatarStatus.value = 'speaking'
            }

            console.log(`📝 第${currentQuestionNumber.value}题: ${result.data.question.content}`)
          }
        } else {
          throw new Error(result.message || '获取下一题失败')
        }
      } catch (error) {
        console.error('❌ 获取下一题失败:', error)
        alert('获取下一题失败，请重试')
      } finally {
        isWaitingNextQuestion.value = false
      }
    }

    const finishInterview = async () => {
      try {
        const { endInterviewNew } = await import('@/api/interview')
        const result = await endInterviewNew({
          session_id: transcriptionSessionId.value
        })

        if (result.success) {
          interviewFinished.value = true
          interviewReport.value = result.data.report
          aiResponse.value = result.data.message

          console.log('📊 面试报告:', result.data.report)

          // 停止所有录制和连接
          stopInterview()
        } else {
          throw new Error(result.message || '结束面试失败')
        }
      } catch (error) {
        console.error('❌ 结束面试失败:', error)
        alert('结束面试失败')
      }
    }

    const skipCurrentQuestion = () => {
      if (confirm('确定要跳过当前问题吗？')) {
        userAnswer.value = '跳过此题'
        submitCurrentAnswer()
      }
    }

    // 其他方法
    const togglePause = () => {
      isPaused.value = !isPaused.value
    }

    const toggleFavorite = () => {
      console.log('收藏当前问题')
    }

    const setMode = (mode) => {
      console.log('设置面试模式:', mode)
      currentMode.value = mode
      console.log('当前模式:', currentMode.value)
    }

    const toggleAIFeedback = () => {
      aiFeedbackEnabled.value = !aiFeedbackEnabled.value
    }

    const toggleFeedbackCollapse = () => {
      isFeedbackCollapsed.value = !isFeedbackCollapsed.value
    }

    const setDifficulty = (level) => {
      difficulty.value = level
    }

    const setExpression = (expr) => {
      expression.value = expr
    }

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}:00`
    }

    const startTimer = () => {
      timer = setInterval(() => {
        if (!isPaused.value && isInterviewStarted.value) {
          currentTime.value++
        }
      }, 1000)
    }

    onMounted(async () => {
      startTimer()
      await loadInterviewConfig()
    })

    onUnmounted(() => {
      if (timer) {
        clearInterval(timer)
      }
      // 清理音频资源
      stopInterview()
    })

    return {
      // 基本状态
      isPaused,
      currentTime,
      currentMode,
      aiFeedbackEnabled,
      isFeedbackCollapsed,
      difficulty,
      expression,
      interviewerType,
      availablePositions,
      userTargetField,
      
      // 面试状态
      isInterviewStarted,
      isPreparingInterview,
      isTranscribing,
      transcriptionText,
      aiResponse,
      audioLevel,
      audioFeedback,
      contentFeedback,
      realTimeFeedback,

      // 面试流程状态
      currentQuestion,
      currentQuestionNumber,
      totalQuestions,
      userAnswer,
      isAnswering,
      isWaitingNextQuestion,
      interviewFinished,
      interviewReport,

      // 虚拟面试官状态
      avatarVideoUrl,
      avatarLoading,
      avatarStatus,
      avatarVideo,
      interviewPreferences,

      // XRTC流状态
      xrtcStreamUrl,
      xrtcStatus,
      xrtcStatusText,
      isXrtcMinimized,

      // 拖动状态
      isDragging,
      dragOffset,
      windowPosition,

      // XRTC视频状态（简化）
      xrtcVideoLoading,
      xrtcVideoError,

      // WebSocket状态
      socket,
      socketConnected,

      // 方法
      toggleInterview,
      togglePause,
      toggleFavorite,
      setMode,
      toggleAIFeedback,
      toggleFeedbackCollapse,
      setDifficulty,
      setExpression,
      formatTime,
      getFieldLabel,

      // 虚拟面试官方法
      loadInterviewPreferences,
      onAvatarVideoLoadStart,
      onAvatarVideoCanPlay,
      onAvatarVideoError,
      getAvatarStatusText,

      // XRTC流方法
      handleXrtcStream,
      toggleXrtcMinimize,
      closeXrtcWindow,

      // 拖动方法
      startDrag,
      onDrag,
      stopDrag,

      // XRTC方法（简化）
      playXrtcStream,
      getXrtcVideoStatusText,
      onXrtcPlayerError,
      onXrtcPlayerConnected,
      onXrtcPlayerDisconnected,

      // WebSocket方法
      connectWebSocket,
      disconnectWebSocket,

      // 视觉分析方法
      startVisionAnalysis,
      captureAndAnalyzeFrame,

      // 面试流程方法
      handleFirstQuestion,
      submitCurrentAnswer,
      getNextQuestion,
      finishInterview,
      skipCurrentQuestion,
      startStreaming,
      sendAudioData
    }
  }
}
</script>

<style scoped>
.interview-interface {
  display: flex;
  min-height: calc(100vh - 60px); /* 改为最小高度，允许内容超出时滚动 */
  background: #fff;
}

/* 左侧主要区域 - 移除高度限制，允许自然滚动 */
.main-content {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  /* 移除固定高度和overflow限制 */
}

/* 面包屑导航 */
.breadcrumb {
  padding: 8px 0 16px 0;
  font-size: 14px;
  color: #6b7280;
}

.breadcrumb-item {
  color: #6b7280;
}

.breadcrumb-item.active {
  color: #722ED1;
}

.breadcrumb-separator {
  margin: 0 8px;
}

/* 视频容器 - 移除固定高度限制 */
.main-video {
  background: #000;
  border-radius: 12px 12px 0 0; /* 只有上方圆角，下方直角为了贴住按钮 */
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 400px; /* 保持视频区域的基础高度 */
  margin-bottom: 0; /* 移除下边距，让按钮贴住 */
  /* 移除flex-shrink: 0，允许在需要时调整 */
}

.video-frame {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #89C3D4, #7FB069);
}

.interviewee-video {
  width: 100%;
  height: 100%;
  position: relative;
}

.user-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  background: #000;
  position: relative;
  z-index: 1;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid #722ED1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.placeholder-text {
  color: white;
  font-size: 18px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* 虚拟面试官窗口 */
.interviewer-window {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 200px;
  height: 150px;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #722ED1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-video-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.avatar-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.avatar-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.avatar-loading .loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #722ED1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

.avatar-loading .loading-text {
  font-size: 12px;
  color: #ccc;
}

.interviewer-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
}

.interviewer-placeholder .placeholder-text {
  font-size: 14px;
}

.interviewer-placeholder .placeholder-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}

.avatar-status {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  align-items: center;
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  color: white;
}

.avatar-status .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}

.avatar-status.disconnected .status-dot {
  background: #ff4d4f;
}

.avatar-status.connecting .status-dot {
  background: #faad14;
  animation: pulse-avatar 1s infinite;
}

.avatar-status.connected .status-dot {
  background: #52c41a;
}

.avatar-status.speaking .status-dot {
  background: #722ED1;
  animation: pulse-avatar 0.5s infinite;
}

@keyframes pulse-avatar {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 视频控制栏 */
.video-controls {
  background: rgba(0, 0, 0, 0.8);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  position: relative;
  z-index: 10;
}

.control-left,
.control-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  position: relative;
  z-index: 11;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.control-btn.active {
  background: #722ED1;
  border-color: #722ED1;
}

.control-btn.start-interview.active {
  background: #dc2626;
  border-color: #dc2626;
}

.btn-text {
  font-size: 12px;
}

.time-display {
  background: rgba(0, 0, 0, 0.5);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}

/* 转写指示器 */
.transcription-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(34, 197, 94, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.indicator-text {
  color: #22c55e;
  font-size: 11px;
}

/* 音频级别显示 */
.audio-level-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  min-width: 80px;
}

.level-bar {
  flex: 1;
  height: 4px;
  background: #00ff00;
  border-radius: 2px;
  transition: width 0.1s ease;
  max-width: 60px;
}

.level-text {
  font-size: 10px;
  color: white;
  min-width: 30px;
}

/* AI 实时反馈区域 - 放在开始面试按钮下方 */
.ai-feedback {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  margin-bottom: 20px;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  cursor: pointer;
  user-select: none;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}



.feedback-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.toggle-switch {
  width: 48px;
  height: 26px;
  background: #d1d5db;
  border-radius: 13px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-switch.active {
  background: #722ED1;
}

.toggle-slider {
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.toggle-switch.active .toggle-slider {
  transform: translateX(22px);
}

.feedback-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  transition: all 0.3s ease;
  overflow: hidden;
  margin-top: 24px;
}



.feedback-item {
  display: flex;
  align-items: flex-start;
  padding: 0;
  background: transparent;
  border-radius: 0;
}

.feedback-icon {
  width: 32px;
  height: 32px;
  margin-right: 16px;
  flex-shrink: 0;
  background: #f3f0ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.feedback-content {
  flex: 1;
}

.feedback-content .feedback-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.feedback-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

/* 开始面试按钮区域 - 全宽度，贴住视频下方 */
.interview-control-section {
  width: 100%;
  margin: 0;
  padding: 0;
  margin-bottom: 20px;
  margin-top: -12px; /* 向上移动，贴住视频区域 */
  position: relative;
  z-index: 10;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-radius: 0 0 16px 16px;
  overflow: hidden;
  transform: translateZ(0);
}

.control-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  padding: 12px 24px;
  border-radius: 0 0 16px 16px;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
  min-height: 60px;
}

.main-interview-btn {
  background: transparent;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.main-interview-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.main-interview-btn.preparing {
  background: rgba(255, 255, 255, 0.1);
  cursor: not-allowed;
}

.timer-display {
  color: white;
  font-size: 16px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.main-interview-btn:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

/* 按钮内容布局 */
.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
}

.btn-icon {
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  backdrop-filter: blur(4px);
}

.btn-text {
  font-size: 18px;
  letter-spacing: 0.5px;
}

.btn-info {
  display: flex;
  align-items: center;
  gap: 24px;
  font-size: 14px;
  opacity: 0.9;
  position: relative;
  z-index: 2;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 14px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.timer-icon {
  font-size: 16px;
}

.timer-text {
  font-weight: 700;
  font-size: 16px;
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

.status-display {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.status-dot {
  width: 10px;
  height: 10px;
  background: #10B981;
  border-radius: 50%;
  animation: pulse 2s infinite;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
}

.status-text {
  font-size: 14px;
  font-weight: 500;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 3px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 3px;
}

.loading-spinner-small {
  width: 12px; /* 一半大小 */
  height: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-top: 1px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.btn-icon {
  font-size: 12px; /* 一半大小 */
}

.btn-text {
  font-size: 12px; /* 一半大小 */
}

/* 中间计时区域 */
.control-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.timer-display {
  display: flex;
  align-items: center;
  gap: 3px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  padding: 3px 6px; /* 一半大小 */
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.timer-icon {
  font-size: 12px; /* 一半大小 */
}

.timer-text {
  font-size: 11px; /* 一半大小 */
  font-family: 'Courier New', monospace;
}

/* 右侧状态区域 */
.control-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  min-width: 80px; /* 一半宽度 */
  justify-content: flex-end;
}

.transcription-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  background: rgba(16, 185, 129, 0.25);
  padding: 6px 12px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(16, 185, 129, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.transcription-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.interview-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  background: rgba(34, 197, 94, 0.25);
  padding: 6px 12px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(34, 197, 94, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.interview-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.ready-status {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.ready-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}


.status-dot {
  width: 4px; /* 一半大小 */
  height: 4px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 10px; /* 一半大小 */
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 实时转写结果区域 */
.transcription-result {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
}

.transcription-header {
  margin-bottom: 16px;
}

.transcription-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.transcription-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.transcription-text {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  margin: 0;
}

.ai-response-panel {
  background: #f0fdf4;
  border-left: 4px solid #22c55e;
  padding: 12px;
  border-radius: 4px;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
  color: #16a34a;
}

.interview-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.progress-bar {
  width: 100px;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #22c55e;
  transition: width 0.3s ease;
}

/* 答题区域样式 */
.answer-section {
  background: #fefefe;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.answer-title {
  font-weight: 600;
  color: #374151;
}

.answer-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: #722ED1;
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: #5a1ea6;
}

.action-btn.secondary {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.answer-input textarea {
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 100px;
}

.answer-input textarea:focus {
  outline: none;
  border-color: #722ED1;
  box-shadow: 0 0 0 3px rgba(114, 46, 209, 0.1);
}

.answer-input textarea:disabled {
  background: #f9fafb;
  color: #6b7280;
}

/* 面试报告样式 */
.interview-report {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
}

.report-header h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
}

.report-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.report-summary {
  background: white;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.report-summary p {
  margin: 0;
  color: #475569;
  line-height: 1.6;
}

.response-header {
  font-size: 12px;
  font-weight: 600;
  color: #22c55e;
  margin-bottom: 8px;
}

.response-content {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

/* 右侧控制面板 - 确保在小屏幕时也能正常显示 */
.control-panel {
  width: 300px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-left: 16px;
  height: fit-content; /* 高度自适应内容 */
  position: sticky; /* 可选：让控制面板在滚动时保持可见 */
  top: 16px; /* 距离顶部的距离 */
}

.panel-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 20px 0;
}

/* 面试模式选择 */
.interview-modes {
  margin-bottom: 24px;
}

.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.mode-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.mode-item:hover {
  border-color: #722ED1;
}

.mode-item.active {
  background: #F9F0FF;
  border-color: #722ED1;
}

.mode-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-icon .svg-icon {
  color: #6b7280;
}

.mode-name {
  font-size: 12px;
  color: #374151;
  text-align: center;
}

.mode-item.active .mode-name {
  color: #374151;
}

.mode-item.active .mode-icon .svg-icon {
  color: #722ED1 !important;
}

/* 确保所有面试模式图标都能正确显示颜色 */
.mode-item .mode-icon .svg-icon {
  transition: color 0.2s ease;
}

/* 设置选项 */
.settings-section {
  margin-top: 20px;
}

.setting-group {
  margin-bottom: 20px;
}

.setting-label {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.setting-label.sub-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.difficulty-options,
.expression-options {
  display: flex;
  gap: 4px;
}

.difficulty-btn,
.expression-btn {
  flex: 1;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
  text-align: center;
}

.difficulty-btn:hover,
.expression-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.difficulty-btn.active,
.expression-btn.active {
  background: #F9F0FF;
  border-color: #722ED1;
  color: #722ED1;
}

.interviewer-selection {
  margin-top: 8px;
}

.interviewer-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
}

.interviewer-select:focus {
  outline: none;
  border-color: #722ED1;
  box-shadow: 0 0 0 3px rgba(114, 45, 209, 0.1);
}

/* 响应式设计 - 在小屏幕时调整布局 */
@media (max-width: 1024px) {
  .interview-interface {
    flex-direction: column;
  }
  
  .control-panel {
    width: 100%;
    margin-left: 0;
    margin-top: 16px;
    position: static; /* 在小屏幕时取消sticky定位 */
  }

  .xrtc-floating-window {
    width: 280px;
    top: 10px;
    right: 10px;
  }
}

@media (max-width: 768px) {
  .xrtc-floating-window {
    width: calc(100vw - 20px);
    left: 10px;
    right: 10px;
    top: 10px;
  }
}

/* XRTC虚拟人浮窗样式 */
.xrtc-floating-window {
  position: fixed;
  width: 320px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
  z-index: 1000;
  transition: box-shadow 0.3s ease;
  user-select: none;
}

.xrtc-floating-window.dragging {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25);
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

.xrtc-floating-window.minimized {
  height: 50px;
  overflow: hidden;
}

.xrtc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  cursor: move;
}

.xrtc-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: move;
  flex: 1;
}

.drag-hint {
  margin-left: auto;
  opacity: 0.6;
  font-size: 12px;
}

.xrtc-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff4444;
  transition: background-color 0.3s ease;
}

.xrtc-status-dot.connected {
  background: #44ff44;
  animation: pulse 2s infinite;
}

.xrtc-status-dot.playing {
  background: #44ff44;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.xrtc-controls {
  display: flex;
  gap: 4px;
}

.xrtc-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background-color 0.2s ease;
}

.xrtc-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.xrtc-content {
  padding: 0;
  height: 400px; /* 固定浮窗内容高度 */
  display: flex;
  flex-direction: column;
}

.xrtc-stream-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.xrtc-stream-info {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.stream-url {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #666;
  word-break: break-all;
  margin-bottom: 4px;
}

.stream-status {
  font-size: 12px;
  color: #28a745;
  font-weight: 500;
}

.xrtc-placeholder {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  border: 2px dashed #667eea;
}

.xrtc-avatar {
  font-size: 32px;
  margin-bottom: 8px;
}

.xrtc-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

/* XRTC视频容器 - 占2/3高度 */
.xrtc-video-container {
  flex: 2;
  position: relative;
  background: #000;
  border-radius: 12px 12px 0 0;
  overflow: hidden;
}

.xrtc-video-fullsize {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.xrtc-video-loading-fullsize {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  color: white;
}

.loading-spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-text-large {
  font-size: 14px;
  text-align: center;
  color: white;
}

.virtual-avatar-fullsize {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar-animation-large {
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: avatarBreathe 3s ease-in-out infinite;
}

.avatar-face-large {
  font-size: 60px;
  margin-bottom: 8px;
  animation: avatarBlink 4s ease-in-out infinite;
}

.avatar-body-large {
  font-size: 40px;
}

.speaking-indicator-large {
  display: flex;
  gap: 4px;
  margin-top: 16px;
  opacity: 1;
}

.wave-large {
  width: 4px;
  height: 20px;
  background: white;
  border-radius: 2px;
  animation: wave 1.5s ease-in-out infinite;
}

.wave-large:nth-child(2) {
  animation-delay: 0.2s;
}

.wave-large:nth-child(3) {
  animation-delay: 0.4s;
}

.fallback-text-large {
  font-size: 14px;
  color: white;
  margin-top: 12px;
  text-align: center;
}

.xrtc-video-controls-fullsize {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.xrtc-video-container:hover .xrtc-video-controls-fullsize {
  opacity: 1;
}

.control-btn-large {
  background: rgba(0, 0, 0, 0.7);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: background-color 0.2s ease;
}

.control-btn-large:hover {
  background: rgba(0, 0, 0, 0.9);
}

/* XRTC视频播放器样式 */
.xrtc-video-player {
  position: relative;
  width: 120px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.xrtc-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.xrtc-video-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: white;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 10px;
  text-align: center;
}

.virtual-avatar-fallback {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
}

.fallback-text {
  font-size: 10px;
  color: white;
  margin-top: 4px;
  text-align: center;
}

.xrtc-video-controls {
  position: absolute;
  bottom: 4px;
  right: 4px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.xrtc-video-player:hover .xrtc-video-controls {
  opacity: 1;
}

.control-btn {
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  transition: background-color 0.2s ease;
}

.control-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.virtual-avatar {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: avatarBreathe 3s ease-in-out infinite;
}

.avatar-face {
  font-size: 32px;
  margin-bottom: 4px;
  animation: avatarBlink 4s ease-in-out infinite;
}

.avatar-body {
  font-size: 24px;
}

@keyframes avatarBreathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes avatarBlink {
  0%, 90%, 100% { opacity: 1; }
  95% { opacity: 0.3; }
}

.speaking-indicator {
  display: flex;
  gap: 2px;
  margin-top: 8px;
  opacity: 0.3;
  transition: opacity 0.3s ease;
}

.speaking-indicator.active {
  opacity: 1;
}

.wave {
  width: 3px;
  height: 12px;
  background: white;
  border-radius: 2px;
  animation: wave 1.5s ease-in-out infinite;
}

.wave:nth-child(2) {
  animation-delay: 0.2s;
}

.wave:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes wave {
  0%, 100% { height: 8px; }
  50% { height: 16px; }
}

.avatar-info {
  flex: 1;
}

.avatar-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.avatar-status {
  font-size: 12px;
  opacity: 0.8;
}

/* 底部问题区域 - 占1/3高度 */
.current-question-bottom {
  flex: 1;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 0 0 12px 12px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.question-label-bottom {
  font-size: 12px;
  color: #666;
  font-weight: 600;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.question-text-bottom {
  font-size: 13px;
  color: #333;
  line-height: 1.5;
  flex: 1;
  overflow-y: auto;
  word-wrap: break-word;
}
</style>