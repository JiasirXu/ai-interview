import request from '@/utils/request'

/**
 * 面试相关业务逻辑API
 * 包括面试设置、录制控制、状态管理、AI服务等
 */

// ==================== 面试核心功能 ====================

/**
 * 开始面试 - 与后端interview_controller.py对应
 */
export function startInterview(interviewConfig) {
  return request.post('/api/interview/start', interviewConfig)
}

/**
 * 获取下一题 - 与后端interview_controller.py对应（旧版本）
 */
export function getNextQuestionOld(questionParams) {
  return request.post('/api/interview/question', questionParams)
}

/**
 * 提交答案 - 与后端interview_controller.py对应
 */
export function submitAnswer(answerData) {
  return request.post('/api/interview/answer', answerData)
}

/**
 * 结束面试 - 与后端interview_controller.py对应
 */
export function endInterview(interviewData) {
  return request.post('/api/interview/end', interviewData)
}

/**
 * 获取面试列表 - 与后端interview_controller.py对应
 */
export function getInterviewList(params) {
  return request.get('/api/interview/list', { params })
}

// ==================== 面试设置接口 ====================

/**
 * 更新面试模式
 * @param {Object} params - 模式参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.mode - 面试模式 (technical/pressure/case/comprehensive)
 * @returns {Promise}
 */
export function updateInterviewMode(params) {
  return request.post('/interview/mode/update', params)
}

/**
 * 更新面试难度
 * @param {Object} params - 难度参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.difficulty - 难度级别 (primary/middle/high)
 * @returns {Promise}
 */
export function updateInterviewDifficulty(params) {
  return request.post('/interview/difficulty/update', params)
}

/**
 * 更新面试官表情
 * @param {Object} params - 表情参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.expression - 表情类型 (friendly/serious/pressure)
 * @returns {Promise}
 */
export function updateInterviewerExpression(params) {
  return request.post('/interview/expression/update', params)
}

/**
 * 更新岗位选择
 * @param {Object} params - 岗位参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.position - 岗位类型
 * @returns {Promise}
 */
export function updateInterviewPosition(params) {
  return request.post('/interview/position/update', params)
}

// ==================== 面试录制和控制接口 ====================

/**
 * 开始面试录制
 * @param {Object} params - 录制参数
 * @param {string} params.session_id - 面试会话ID
 * @param {Object} params.media_config - 媒体配置
 * @param {boolean} params.media_config.audio - 是否录制音频
 * @param {boolean} params.media_config.video - 是否录制视频
 * @param {string} params.media_config.quality - 录制质量
 * @returns {Promise}
 */
export function startRecording(params) {
  return request.post('/interview/recording/start', params)
}

/**
 * 暂停/恢复面试录制
 * @param {Object} params - 控制参数
 * @param {string} params.session_id - 面试会话ID
 * @param {boolean} params.is_paused - 是否暂停
 * @returns {Promise}
 */
export function toggleRecording(params) {
  return request.post('/interview/recording/toggle', params)
}

/**
 * 停止面试录制
 * @param {Object} params - 停止参数
 * @param {string} params.session_id - 面试会话ID
 * @returns {Promise}
 */
export function stopRecording(params) {
  return request.post('/interview/recording/stop', params)
}

/**
 * 获取录制状态
 * @param {string} sessionId - 面试会话ID
 * @returns {Promise}
 */
export function getRecordingStatus(sessionId) {
  return request.get(`/interview/recording/status/${sessionId}`)
}

// ==================== 面试状态管理接口 ====================

/**
 * 获取面试会话信息
 * @param {string} sessionId - 面试会话ID
 * @returns {Promise}
 */
export function getInterviewSession(sessionId) {
  return request.get(`/interview/session/${sessionId}`)
}

/**
 * 更新面试会话状态
 * @param {Object} params - 状态参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.status - 状态 (active/paused/ended)
 * @param {Object} params.metadata - 元数据
 * @returns {Promise}
 */
export function updateInterviewStatus(params) {
  return request.post('/interview/session/status', params)
}

/**
 * 收藏面试问题
 * @param {Object} params - 收藏参数
 * @param {string} params.session_id - 面试会话ID
 * @param {string} params.question_id - 问题ID
 * @param {string} params.question_text - 问题文本
 * @param {number} params.timestamp - 时间戳
 * @returns {Promise}
 */
export function favoriteQuestion(params) {
  return request.post('/interview/question/favorite', params)
}

/**
 * 获取用户收藏的问题列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @returns {Promise}
 */
export function getFavoriteQuestions(params) {
  return request.get('/interview/question/favorites', { params })
}

// ==================== 面试历史记录接口 ====================

/**
 * 获取面试历史列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.limit - 每页数量
 * @param {string} params.position - 岗位筛选 (可选)
 * @param {string} params.mode - 模式筛选 (可选)
 * @returns {Promise}
 */
export function getInterviewHistory(params) {
  return request.get('/interview/history', { params })
}

/**
 * 获取面试详细报告
 * @param {string} sessionId - 面试会话ID
 * @returns {Promise}
 */
export function getInterviewReport(sessionId) {
  return request.get(`/interview/report/${sessionId}`)
}

/**
 * 删除面试记录
 * @param {string} sessionId - 面试会话ID
 * @returns {Promise}
 */
export function deleteInterviewRecord(sessionId) {
  return request.delete(`/interview/record/${sessionId}`)
}

// ==================== 实时语音转写接口 ====================

/**
 * 启动实时语音转写
 * @param {Object} params - 转写参数
 * @param {string} params.mode - 面试模式
 * @param {string} params.position - 岗位类型
 * @param {string} params.difficulty - 难度级别
 * @returns {Promise}
 */
export function startRealTimeTranscription(params = {}) {
  const defaultParams = {
    mode: 'technical',
    position: 'ai-engineer',
    difficulty: 'primary',
    audio_format: 'pcm',
    sample_rate: 16000,
    encoding: 'raw'
  }
  
  return request.post('/interview/transcription/start', { ...defaultParams, ...params })
}

/**
 * 停止实时语音转写
 * @param {string} sessionId - 转写会话ID
 * @returns {Promise}
 */
export function stopRealTimeTranscription(sessionId) {
  return request.post('/interview/transcription/stop', { session_id: sessionId })
}

/**
 * 发送音频数据进行转写
 * @param {Object} params - 音频数据参数
 * @param {string} params.session_id - 转写会话ID
 * @param {ArrayBuffer} params.audio_data - 音频数据
 * @param {boolean} params.is_final - 是否为最后一段音频
 * @returns {Promise}
 */
export function sendAudioData(params) {
  return request.post('/interview/transcription/audio', params)
}

/**
 * 获取转写结果
 * @param {string} sessionId - 转写会话ID
 * @returns {Promise}
 */
export function getTranscriptionResult(sessionId) {
  return request.get(`/interview/transcription/result/${sessionId}`)
}

/**
 * 获取AI智能回复
 * @param {Object} params - 回复参数
 * @param {string} params.question - 面试问题
 * @param {string} params.userAnswer - 用户回答
 * @param {string} params.mode - 面试模式
 * @param {string} params.position - 岗位类型
 * @returns {Promise}
 */
export function getInterviewAIResponse(params) {
  return request.post('/interview/ai/response', params)
}

/**
 * 实时语音转写WebSocket连接管理
 */
export class RealTimeTranscriptionManager {
  constructor() {
    this.websocket = null
    this.sessionId = null
    this.isConnected = false
    this.onResultCallback = null
    this.onErrorCallback = null
  }

  /**
   * 连接实时转写WebSocket
   * @param {Object} config - 连接配置
   * @param {Function} onResult - 结果回调函数
   * @param {Function} onError - 错误回调函数
   * @returns {Promise}
   */
  async connect(config = {}, onResult = null, onError = null) {
    try {
      this.onResultCallback = onResult
      this.onErrorCallback = onError

      // 首先获取WebSocket连接参数
      const response = await startRealTimeTranscription(config)
      
      if (!response.success) {
        throw new Error(response.error || 'Failed to start transcription')
      }

      this.sessionId = response.session_id
      const wsUrl = response.websocket_url

      // 建立WebSocket连接
      this.websocket = new WebSocket(wsUrl)

      return new Promise((resolve, reject) => {
        this.websocket.onopen = () => {
          console.log('实时转写WebSocket连接成功')
          this.isConnected = true
          resolve(true)
        }

        this.websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            if (data.action === 'result' && this.onResultCallback) {
              this.onResultCallback(data.data)
            } else if (data.action === 'error' && this.onErrorCallback) {
              this.onErrorCallback(data.error)
            }
          } catch (error) {
            console.error('WebSocket消息解析失败:', error)
          }
        }

        this.websocket.onerror = (error) => {
          console.error('WebSocket连接错误:', error)
          this.isConnected = false
          if (this.onErrorCallback) {
            this.onErrorCallback('WebSocket连接错误')
          }
          reject(error)
        }

        this.websocket.onclose = () => {
          console.log('WebSocket连接关闭')
          this.isConnected = false
        }
      })
    } catch (error) {
      console.error('启动实时转写失败:', error)
      if (this.onErrorCallback) {
        this.onErrorCallback(error.message)
      }
      throw error
    }
  }

  /**
   * 发送音频数据
   * @param {ArrayBuffer} audioData - 音频数据
   */
  sendAudioData(audioData) {
    if (this.websocket && this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(audioData)
    } else {
      console.warn('WebSocket未连接，无法发送音频数据')
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.websocket) {
      this.websocket.close()
      this.websocket = null
    }
    this.isConnected = false
    this.sessionId = null
  }
}

// ==================== 面试流程控制接口 ====================

/**
 * 获取下一题
 * @param {Object} params - 参数
 * @param {string} params.session_id - 会话ID
 * @param {string} params.answer - 当前题目的答案（可选）
 */
export const getNextQuestionNew = (params) => {
  return request({
    url: '/api/interview/next-question',
    method: 'post',
    data: params
  })
}

/**
 * 提交答案
 * @param {Object} params - 参数
 * @param {string} params.session_id - 会话ID
 * @param {string} params.answer - 答案内容
 */
export const submitAnswerNew = (params) => {
  return request({
    url: '/api/interview/submit-answer',
    method: 'post',
    data: params
  })
}

/**
 * 结束面试
 * @param {Object} params - 参数
 * @param {string} params.session_id - 会话ID
 */
export const endInterviewNew = (params) => {
  return request({
    url: '/api/interview/end',
    method: 'post',
    data: params
  })
}

export default {
  // 面试设置
  updateInterviewMode,
  updateInterviewDifficulty,
  updateInterviewerExpression,
  updateInterviewPosition,
  // 录制控制
  startRecording,
  toggleRecording,
  stopRecording,
  getRecordingStatus,
  // 状态管理
  getInterviewSession,
  updateInterviewStatus,
  favoriteQuestion,
  getFavoriteQuestions,
  // 历史记录
  getInterviewHistory,
  getInterviewReport,
  deleteInterviewRecord,
  // 实时语音转写
  startRealTimeTranscription,
  stopRealTimeTranscription,
  sendAudioData,
  getTranscriptionResult,
  getInterviewAIResponse,
  RealTimeTranscriptionManager,

  // 新增的面试流程API
  getNextQuestionNew,
  submitAnswerNew,
  endInterviewNew
}

