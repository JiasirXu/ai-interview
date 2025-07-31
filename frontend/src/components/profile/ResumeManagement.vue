<template>
  <div class="resume-management">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <span class="breadcrumb-item">个人中心</span>
      <span class="breadcrumb-divider">></span>
      <span class="breadcrumb-item active">简历管理</span>
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-section">
      <div 
        class="upload-area"
        :class="{ 'dragging': isDragging, 'uploading': uploading }"
        @drop="handleDrop"
        @dragover.prevent="handleDragOver"
        @dragenter.prevent="handleDragEnter"
        @dragleave.prevent="handleDragLeave"
        @click="openFileDialog"
      >
        <div class="upload-content" v-if="!uploading">
          <div class="upload-icon">
            <SvgIcon name="resume-upload" />
          </div>
          <p class="upload-text">点击或拖拽上传简历文件</p>
          <p class="upload-hint">支持 PDF、Word 格式，文件大小 ≤10MB</p>
        </div>
        
        <!-- 上传进度 -->
        <div class="upload-progress" v-if="uploading">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p class="progress-text">上传中... {{ uploadProgress }}%</p>
        </div>
        
        <input 
          ref="fileInput"
          type="file" 
          accept=".pdf,.doc,.docx"
          @change="handleFileSelect"
          style="display: none"
        />
      </div>
      
      <!-- 错误提示 -->
      <div class="error-messages" v-if="errors.upload">
        <div class="error-item" v-for="error in errors.upload" :key="error">
          {{ error }}
        </div>
      </div>
    </div>

    <!-- 已上传简历 -->
    <div class="resume-section">
      <h3 class="section-title">已上传简历</h3>
      
      <div class="resume-table" v-if="resumeList.length > 0">
        <div class="table-header">
          <div class="col-name">简历名称</div>
          <div class="col-time">上传时间</div>
          <div class="col-size">文件大小</div>
          <div class="col-status">解析状态</div>
          <div class="col-actions">操作</div>
        </div>
        
        <div class="table-body">
          <div class="table-row" v-for="resume in resumeList" :key="resume.id">
            <div class="col-name">
              <SvgIcon :name="getFileIcon(resume.type)" class="file-icon" />
              <span>{{ resume.name }}</span>
            </div>
            <div class="col-time">{{ formatDate(resume.uploadTime) }}</div>
            <div class="col-size">{{ resume.size }}</div>
            <div class="col-status">
              <span class="status-badge" :class="resume.status">
                {{ getStatusText(resume.status) }}
              </span>
              <button 
                v-if="resume.status === 'failed'" 
                class="retry-btn"
                @click="retryParse(resume)"
                title="重新解析"
              >
                重试
              </button>
            </div>
            <div class="col-actions">
              <button 
                class="action-btn view-btn" 
                @click="viewResume(resume)" 
                :disabled="resume.status === 'parsing'"
                title="查看"
              >
                <SvgIcon name="view" />
              </button>
              <button 
                class="action-btn delete-btn" 
                @click="deleteResume(resume)" 
                title="删除"
              >
                <SvgIcon name="delete" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else>
        <p>暂无上传的简历文件</p>
      </div>
    </div>

    <!-- 已识别技能 -->
    <div class="skills-section" v-if="extractedSkills.length > 0">
      <h3 class="section-title">已识别技能</h3>
      <div class="skills-tags">
        <span 
          class="skill-tag" 
          v-for="skill in extractedSkills" 
          :key="skill"
        >
          {{ skill }}
        </span>
      </div>
    </div>

    <!-- 项目经历 -->
    <div class="projects-section" v-if="projectExperience.length > 0">
      <h3 class="section-title">实践经历</h3>
      <div class="projects-list">
        <div class="project-item" v-for="project in projectExperience" :key="project.id">
          <div class="project-header">
            <h4 class="project-title">{{ project.title }}</h4>
            <span class="project-period">{{ project.period }}</span>
          </div>
          <p class="project-description">{{ project.description }}</p>
        </div>
      </div>
    </div>



    <!-- 文件预览模态框 -->
    <div class="modal-overlay" v-if="previewFile" @click="closePreview" @keydown.esc="closePreview">
      <div class="modal-content preview-modal" @click.stop>
        <!-- 最小化的控制栏 -->
        <div class="preview-controls">
          <div class="preview-title">
            <span>{{ previewFile.type.toUpperCase() }}预览</span>
          </div>
          <button class="close-btn" @click="closePreview">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        
        <div class="preview-body">
          <!-- PDF预览 -->
          <iframe 
            v-if="previewFile.type === 'pdf'"
            :src="getPDFPreviewUrl(previewFile.url)"
            class="pdf-preview"
            frameborder="0"
          ></iframe>
          
          <!-- Word预览 (使用Office在线预览) -->
          <iframe 
            v-else-if="previewFile.type === 'docx' || previewFile.type === 'doc'"
            :src="getOfficePreviewUrl(previewFile.url)"
            class="office-preview"
            frameborder="0"
          ></iframe>
          
          <!-- 加载中 -->
          <div v-else class="preview-loading">
            <div class="loading-spinner"></div>
            <p>文件预览加载中...</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 解析进度提示 -->
    <div class="parsing-toast" v-if="showParsingToast">
      <SvgIcon name="loading" class="loading-icon" />
      <span>正在使用讯飞AI解析简历内容...</span>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import SvgIcon from '@/components/common/SvgIcon.vue'
import * as resumeApi from '@/api/resume'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ResumeManagement',
  components: {
    SvgIcon
  },
  setup() {
    const isDragging = ref(false)
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const fileInput = ref(null)
    const previewFile = ref(null)
    const showParsingToast = ref(false)
    
    const resumeList = ref([])
    const extractedSkills = ref([])
    const projectExperience = ref([])
    const errors = reactive({})
    
    // 支持的文件类型
    const allowedTypes = {
      'application/pdf': { ext: 'pdf', maxSize: 10 * 1024 * 1024 },
      'application/msword': { ext: 'doc', maxSize: 10 * 1024 * 1024 },
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { ext: 'docx', maxSize: 10 * 1024 * 1024 }
    }
    
    // 文件验证
    const validateFile = (file) => {
      const errors = []
      
      if (!allowedTypes[file.type]) {
        errors.push('不支持的文件格式，仅支持：PDF、Word')
        return errors
      }
      
      const typeConfig = allowedTypes[file.type]
      if (file.size > typeConfig.maxSize) {
        const maxSizeMB = typeConfig.maxSize / (1024 * 1024)
        errors.push(`文件大小不能超过${maxSizeMB}MB`)
      }
      
      if (file.name.length > 100) {
        errors.push('文件名不能超过100个字符')
      }
      
      const existingFile = resumeList.value.find(resume => resume.name === file.name)
      if (existingFile) {
        errors.push('已存在同名文件，请重命名后上传')
      }
      
      if (resumeList.value.length >= 10) {
        errors.push('最多只能上传10份简历')
      }
      
      return errors
    }
    
    // 文件处理事件
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      if (files.length > 0) {
        uploadFiles(files)
      }
    }
    
    const handleDrop = (event) => {
      event.preventDefault()
      isDragging.value = false
      
      const files = Array.from(event.dataTransfer.files)
      if (files.length > 0) {
        uploadFiles(files)
      }
    }
    
    const handleDragOver = (event) => {
      event.preventDefault()
      isDragging.value = true
    }
    
    const handleDragEnter = (event) => {
      event.preventDefault()
      isDragging.value = true
    }
    
    const handleDragLeave = (event) => {
      event.preventDefault()
      if (event.target === event.currentTarget) {
        isDragging.value = false
      }
    }
    
    // 文件上传
    const uploadFiles = async (files) => {
      // 验证文件
      const validationErrors = []
      for (let file of files) {
        const fileErrors = validateFile(file)
        if (fileErrors.length > 0) {
          validationErrors.push(`文件 "${file.name}": ${fileErrors.join(', ')}`)
        }
      }
      
      if (validationErrors.length > 0) {
        errors.upload = validationErrors
        return
      }
      
      delete errors.upload
      uploading.value = true
      uploadProgress.value = 0
      
      try {
        for (let file of files) {
          await uploadSingleFile(file)
        }
        
        // 清空文件输入
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        
      } catch (error) {
        console.error('上传失败:', error)
        errors.upload = ['上传失败，请重试']
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }
    
    const uploadSingleFile = async (file) => {
      try {
        console.log('开始上传文件:', {
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified
        })
        
        // 检查用户认证状态
        const authStore = useAuthStore()
        console.log('用户认证状态:', {
          isAuthenticated: authStore.isAuthenticated,
          token: authStore.token ? authStore.token.substring(0, 20) + '...' : null
        })
        
        // 模拟上传进度
        const progressInterval = setInterval(() => {
          if (uploadProgress.value < 70) {
            uploadProgress.value += 10
          }
        }, 200)
        
        // 调用上传API
        console.log('调用uploadResume API...')
        const uploadResult = await resumeApi.uploadResume(file, (progress) => {
          uploadProgress.value = Math.min(70, progress)
        })
        
        console.log('上传API返回结果:', uploadResult)
        
        clearInterval(progressInterval)
        uploadProgress.value = 80
        
        // 检查上传结果
        if (!uploadResult.success) {
          throw new Error(uploadResult.message || '上传失败')
        }
        
        // 创建简历记录
        const resumeData = uploadResult.resume
        const newResume = {
          id: resumeData.id,
          name: resumeData.name,
          uploadTime: new Date(),
          size: formatFileSize(file.size),
          status: 'parsing',
          type: getFileExtension(file.name),
          url: `/uploads/${resumeData.id}`, // 临时URL，等待处理完成后更新
          skills: [],
          projects: []
        }
        
        resumeList.value.unshift(newResume)
        uploadProgress.value = 90
        
        // 处理简历（提取文本和AI分析）
        showParsingToast.value = true
        try {
          console.log('开始处理简历...')
          const processResult = await resumeApi.processResume(resumeData.id, {})
          console.log('处理结果:', processResult)
          
          if (processResult.success) {
            // 更新解析结果 - 使用后端返回的状态或设为parsed
            newResume.status = processResult.resume.status === 'completed' ? 'parsed' : processResult.resume.status
            newResume.skills = processResult.resume.skills || []
            newResume.projects = processResult.resume.projects || []
            
            // 更新为正确的文件URL
            if (processResult.resume.url) {
              newResume.url = processResult.resume.url
            }
            
            // 更新全局技能和项目列表
            updateGlobalSkillsAndProjects()
          } else {
            throw new Error(processResult.message || '解析失败')
          }
          
        } catch (parseError) {
          console.error('解析失败:', parseError)
          newResume.status = 'failed'
        } finally {
          showParsingToast.value = false
        }
        
        uploadProgress.value = 100
        
      } catch (error) {
        console.error('上传失败:', error)
        console.error('错误详情:', {
          name: error.name,
          message: error.message,
          stack: error.stack,
          response: error.response?.data
        })
        throw error
      }
    }
    
    // 更新全局技能和项目列表
    const updateGlobalSkillsAndProjects = () => {
      const allSkills = new Set()
      const allProjects = []
      
      resumeList.value.forEach(resume => {
        if (resume.status === 'parsed' || resume.status === 'completed') {
          resume.skills?.forEach(skill => allSkills.add(skill))
          resume.projects?.forEach(project => allProjects.push(project))
        }
      })
      
      extractedSkills.value = Array.from(allSkills)
      projectExperience.value = allProjects
    }
    
    // 简历操作
    const viewResume = (resume) => {
      if (resume.status === 'parsing') {
        return
      }
      
      previewFile.value = {
        name: resume.name,
        url: resume.url,
        type: resume.type
      }
    }
    
    const deleteResume = async (resume) => {
      if (!confirm(`确定要删除简历"${resume.name}"吗？`)) {
        return
      }
      
      try {
        await resumeApi.deleteResumeFile(resume.id)
        
        const index = resumeList.value.findIndex(r => r.id === resume.id)
        if (index > -1) {
          resumeList.value.splice(index, 1)
        }
        
        // 更新全局技能和项目列表
        updateGlobalSkillsAndProjects()
        
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败，请重试')
      }
    }
    
    const retryParse = async (resume) => {
      resume.status = 'parsing'
      showParsingToast.value = true
      
      try {
        const reparseResult = await resumeApi.reparseResume(resume.id)
        
        if (reparseResult.success) {
          resume.status = 'parsed'
          resume.skills = reparseResult.resume.skills || []
          resume.projects = reparseResult.resume.projects || []
          
          updateGlobalSkillsAndProjects()
        } else {
          throw new Error(reparseResult.message || '重新解析失败')
        }
        
      } catch (error) {
        console.error('重新解析失败:', error)
        resume.status = 'failed'
      } finally {
        showParsingToast.value = false
      }
    }
    
    // 工具方法
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
    }
    
    const getFileExtension = (filename) => {
      return filename.split('.').pop().toLowerCase()
    }
    
    const getFileIcon = (type) => {
      switch (type) {
        case 'pdf': return 'file-pdf'
        case 'doc':
        case 'docx': return 'file-word'
        default: return 'file'
      }
    }
    
    const getStatusText = (status) => {
      switch (status) {
        case 'parsing': return '解析中'
        case 'parsed': return '已解析'
        case 'failed': return '解析失败'
        default: return '未知状态'
      }
    }
    
    const formatDate = (date) => {
      if (typeof date === 'string') {
        return date
      }
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(/\//g, '-')
    }
    
    const openFileDialog = () => {
      if (!uploading.value) {
        fileInput.value.click()
      }
    }
    
    const closePreview = () => {
      previewFile.value = null
    }

    // PDF预览URL生成
    const getPDFPreviewUrl = (fileUrl) => {
      // 确保URL是完整的
      const fullUrl = fileUrl.startsWith('http') ? fileUrl : `http://localhost:5000${fileUrl}`
      // 添加PDF.js参数以获得更好的预览体验
      return `${fullUrl}#view=FitH&toolbar=1&navpanes=1&scrollbar=1`
    }

    // Office文档预览URL生成
    const getOfficePreviewUrl = (fileUrl) => {
      // 确保URL是完整的
      const fullUrl = fileUrl.startsWith('http') ? fileUrl : `http://localhost:5000${fileUrl}`
      return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fullUrl)}`
    }

    // 键盘事件监听器
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && previewFile.value) {
        closePreview()
      }
    }

    // 加载简历列表
    const loadResumeList = async () => {
      try {
        console.log('开始加载简历列表...')
        const result = await resumeApi.getResumeList()
        console.log('简历列表加载结果:', result)

        if (result.success && result.resumes) {
          resumeList.value = result.resumes.map(resume => ({
            id: resume.id,
            name: resume.name || resume.original_filename,
            uploadTime: new Date(resume.created_at),
            size: formatFileSize(resume.file_size),
            status: resume.status === 'completed' ? 'parsed' : resume.status,
            type: resume.file_type,
            url: resume.url,
            skills: resume.skills || [],
            projects: resume.projects || []
          }))

          // 更新全局技能和项目列表
          updateGlobalSkillsAndProjects()

          console.log('简历列表加载完成，共', resumeList.value.length, '个简历')
        }
      } catch (error) {
        console.error('加载简历列表失败:', error)
      }
    }

    // 生命周期钩子
    onMounted(async () => {
      document.addEventListener('keydown', handleKeyDown)
      await loadResumeList()
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeyDown)
    })





    return {
      isDragging,
      uploading,
      uploadProgress,
      fileInput,
      previewFile,
      showParsingToast,
      resumeList,
      extractedSkills,
      projectExperience,
      errors,
      handleFileSelect,
      handleDrop,
      handleDragOver,
      handleDragEnter,
      handleDragLeave,
      viewResume,
      deleteResume,
      retryParse,
      openFileDialog,
      closePreview,
      formatDate,
      getStatusText,
      getFileIcon,
      getPDFPreviewUrl,
      getOfficePreviewUrl
    }
  }
}
</script>

<style scoped>
.resume-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: #86868b;
}

.breadcrumb-item {
  color: #86868b;
}

.breadcrumb-item.active {
  color: #722ED1;
}

.breadcrumb-divider {
  margin: 0 8px;
}

.upload-section {
  margin-bottom: 30px;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #8b5cf6;
  background-color: #f8f6ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  width: 60px;
  height: 60px;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: #374151;
  margin: 0;
}

.upload-hint {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.resume-section, .skills-section, .projects-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 16px;
}

.resume-table {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1.5fr;
  background-color: #f9fafb;
  padding: 16px 20px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.table-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1.5fr;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.table-row:hover {
  background-color: #f9fafb;
}

.col-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  width: 16px;
  height: 16px;
  color: #6b7280;
}

.col-time, .col-size {
  font-size: 14px;
  color: #6b7280;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.parsing {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.parsed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.failed {
  background-color: #fee2e2;
  color: #991b1b;
}

.col-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn .svg-icon {
  width: 16px;
  height: 16px;
}

.view-btn {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.view-btn:hover {
  background-color: #3B82F6;
}

.edit-btn {
  background-color: #d1fae5;
  color: #047857;
}

.edit-btn:hover {
  background-color: #10B981;
}

.delete-btn {
  background-color: #fecaca;
  color: #b91c1c;
}

.delete-btn:hover {
  background-color: #EF4444;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #6b7280;
}

.skills-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background-color: #f3e8ff;
  color: #7c3aed;
  border: 1px solid #e9d5ff;
}

.skill-tag.skill {
  background-color: #f3e8ff;
  color: #7c3aed;
}

.skill-tag.frontend {
  background-color: #dbeafe;
  color: #1e40af;
}

.skill-tag.language {
  background-color: #fef3c7;
  color: #92400e;
}

.skill-tag.backend {
  background-color: #d1fae5;
  color: #065f46;
}

.skill-tag.database {
  background-color: #f3e8ff;
  color: #7c3aed;
}

.skill-tag.tool {
  background-color: #fdf2f8;
  color: #be185d;
}

.skill-tag.cloud {
  background-color: #ecfdf5;
  color: #047857;
}

.skill-tag.design {
  background-color: #fff7ed;
  color: #c2410c;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-item {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e5e7eb;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.project-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.project-period {
  font-size: 14px;
  color: #6b7280;
}

.project-description {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 16px;
}

.edit-detail-btn {
  background: none;
  border: none;
  color: #8b5cf6;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
}

.edit-detail-btn:hover {
  color: #7c3aed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #ffffff;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
}

.preview-modal {
  width: 95vw;
  height: 95vh;
  max-width: none;
  max-height: none;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.preview-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  height: 48px;
  min-height: 48px;
}

.preview-title {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
}

.close-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 6px;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: #e2e8f0;
  color: #374151;
}

.preview-body {
  padding: 0;
  height: calc(95vh - 48px);
  background-color: #1f2937;
  position: relative;
  overflow: hidden;
}

.preview-placeholder {
  text-align: center;
  color: #6b7280;
}

.preview-placeholder p {
  margin: 8px 0;
}

.upload-progress {
  margin-top: 16px;
  width: 100%;
  height: 20px;
  background-color: #f3f4f6;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background-color: #8b5cf6;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.progress-fill {
  height: 100%;
  background-color: #8b5cf6;
  border-radius: 10px;
}

.progress-text {
  text-align: center;
  font-size: 14px;
  color: #374151;
  margin-top: 8px;
}

.error-messages {
  margin-top: 16px;
  padding: 12px;
  background-color: #fee2e2;
  border-radius: 6px;
  color: #991b1b;
}

.error-item {
  margin-bottom: 8px;
}

.retry-btn {
  background: none;
  border: none;
  color: #8b5cf6;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
}

.retry-btn:hover {
  color: #7c3aed;
}

.parsing-toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  background-color: #ffffff;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
}

.loading-icon {
  width: 20px;
  height: 20px;
  color: #8b5cf6;
}

.pdf-preview {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.office-preview {
  width: 100%;
  height: 100%;
  border: none;
  background: #ffffff;
}

.preview-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #374151;
  border-top: 3px solid #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-modal {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
  }
  
  .preview-controls {
    padding: 8px 12px;
    height: 44px;
    min-height: 44px;
  }
  
  .preview-body {
    height: calc(100vh - 44px);
  }
  
  .preview-title {
    font-size: 16px;
  }
  
  .close-btn {
    width: 36px;
    height: 36px;
  }
}

/* 改进PDF预览在暗色背景下的显示 */
.pdf-preview {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}


</style>