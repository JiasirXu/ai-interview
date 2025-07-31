<template>
  <div class="interview-preferences">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">处理中...</div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" :class="['message-toast', messageType]">
      {{ message }}
    </div>

    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item">模拟面试</span>
      <span class="breadcrumb-separator">></span>
      <span class="breadcrumb-item current">偏好设置</span>
    </div>

    <h1 class="page-title">虚拟面试官定制</h1>

    <!-- 形象风格 -->
    <div class="preferences-section">
      <h2 class="section-title">形象风格</h2>
      <div class="avatar-grid">
        <div
          class="avatar-item"
          v-for="index in 5"
          :key="index"
          :class="{ active: preferences.selectedAvatar === index - 1 }"
          @click="selectAvatar(index - 1)"
        >
          <div class="avatar-image">
            <img
              :src="getAvatarImage(index)"
              :alt="`风格 ${index}`"
              class="avatar-photo"
            />
          </div>
          <div class="avatar-label">{{ getAvatarName(index) }}</div>
        </div>
      </div>
    </div>

    <!-- 互动模式 -->
    <div class="preferences-section">
      <h2 class="section-title">互动模式</h2>
      <div class="interaction-modes">
        <div
          class="mode-item"
          v-for="mode in interactionModes"
          :key="mode.value"
          :class="{ active: preferences.interactionMode === mode.value }"
          @click="setInteractionMode(mode.value)"
        >
          {{ mode.label }}
        </div>
      </div>
    </div>

    <!-- 微表情反馈 -->
    <div class="preferences-section">
      <h2 class="section-title">微表情反馈</h2>
      <div class="feedback-options">
        <label 
          class="feedback-item" 
          v-for="feedback in feedbackOptions" 
          :key="feedback.value"
        >
          <input 
            type="checkbox" 
            :checked="preferences.feedbacks.includes(feedback.value)"
            @change="toggleFeedback(feedback.value)"
          />
          <span class="checkmark"></span>
          <span class="feedback-label">{{ feedback.label }}</span>
        </label>
      </div>
    </div>

    <!-- 语音特性 -->
    <div class="preferences-section">
      <h2 class="section-title">语音特性</h2>
      <div class="voice-settings">
        <div class="voice-row">
          <span class="voice-label">语速调节</span>
          <div class="speed-slider">
            <input 
              type="range" 
              min="0.5" 
              max="2" 
              step="0.1" 
              v-model="preferences.voiceSpeed"
              class="slider"
            />
            <div class="speed-labels">
              <span>慢</span>
              <span>标准</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <h1 class="page-title">回放与记录</h1>

    <!-- 自动录像设置 -->
    <div class="preferences-section">
      <h2 class="section-title">自动录像设置</h2>
      <div class="recording-options">
        <label class="recording-item">
          <input 
            type="radio" 
            name="recordingType" 
            value="text"
            :checked="preferences.recordingType === 'text'"
            @change="setRecordingType('text')"
          />
          <span class="radio-mark"></span>
          <span class="recording-label">仅文字记录</span>
        </label>
        <label class="recording-item">
          <input 
            type="radio" 
            name="recordingType" 
            value="audio"
            :checked="preferences.recordingType === 'audio'"
            @change="setRecordingType('audio')"
          />
          <span class="radio-mark"></span>
          <span class="recording-label">仅录音</span>
        </label>
        <label class="recording-item">
          <input 
            type="radio" 
            name="recordingType" 
            value="video"
            :checked="preferences.recordingType === 'video'"
            @change="setRecordingType('video')"
          />
          <span class="radio-mark"></span>
          <span class="recording-label">视频+屏幕录制</span>
        </label>
      </div>
    </div>

    <!-- AI高光剪辑 -->
    <div class="preferences-section">
      <div class="ai-feature">
        <div class="feature-info">
          <div class="feature-title">AI高光剪辑</div>
          <div class="feature-desc">自动生成30秒"最佳表现"片段</div>
        </div>
        <div class="toggle-switch" :class="{ active: preferences.aiHighlight }" @click="preferences.aiHighlight = !preferences.aiHighlight">
          <div class="toggle-slider"></div>
        </div>
      </div>
    </div>

    <!-- 标记改进片段 -->
    <div class="preferences-section">
      <div class="ai-feature">
        <div class="feature-info">
          <div class="feature-title">标记"改进片段"</div>
          <div class="feature-desc">生成训练专题</div>
        </div>
        <div class="toggle-switch" :class="{ active: preferences.improvementMarking }" @click="preferences.improvementMarking = !preferences.improvementMarking">
          <div class="toggle-slider"></div>
        </div>
      </div>
    </div>

    <!-- 噪音干扰 -->
    <div class="preferences-section">
      <h2 class="section-title">噪音干扰</h2>
      <div class="noise-options">
        <label class="noise-item">
          <input 
            type="checkbox" 
            :checked="preferences.noises.includes('keyboard')"
            @change="toggleNoise('keyboard')"
          />
          <span class="checkmark"></span>
          <span class="noise-label">模拟键盘声</span>
        </label>
        <label class="noise-item">
          <input 
            type="checkbox" 
            :checked="preferences.noises.includes('phone')"
            @change="toggleNoise('phone')"
          />
          <span class="checkmark"></span>
          <span class="noise-label">电话铃声</span>
        </label>
        <label class="noise-item">
          <input 
            type="checkbox" 
            :checked="preferences.noises.includes('custom')"
            @change="toggleNoise('custom')"
          />
          <span class="checkmark"></span>
          <span class="noise-label">自定义噪音</span>
        </label>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="save-section">
      <button class="save-btn primary" @click="savePreferences" :disabled="loading">
        <span v-if="loading">保存中...</span>
        <span v-else>一键保存配置</span>
      </button>
      <button class="save-btn secondary" @click="resetPreferences" :disabled="loading">
         恢复默认
      </button>
    </div>
  </div>
</template>

<script>
import { reactive, ref, onMounted } from 'vue'
import {
  getInterviewPreferences,
  updateInterviewPreferences
} from '@/api/preference'

// 添加状态管理
const loading = ref(false)
const message = ref('')
const messageType = ref('success')

export default {
  name: 'InterviewPreferences',
  setup() {
    const preferences = reactive({
      selectedAvatar: 0,
      interactionMode: 'frequent',
      feedbacks: ['nod'],
      voiceSpeed: 1.0,
      recordingType: 'video',
      aiHighlight: true,
      improvementMarking: true,
      noises: ['keyboard']
    })



    const interactionModes = [
      { value: 'frequent', label: '高频询问型' },
      { value: 'listener', label: '倾听型' },
      { value: 'counter', label: '反问型' }
    ]

    const feedbackOptions = [
      { value: 'nod', label: '点头认可' },
      { value: 'frown', label: '皱眉质疑' },
      { value: 'timer', label: '计时焦虑表情' }
    ]

    const selectAvatar = (index) => {
      preferences.selectedAvatar = index
    }

    // 获取头像图片路径
    const getAvatarImage = (index) => {
      const imageMap = {
        1: require('@/components/interview/1.png'),
        2: require('@/components/interview/2.jpg'),
        3: require('@/components/interview/3.png'),
        4: require('@/components/interview/4.png'),
        5: require('@/components/interview/5.png')
      }
      return imageMap[index] || imageMap[1]
    }

    // 获取头像名字
    const getAvatarName = (index) => {
      const nameMap = {
        1: '梦萱',
        2: '超哥',
        3: '婉仪',
        4: '诗雅',
        5: '浩然'
      }
      return nameMap[index] || '未知'
    }

    const setInteractionMode = (mode) => {
      preferences.interactionMode = mode
    }

    const toggleFeedback = (feedback) => {
      const index = preferences.feedbacks.indexOf(feedback)
      if (index > -1) {
        preferences.feedbacks.splice(index, 1)
      } else {
        preferences.feedbacks.push(feedback)
      }
    }

    const setRecordingType = (type) => {
      preferences.recordingType = type
    }

    const toggleNoise = (noise) => {
      const index = preferences.noises.indexOf(noise)
      if (index > -1) {
        preferences.noises.splice(index, 1)
      } else {
        preferences.noises.push(noise)
      }
    }

    const testVoice = async () => {
      try {
        loading.value = true
        console.log('测试语音播放，语速:', preferences.voiceSpeed)

        // 调用后端语音试听接口
        const response = await fetch('/api/preferences/interview/test-voice', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({
            voice_speed: preferences.voiceSpeed,
            test_text: '您好，我是您的虚拟面试官，很高兴为您进行面试。'
          })
        })

        const result = await response.json()
        if (result.success) {
          // 播放试听音频
          if (result.audio_url) {
            const audio = new Audio(result.audio_url)
            audio.play()
          }
          showMessage('语音试听成功', 'success')
        } else {
          showMessage(result.message || '语音试听失败', 'error')
        }
      } catch (error) {
        console.error('语音试听失败:', error)
        showMessage('语音试听失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const savePreferences = async () => {
      try {
        loading.value = true
        console.log('保存偏好设置:', preferences)

        // 构建完整的面试配置数据
        const interviewConfig = {
          avatar_config: {
            avatar_style: preferences.selectedAvatar,
            avatar_gender: 'neutral',
            avatar_age_range: 'middle'
          },
          interaction_config: {
            interaction_mode: preferences.interactionMode,
            question_frequency: preferences.interactionMode === 'frequent' ? 3.0 :
                               preferences.interactionMode === 'listener' ? 1.0 : 2.0,
            follow_up_probability: preferences.interactionMode === 'counter' ? 0.6 : 0.3
          },
          expression_config: {
            enabled_expressions: preferences.feedbacks,
            expression_intensity: 0.7,
            expression_frequency: 0.5
          },
          voice_config: {
            voice_speed: preferences.voiceSpeed,
            voice_pitch: 1.0,
            voice_volume: 0.8,
            voice_style: 'professional'
          },
          recording_config: {
            recording_type: preferences.recordingType,
            auto_recording: true,
            recording_quality: 'medium',
            ai_highlight: preferences.aiHighlight,
            improvement_marking: preferences.improvementMarking,
            auto_summary: true
          },
          noise_config: {
            enabled_noises: preferences.noises,
            noise_volume: 0.3,
            noise_frequency: 0.2,
            custom_noise_url: ''
          },
          advanced_config: {
            ai_model: 'spark',
            response_delay: 1000,
            context_memory: 5,
            difficulty_adaptation: true
          },
          metadata: {
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            version: '1.0.0'
          }
        }

        // 调用后端保存接口
        const response = await updateInterviewPreferences(interviewConfig)

        if (response.success) {
          showMessage('偏好设置保存成功', 'success')
        } else {
          showMessage(response.message || '保存失败', 'error')
        }
      } catch (error) {
        console.error('保存偏好设置失败:', error)
        showMessage('保存失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const resetPreferences = () => {
      Object.assign(preferences, {
        selectedAvatar: 0,
        interactionMode: 'frequent',
        feedbacks: ['nod'],
        voiceSpeed: 1.0,
        recordingType: 'video',
        aiHighlight: true,
        improvementMarking: true,
        noises: ['keyboard']
      })
      showMessage('已恢复默认设置', 'success')
    }

    // 消息提示函数
    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }

    // 加载用户的面试偏好设置
    const loadPreferences = async () => {
      try {
        loading.value = true
        const response = await getInterviewPreferences()

        if (response.success && response.data) {
          const config = response.data

          // 从后端数据映射到前端状态
          if (config.avatar_config) {
            preferences.selectedAvatar = config.avatar_config.avatar_style || 0
          }

          if (config.interaction_config) {
            preferences.interactionMode = config.interaction_config.interaction_mode || 'frequent'
          }

          if (config.expression_config) {
            preferences.feedbacks = config.expression_config.enabled_expressions || ['nod']
          }

          if (config.voice_config) {
            preferences.voiceSpeed = config.voice_config.voice_speed || 1.0
          }

          if (config.recording_config) {
            preferences.recordingType = config.recording_config.recording_type || 'video'
            preferences.aiHighlight = config.recording_config.ai_highlight !== false
            preferences.improvementMarking = config.recording_config.improvement_marking !== false
          }

          if (config.noise_config) {
            preferences.noises = config.noise_config.enabled_noises || []
          }

          console.log('面试偏好设置加载成功:', preferences)
        }
      } catch (error) {
        console.error('加载面试偏好设置失败:', error)
        showMessage('加载设置失败', 'error')
      } finally {
        loading.value = false
      }
    }

    // 组件挂载时加载设置
    onMounted(() => {
      loadPreferences()
    })

    return {
      preferences,
      interactionModes,
      feedbackOptions,
      loading,
      message,
      messageType,
      selectAvatar,
      getAvatarImage,
      getAvatarName,
      setInteractionMode,
      toggleFeedback,
      setRecordingType,
      toggleNoise,
      testVoice,
      savePreferences,
      resetPreferences,
      showMessage,
      loadPreferences
    }
  }
}
</script>

<style scoped>
.interview-preferences {
  /* 移除 max-width 限制，改为铺满 */
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 24px;
  background: #fff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #6b7280;
}

.breadcrumb-item {
  color: #6b7280;
}

.breadcrumb-item.current {
  color: #722ED1;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 8px;
  color: #9ca3af;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin: 32px 0 24px 0;
}

.preferences-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 16px;
}

/* 形象风格 */
.avatar-grid {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.avatar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid transparent;
  transition: border-color 0.2s;
  margin-bottom: 8px;
  position: relative;
}

.avatar-item.active .avatar-image {
  border-color: #722ED1;
  box-shadow: 0 0 0 2px rgba(114, 46, 209, 0.2);
}

.avatar-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  border-radius: 50%;
  transition: transform 0.2s;
}

.avatar-item:hover .avatar-photo {
  transform: scale(1.05);
}

.avatar-item.active .avatar-photo {
  transform: scale(1.02);
}

.avatar-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.avatar-item.active .avatar-label {
  color: #722ED1;
}

/* 互动模式 */
.interaction-modes {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.mode-item {
  background: #f3f0ff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #722ED1;
  transition: all 0.2s;
}

.mode-item:hover {
  border-color: #722ED1;
  background: #ede9fe;
}

.mode-item.active {
  background: #722ED1;
  border-color: #722ED1;
  color: white;
}

/* 微表情反馈 */
.feedback-options {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.feedback-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.feedback-item input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 18px;
  height: 18px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.2s;
}

.feedback-item input[type="checkbox"]:checked + .checkmark {
  background: #722ED1;
  border-color: #722ED1;
}

.feedback-item input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 12px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 语音设置 */
.voice-settings {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  
}

.voice-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.voice-label {
  font-size: 14px;
  color: #495057;
  font-weight: 500;
  min-width: 80px;
  padding-top: 0;
}

.speed-slider {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
  padding-top: 22px;
}

.slider {
  width: 200px;
  height: 4px;
  background: #dee2e6;
  border-radius: 2px;
  outline: none;
  appearance: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #722ED1;
  border-radius: 50%;
  cursor: pointer;
}

.speed-labels {
  display: flex;
  justify-content: space-between;
  width: 200px;
  font-size: 12px;
  color: #6b7280;
}

/* 题目跳转规则 */
.jump-rules {
  display: flex;
  gap: 24px;
}

.rule-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.rule-item input[type="radio"] {
  display: none;
}

.radio-mark {
  width: 18px;
  height: 18px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 50%;
  margin-right: 8px;
  position: relative;
  transition: all 0.2s;
}

.rule-item input[type="radio"]:checked + .radio-mark {
  border-color: #722ED1;
}

.rule-item input[type="radio"]:checked + .radio-mark::after {
  content: '';
  width: 8px;
  height: 8px;
  background: #722ED1;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 中断模拟 */
.interrupt-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.interrupt-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.interrupt-item input[type="checkbox"] {
  display: none;
}

/* 打断频率 */
.frequency-setting {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.frequency-slider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.frequency-labels {
  display: flex;
  justify-content: space-between;
  width: 300px;
  font-size: 12px;
  color: #6b7280;
}

/* 自动录像设置 */
.recording-options {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.recording-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.recording-item input[type="radio"] {
  display: none;
}

.radio-mark {
  width: 18px;
  height: 18px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 50%;
  margin-right: 8px;
  position: relative;
  transition: all 0.2s;
}

.recording-item input[type="radio"]:checked + .radio-mark {
  border-color: #722ED1;
}

.recording-item input[type="radio"]:checked + .radio-mark::after {
  content: '';
  width: 8px;
  height: 8px;
  background: #722ED1;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* AI功能设置 */
.ai-feature {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.feature-info {
  flex: 1;
}

.feature-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 14px;
  color: #6b7280;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #dee2e6;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.toggle-switch.active {
  background: #722ED1;
}

.toggle-slider {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.toggle-switch.active .toggle-slider {
  transform: translateX(20px);
}

/* 噪音干扰 */
.noise-options {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.noise-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #495057;
}

.noise-item input[type="checkbox"] {
  display: none;
}

.noise-item .checkmark {
  width: 18px;
  height: 18px;
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  border-radius: 4px;
  margin-right: 8px;
  position: relative;
  transition: all 0.2s;
}

.noise-item input[type="checkbox"]:checked + .checkmark {
  background: #722ED1;
  border-color: #722ED1;
}

.noise-item input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  color: white;
  font-size: 12px;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 保存按钮区域 */
.save-section {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 40px;
  margin-top: 40px;
  border-top: 1px solid #e9ecef;
}

.save-btn {
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-btn.primary {
  background: #722ED1;
  color: white;
}

.save-btn.primary:hover {
  background: #5b21b6;
}

.save-btn.secondary {
  background: #ffffff;
  color: #6b7280;
  border: 1px solid #dee2e6;
}

.save-btn.secondary:hover {
  background: #f8f9fa;
  color: #495057;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #722ED1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 16px;
  font-size: 16px;
  color: #722ED1;
}

/* 消息提示 */
.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  z-index: 10000;
  animation: slideIn 0.3s ease-out;
}

.message-toast.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.message-toast.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 禁用状态 */
.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-btn:disabled:hover {
  background: inherit;
  color: inherit;
}
</style>