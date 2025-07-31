import request from '@/utils/request'

/**
 * 用户资料管理API模块
 * 与后端profile_controller.py对应，包括个人信息、教育背景、技能管理等功能
 */

// ==================== 个人信息管理 ====================

/**
 * 获取个人信息
 * @returns {Promise} 个人信息
 */
export const getPersonalInfo = () => {
  return request({
    url: '/api/profile/personal-info',
    method: 'get'
  })
}

/**
 * 更新个人信息
 * @param {Object} personalInfo - 个人信息
 * @param {string} personalInfo.name - 姓名
 * @param {string} personalInfo.gender - 性别
 * @param {string} personalInfo.birth_date - 出生日期
 * @param {string} personalInfo.phone - 电话
 * @param {string} personalInfo.email - 邮箱
 * @param {string} personalInfo.contact - 微信/QQ
 * @returns {Promise} 更新结果
 */
export const updatePersonalInfo = (personalInfo) => {
  return request({
    url: '/api/profile/personal-info',
    method: 'put',
    data: personalInfo
  })
}

/**
 * 上传头像
 * @param {File} file - 头像文件
 * @returns {Promise} 上传结果
 */
export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('avatar', file)
  
  return request({
    url: '/api/profile/avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ==================== 账户设置 ====================
// 注意：账户设置相关的API已移至 auth.js 中

// ==================== 求职偏好 ====================

/**
 * 获取求职偏好
 * @returns {Promise} 求职偏好
 */
export function getJobPreferences() {
  return request.get('/profile/job-preferences')
}

/**
 * 更新求职偏好
 * @param {Object} data - 求职偏好数据
 * @param {Array} data.positions - 期望职位
 * @param {Array} data.industries - 期望行业
 * @param {Array} data.locations - 期望工作地点
 * @param {Object} data.salary - 薪资期望
 * @param {string} data.workType - 工作类型 fulltime/parttime/remote
 * @param {Array} data.skills - 技能标签
 * @returns {Promise} 更新结果
 */
export function updateJobPreferences(data) {
  return request.put('/profile/job-preferences', data)
}

// ==================== 技能管理 ====================

/**
 * 获取技能列表
 * @returns {Promise} 技能列表
 */
export const getSkills = () => {
  return request({
    url: '/api/profile/skills',
    method: 'get'
  })
}

/**
 * 更新技能列表
 * @param {Array} skills - 技能列表
 * @param {string} skills[].name - 技能名称
 * @param {string} skills[].level - 熟练程度
 * @param {string} skills[].category - 技能分类
 * @returns {Promise} 更新结果
 */
export const updateSkills = (skills) => {
  return request({
    url: '/api/profile/skills',
    method: 'put',
    data: { skills }
  })
}

/**
 * 添加技能
 * @param {Object} data - 技能数据
 * @param {string} data.name - 技能名称
 * @param {string} data.level - 技能水平 beginner/intermediate/advanced/expert
 * @param {string} data.category - 技能分类
 * @param {number} data.experience - 经验年限
 * @returns {Promise} 添加结果
 */
export function addSkill(data) {
  return request.post('/profile/skills', data)
}

/**
 * 更新技能
 * @param {string} skillId - 技能ID
 * @param {Object} data - 技能数据
 * @returns {Promise} 更新结果
 */
export function updateSkill(skillId, data) {
  return request.put(`/profile/skills/${skillId}`, data)
}

/**
 * 删除技能
 * @param {string} skillId - 技能ID
 * @returns {Promise} 删除结果
 */
export function deleteSkill(skillId) {
  return request.delete(`/profile/skills/${skillId}`)
}

// ==================== 工作经历 ====================

/**
 * 获取工作经历
 * @returns {Promise} 工作经历列表
 */
export function getWorkExperience() {
  return request.get('/profile/work-experience')
}

/**
 * 添加工作经历
 * @param {Object} data - 工作经历数据
 * @param {string} data.company - 公司名称
 * @param {string} data.position - 职位
 * @param {string} data.startDate - 开始日期
 * @param {string} data.endDate - 结束日期
 * @param {string} data.description - 工作描述
 * @param {Array} data.achievements - 主要成就
 * @returns {Promise} 添加结果
 */
export function addWorkExperience(data) {
  return request.post('/profile/work-experience', data)
}

/**
 * 更新工作经历
 * @param {string} experienceId - 经历ID
 * @param {Object} data - 工作经历数据
 * @returns {Promise} 更新结果
 */
export function updateWorkExperience(experienceId, data) {
  return request.put(`/profile/work-experience/${experienceId}`, data)
}

/**
 * 删除工作经历
 * @param {string} experienceId - 经历ID
 * @returns {Promise} 删除结果
 */
export function deleteWorkExperience(experienceId) {
  return request.delete(`/profile/work-experience/${experienceId}`)
}

// ==================== 教育背景 ====================

/**
 * 获取教育背景
 * @returns {Promise} 教育背景列表
 */
export const getEducationInfo = () => {
  return request({
    url: '/api/profile/education',
    method: 'get'
  })
}

/**
 * 更新教育背景
 * @param {Object} educationInfo - 教育背景
 * @param {string} educationInfo.school - 学校
 * @param {string} educationInfo.college - 学院
 * @param {string} educationInfo.major - 专业
 * @param {string} educationInfo.degree - 学历
 * @param {string} educationInfo.start_date - 入学时间
 * @param {string} educationInfo.end_date - 毕业时间
 * @param {string} educationInfo.description - 描述
 * @returns {Promise} 更新结果
 */
export const updateEducationInfo = (educationInfo) => {
  return request({
    url: '/api/profile/education',
    method: 'put',
    data: educationInfo
  })
}

/**
 * 删除教育背景
 * @param {string} educationId - 教育背景ID
 * @returns {Promise} 删除结果
 */
export function deleteEducation(educationId) {
  return request.delete(`/profile/education/${educationId}`)
}

// ==================== 项目经历 ====================

/**
 * 获取项目经历
 * @returns {Promise} 项目经历列表
 */
export function getProjects() {
  return request.get('/profile/projects')
}

/**
 * 添加项目经历
 * @param {Object} data - 项目经历数据
 * @param {string} data.name - 项目名称
 * @param {string} data.description - 项目描述
 * @param {string} data.role - 担任角色
 * @param {string} data.startDate - 开始日期
 * @param {string} data.endDate - 结束日期
 * @param {Array} data.technologies - 使用技术
 * @param {string} data.url - 项目链接
 * @param {Array} data.achievements - 项目成果
 * @returns {Promise} 添加结果
 */
export function addProject(data) {
  return request.post('/profile/projects', data)
}

/**
 * 更新项目经历
 * @param {string} projectId - 项目ID
 * @param {Object} data - 项目经历数据
 * @returns {Promise} 更新结果
 */
export function updateProject(projectId, data) {
  return request.put(`/profile/projects/${projectId}`, data)
}

/**
 * 删除项目经历
 * @param {string} projectId - 项目ID
 * @returns {Promise} 删除结果
 */
export function deleteProject(projectId) {
  return request.delete(`/profile/projects/${projectId}`)
}

// ==================== 证书和认证 ====================

/**
 * 获取证书列表
 * @returns {Promise} 证书列表
 */
export function getCertifications() {
  return request.get('/profile/certifications')
}

/**
 * 添加证书
 * @param {Object} data - 证书数据
 * @param {string} data.name - 证书名称
 * @param {string} data.issuer - 颁发机构
 * @param {string} data.issueDate - 颁发日期
 * @param {string} data.expiryDate - 过期日期
 * @param {string} data.credentialId - 证书ID
 * @param {string} data.url - 证书链接
 * @returns {Promise} 添加结果
 */
export function addCertification(data) {
  return request.post('/profile/certifications', data)
}

/**
 * 更新证书
 * @param {string} certId - 证书ID
 * @param {Object} data - 证书数据
 * @returns {Promise} 更新结果
 */
export function updateCertification(certId, data) {
  return request.put(`/profile/certifications/${certId}`, data)
}

/**
 * 删除证书
 * @param {string} certId - 证书ID
 * @returns {Promise} 删除结果
 */
export function deleteCertification(certId) {
  return request.delete(`/profile/certifications/${certId}`)
}

// ==================== 语言能力 ====================

/**
 * 获取语言能力
 * @returns {Promise} 语言能力列表
 */
export function getLanguages() {
  return request.get('/profile/languages')
}

/**
 * 添加语言能力
 * @param {Object} data - 语言能力数据
 * @param {string} data.language - 语言名称
 * @param {string} data.level - 水平 native/fluent/conversational/basic
 * @param {Array} data.skills - 技能 speaking/listening/reading/writing
 * @param {string} data.certificate - 证书
 * @returns {Promise} 添加结果
 */
export function addLanguage(data) {
  return request.post('/profile/languages', data)
}

/**
 * 更新语言能力
 * @param {string} languageId - 语言ID
 * @param {Object} data - 语言能力数据
 * @returns {Promise} 更新结果
 */
export function updateLanguage(languageId, data) {
  return request.put(`/profile/languages/${languageId}`, data)
}

/**
 * 删除语言能力
 * @param {string} languageId - 语言ID
 * @returns {Promise} 删除结果
 */
export function deleteLanguage(languageId) {
  return request.delete(`/profile/languages/${languageId}`)
}

// ==================== 个人作品集 ====================

/**
 * 获取作品集
 * @returns {Promise} 作品集列表
 */
export function getPortfolio() {
  return request.get('/profile/portfolio')
}

/**
 * 添加作品
 * @param {Object} data - 作品数据
 * @param {string} data.title - 作品标题
 * @param {string} data.description - 作品描述
 * @param {string} data.category - 作品分类
 * @param {Array} data.images - 作品图片
 * @param {string} data.url - 作品链接
 * @param {Array} data.tags - 标签
 * @returns {Promise} 添加结果
 */
export function addPortfolioItem(data) {
  return request.post('/profile/portfolio', data)
}

/**
 * 更新作品
 * @param {string} itemId - 作品ID
 * @param {Object} data - 作品数据
 * @returns {Promise} 更新结果
 */
export function updatePortfolioItem(itemId, data) {
  return request.put(`/profile/portfolio/${itemId}`, data)
}

/**
 * 删除作品
 * @param {string} itemId - 作品ID
 * @returns {Promise} 删除结果
 */
export function deletePortfolioItem(itemId) {
  return request.delete(`/profile/portfolio/${itemId}`)
}

/**
 * 获取用户资料概要
 */
export const getProfileSummary = () => {
  return request({
    url: '/api/profile/summary',
    method: 'get'
  })
}

// API对象形式（保持兼容性）
export const profileApi = {
  getPersonalInfo,
  updatePersonalInfo,
  getEducationInfo,
  updateEducationInfo,
  getSkills,
  updateSkills,
  uploadAvatar,
  getProfileSummary
} 