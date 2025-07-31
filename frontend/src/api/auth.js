import request from '@/utils/request'

/**
 * 认证和账户管理API
 */

// ==================== 用户认证 ====================

/**
 * 用户登录
 * @param {Object} credentials - 登录凭据
 * @param {string} credentials.username - 用户名或邮箱
 * @param {string} credentials.password - 密码
 */
export function login(credentials) {
  return request.post('/api/auth/login', credentials)
}

/**
 * 用户注册
 * @param {Object} userData - 用户数据
 * @param {string} userData.username - 用户名
 * @param {string} userData.email - 邮箱
 * @param {string} userData.password - 密码
 * @param {string} userData.phone - 手机号（可选）
 */
export function register(userInfo) {
  return request.post('/api/auth/register', userInfo)
}

/**
 * 用户登出
 */
export function logout() {
  return request.post('/api/auth/logout')
}

/**
 * 刷新token
 */
export function refreshToken() {
  return request.post('/api/auth/refresh-token')
}

/**
 * 验证token
 */
export function verifyToken() {
  return request.post('/api/auth/verify-token')
}

// ==================== 账户安全设置 ====================

/**
 * 修改密码
 * @param {Object} passwordData - 密码数据
 * @param {string} passwordData.current_password - 当前密码
 * @param {string} passwordData.new_password - 新密码
 */
export function changePassword(passwordData) {
  return request.post('/api/auth/change-password', passwordData)
}

/**
 * 更换手机号
 */
export function changePhone(phoneData) {
  return request.post('/api/auth/change-phone', phoneData)
}

/**
 * 获取登录历史
 */
export function getLoginHistory() {
  return request.get('/api/auth/login-history')
}

/**
 * 刷新登录历史
 */
export function refreshLoginHistory() {
  return request.post('/api/auth/refresh-login-history')
}

// ==================== 隐私设置 ====================

/**
 * 获取隐私设置
 */
export function getPrivacySettings() {
  return request.get('/api/preferences/privacy')
}

/**
 * 更新隐私设置
 */
export function updatePrivacySettings(privacyData) {
  return request.put('/api/preferences/privacy', privacyData)
}

/**
 * 设置简历可见范围
 */
export function setResumeVisibility(visibilityData) {
  return request.post('/api/auth/set-resume-visibility', {
    visibility: visibilityData.visibility
  })
}

/**
 * 清除用户痕迹数据
 */
export function clearUserData(clearTypes) {
  return request.post('/api/preferences/clear-data', {
    clear_types: clearTypes
  })
}

// ==================== 账户注销 ====================

/**
 * 注销账户
 */
export function deleteAccount(deleteData) {
  return request.post('/api/preferences/account/delete', {
    cancel_reason: deleteData.reason,
    confirm_delete: deleteData.confirm
  })
}

// ==================== 账户信息 ====================

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request.get('/api/auth/me')
}

/**
 * 更新用户基本信息
 */
export function updateUserInfo(userInfo) {
  return request.put('/api/auth/me', userInfo)
}

/**
 * 获取用户权限
 */
export function getUserPermissions() {
  return request.get('/api/auth/permissions')
}

/**
 * 检查用户状态
 */
export function checkUserStatus() {
  return request.get('/api/auth/status')
}

// ==================== 双因素认证 ====================

/**
 * 启用双因素认证
 */
export function enableTwoFactor() {
  return request.post('/api/auth/2fa/enable')
}

/**
 * 禁用双因素认证
 */
export function disableTwoFactor() {
  return request.post('/api/auth/2fa/disable')
}

/**
 * 验证双因素认证代码
 */
export function verifyTwoFactor(code) {
  return request.post('/api/auth/2fa/verify', { code })
}

export default {
  login,
  register,
  logout,
  refreshToken,
  verifyToken,
  changePassword,
  changePhone,
  getLoginHistory,
  refreshLoginHistory,
  getPrivacySettings,
  updatePrivacySettings,
  setResumeVisibility,
  clearUserData,
  deleteAccount,
  getCurrentUser,
  updateUserInfo,
  getUserPermissions,
  checkUserStatus,
  enableTwoFactor,
  disableTwoFactor,
  verifyTwoFactor
} 