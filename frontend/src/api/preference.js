import request from '@/utils/request'

// ==================== 面试偏好设置 ====================

/**
 * 获取面试偏好设置
 */
export const getInterviewPreferences = () => {
  return request({
    url: '/api/preferences/interview',
    method: 'get'
  })
}

/**
 * 更新面试偏好设置
 * @param {Object} preferences - 面试偏好设置
 * @param {Object} preferences.avatar_config - 虚拟面试官形象配置
 * @param {Object} preferences.interaction_config - 互动模式配置
 * @param {Object} preferences.expression_config - 微表情反馈配置
 * @param {Object} preferences.voice_config - 语音特性配置
 * @param {Object} preferences.recording_config - 回放与记录配置
 * @param {Object} preferences.noise_config - 噪音干扰配置
 * @param {Object} preferences.advanced_config - 高级配置
 * @param {Object} preferences.metadata - 元数据
 */
export const updateInterviewPreferences = (preferences) => {
  return request({
    url: '/api/preferences/interview',
    method: 'put',
    data: preferences
  })
}

/**
 * 测试语音播放
 * @param {Object} params - 测试参数
 * @param {number} params.voice_speed - 语音速度
 * @param {string} params.test_text - 测试文本
 */
export const testVoicePreview = (params) => {
  return request({
    url: '/api/preferences/interview/test-voice',
    method: 'post',
    data: params
  })
}

// ==================== 求职偏好设置 ====================

/**
 * 获取求职偏好设置
 */
export const getJobPreferences = () => {
  return request({
    url: '/api/preferences/job',
    method: 'get'
  })
}

/**
 * 更新求职偏好设置
 * @param {Object} preferences - 求职偏好设置
 * @param {string} preferences.selected_field - 目标领域
 * @param {Array} preferences.selected_directions - 岗位方向
 * @param {Array} preferences.selected_companies - 目标企业
 * @param {string} preferences.selected_city - 工作城市
 * @param {string} preferences.selected_company_size - 公司规模
 * @param {string} preferences.selected_experience - 工作经验
 */
export const updateJobPreferences = (preferences) => {
  return request({
    url: '/api/preferences/job',
    method: 'put',
    data: preferences
  })
}

// ==================== 隐私设置 ====================

/**
 * 获取隐私设置
 */
export const getPrivacySettings = () => {
  return request({
    url: '/api/preferences/privacy',
    method: 'get'
  })
}

/**
 * 更新隐私设置
 * @param {Object} settings - 隐私设置
 * @param {boolean} settings.data_sharing - 数据共享
 * @param {string} settings.resume_visibility - 简历可见性
 * @param {boolean} settings.allow_recommendations - 允许推荐
 * @param {boolean} settings.show_online_status - 显示在线状态
 */
export const updatePrivacySettings = (settings) => {
  return request({
    url: '/api/preferences/privacy',
    method: 'put',
    data: settings
  })
}

// ==================== 数据管理 ====================

/**
 * 清除用户数据
 * @param {Array} clearTypes - 清除类型
 */
export const clearUserData = (clearTypes) => {
  return request({
    url: '/api/preferences/clear-data',
    method: 'post',
    data: { clear_types: clearTypes }
  })
}

/**
 * 注销账户
 * @param {Object} data - 注销数据
 * @param {string} data.cancel_reason - 注销原因
 * @param {boolean} data.confirm_delete - 确认删除
 */
export const deleteAccount = (data) => {
  return request({
    url: '/api/preferences/account/delete',
    method: 'post',
    data
  })
}

// ==================== 通用偏好管理 ====================

/**
 * 获取所有偏好设置
 */
export const getAllPreferences = () => {
  return request({
    url: '/api/preferences/all',
    method: 'get'
  })
}

/**
 * 重置偏好设置
 * @param {Array} resetTypes - 重置类型
 */
export const resetPreferences = (resetTypes = ['all']) => {
  return request({
    url: '/api/preferences/reset',
    method: 'post',
    data: { reset_types: resetTypes }
  })
}

// API对象形式（保持兼容性）
export const preferenceApi = {
  // 面试偏好
  getInterviewPreferences,
  updateInterviewPreferences,
  testVoicePreview,

  // 求职偏好
  getJobPreferences,
  updateJobPreferences,

  // 隐私设置
  getPrivacySettings,
  updatePrivacySettings,

  // 数据管理
  clearUserData,
  deleteAccount,

  // 通用管理
  getAllPreferences,
  resetPreferences
}