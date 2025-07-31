import request from '@/utils/request'

/**
 * 简历管理API模块
 * 包含简历管理和AI分析功能，与后端resume_controller.py对应
 */

// ==================== 简历基本操作 ====================

/**
 * 上传简历 - 与后端resume_controller.py对应
 */
export function uploadResume(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post('/api/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
        onProgress(percentCompleted)
      }
    }
  })
}

/**
 * 处理简历 - 与后端resume_controller.py对应
 */
export function processResume(resumeId, processParams) {
  return request.post(`/api/resume/process/${resumeId}`, processParams)
}

/**
 * 获取简历列表 - 与后端resume_controller.py对应
 */
export function getResumeList(params) {
  return request.get('/api/resume/list', { params })
}

/**
 * 获取简历详情 - 与后端resume_controller.py对应
 */
export function getResumeDetail(resumeId) {
  return request.get(`/api/resume/${resumeId}`)
}

/**
 * 更新简历 - 与后端resume_controller.py对应
 */
export function updateResume(resumeId, resumeData) {
  return request.put(`/api/resume/${resumeId}`, resumeData)
}

/**
 * 删除简历 - 与后端resume_controller.py对应
 */
export function deleteResume(resumeId) {
  return request.delete(`/api/resume/${resumeId}`)
}

/**
 * 分析简历 - 与后端resume_controller.py对应
 */
export function analyzeResume(resumeId, analysisParams) {
  return request.post(`/api/resume/${resumeId}/analyze`, analysisParams)
}

/**
 * 获取简历技能 - 与后端resume_controller.py对应
 */
export function getResumeSkills(resumeId) {
  return request.get(`/api/resume/${resumeId}/skills`)
}

/**
 * 获取简历状态 - 与后端resume_controller.py对应
 */
export function getResumeStatus(resumeId) {
  return request.get(`/api/resume/status/${resumeId}`)
}

// ==================== 简历AI分析服务 ====================

/**
 * OCR文档识别 - 从xunfei.js整合
 */
export function ocrRecognize(params) {
  return request.post('/api/resume/ocr/recognize', params)
}

/**
 * 文本提取 (pdfplumber + OCR双重策略) - 从xunfei.js整合
 */
export function extractText(params) {
  return request.post('/api/resume/text/extract', params)
}

/**
 * 简历内容分析 - 使用AI模型分析简历内容
 */
export function analyzeResumeContent(params) {
  return request.post('/api/resume/content/analyze', params)
}

/**
 * 简历技能提取 - 使用AI提取简历中的技能
 */
export function extractResumeSkills(params) {
  return request.post('/api/resume/skills/extract', params)
}

/**
 * 简历匹配分析 - 分析简历与岗位的匹配度
 */
export function matchResumeWithPosition(params) {
  return request.post('/api/resume/match/position', params)
}

/**
 * 简历优化建议 - 提供简历优化建议
 */
export function getResumeOptimization(params) {
  return request.post('/api/resume/optimization/suggest', params)
}

// ==================== 简历便捷操作 ====================

/**
 * 上传文件并进行OCR识别
 */
export function uploadAndOCR(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = function(e) {
      const base64Data = e.target.result
      ocrRecognize({
        image_data: base64Data,
        output_format: 'json'
      }).then(resolve).catch(reject)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * 解析简历内容（使用AI分析）- 兼容旧版本
 */
export function parseResume(fileUrl) {
  return request.post('/api/resume/parse', {
    fileUrl: fileUrl
  })
}

/**
 * 重新解析简历 - 兼容旧版本
 */
export function reparseResume(resumeId) {
  return request.post(`/api/resume/${resumeId}/reparse`)
}

/**
 * 获取文件预览URL
 */
export function getPreviewUrl(resumeId) {
  return request.get(`/api/resume/${resumeId}/preview`)
}

/**
 * 删除简历文件 - 兼容旧版本
 */
export function deleteResumeFile(resumeId) {
  return deleteResume(resumeId)
}

// ==================== 简历评估和报告 ====================

/**
 * 获取简历评估报告
 */
export function getResumeEvaluation(resumeId) {
  return request.get(`/api/resume/${resumeId}/evaluation`)
}

/**
 * 导出简历分析报告
 */
export function exportResumeReport(resumeId, format = 'pdf') {
  return request.get(`/api/resume/${resumeId}/export`, {
    params: { format },
    responseType: 'blob'
  })
}

/**
 * 获取简历统计数据
 */
export function getResumeStats(params) {
  return request.get('/api/resume/stats', { params })
}

export default {
  // 基本操作
  uploadResume,
  processResume,
  getResumeList,
  getResumeDetail,
  updateResume,
  deleteResume,
  analyzeResume,
  getResumeSkills,
  getResumeStatus,
  
  // AI分析服务
  ocrRecognize,
  extractText,
  analyzeResumeContent,
  extractResumeSkills,
  matchResumeWithPosition,
  getResumeOptimization,
  
  // 便捷操作
  uploadAndOCR,
  parseResume,
  reparseResume,
  getPreviewUrl,
  deleteResumeFile,
  
  // 评估和报告
  getResumeEvaluation,
  exportResumeReport,
  getResumeStats
} 