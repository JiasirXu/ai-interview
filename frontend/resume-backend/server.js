const express = require('express')
const multer = require('multer')
const path = require('path')
const fs = require('fs')
const cors = require('cors')
const crypto = require('crypto')
const axios = require('axios')
const FormData = require('form-data')

const app = express()
const PORT = 3000

// 中间件
app.use(cors())
app.use(express.json())
app.use(express.static('uploads')) // 静态文件服务

// 讯飞API配置
const XUNFEI_CONFIG = {
  APPID: '014f8018',
  APISecret: 'ODQ4NTRlOGRkOGM2Y2NmMWRkN2FmZWFi',
  APIKey: 'a444fdfbce20c52641ce2b3167957e6d',
  // 通用文档识别(大模型)接口
  OCR_URL: 'https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm'
}

// 内存存储（生产环境建议使用数据库）
let resumeStore = new Map()

// 配置文件上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadPath = 'uploads/resumes'
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true })
    }
    cb(null, uploadPath)
  },
  filename: (req, file, cb) => {
    // 生成唯一文件名
    const uniqueName = `${Date.now()}-${Math.random().toString(36).substr(2)}-${file.originalname}`
    cb(null, uniqueName)
  }
})

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true)
    } else {
      cb(new Error('不支持的文件类型'))
    }
  }
})

// 讯飞API鉴权
function generateXunfeiAuth() {
  const host = 'cbm01.cn-huabei-1.xf-yun.com'
  const uri = '/v1/private/se75ocrbm'
  const method = 'POST'
  const date = new Date().toUTCString()
  
  // 生成签名
  const signatureOrigin = `host: ${host}\ndate: ${date}\n${method} ${uri} HTTP/1.1`
  const signature = crypto
    .createHmac('sha256', XUNFEI_CONFIG.APISecret)
    .update(signatureOrigin)
    .digest('base64')
  
  const authorizationOrigin = `api_key="${XUNFEI_CONFIG.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="${signature}"`
  const authorization = Buffer.from(authorizationOrigin).toString('base64')
  
  return {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Method': 'POST',
    'Host': host,
    'Date': date,
    'Authorization': `Signature ${authorization}`
  }
}

// 调用讯飞文档识别API
async function callXunfeiOCR(fileBase64) {
  try {
    const headers = generateXunfeiAuth()
    
    const requestData = {
      header: {
        app_id: XUNFEI_CONFIG.APPID,
        status: 3
      },
      parameter: {
        se75ocrbm: {
          result: {
            encoding: "utf8",
            compress: "raw",
            format: "json"
          }
        }
      },
      payload: {
        image: {
          encoding: "jpg", // 或根据文件类型调整
          status: 3,
          image: fileBase64
        }
      }
    }
    
    const response = await axios.post(XUNFEI_CONFIG.OCR_URL, requestData, { headers })
    
    if (response.data && response.data.payload) {
      // 解析识别结果
      const result = JSON.parse(Buffer.from(response.data.payload.result.text, 'base64').toString('utf8'))
      return result
    }
    
    throw new Error('讯飞API返回格式错误')
    
  } catch (error) {
    console.error('讯飞API调用失败:', error)
    throw error
  }
}

// 从识别结果提取技能和项目经历
function extractSkillsAndProjects(ocrResult) {
  const text = ocrResult.pages?.[0]?.lines?.map(line => line.words?.map(word => word.content).join('')).join('\n') || ''
  
  // 技能关键词
  const skillKeywords = [
    'JavaScript', 'TypeScript', 'Vue', 'React', 'Angular', 'Node.js',
    'Python', 'Java', 'C++', 'C#', 'Go', 'Rust', 'PHP',
    'HTML', 'CSS', 'SCSS', 'Less', 'Bootstrap', 'Tailwind',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLServer',
    'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
    'Spring', 'Express', 'Django', 'Flask', 'FastAPI',
    'Webpack', 'Vite', 'Rollup', 'Babel', 'ESLint'
  ]
  
  // 提取技能
  const extractedSkills = skillKeywords.filter(skill => 
    text.toLowerCase().includes(skill.toLowerCase())
  )
  
  // 提取项目经历（简单的正则匹配）
  const projectPatterns = [
    /项目名称[：:]\s*(.+)/g,
    /(?:项目|Project)[：:]?\s*(.+?)(?:\n|项目时间|技术栈|职责)/g,
    /(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}[\s~-]+\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})\s*(.+)/g
  ]
  
  const projects = []
  let projectId = 1
  
  projectPatterns.forEach(pattern => {
    let match
    while ((match = pattern.exec(text)) !== null) {
      const projectInfo = match[2] || match[1]
      if (projectInfo && projectInfo.length > 10 && projectInfo.length < 200) {
        projects.push({
          id: projectId++,
          title: projectInfo.substring(0, 50),
          period: match[1] || '时间不详',
          description: projectInfo
        })
      }
    }
  })
  
  return {
    skills: [...new Set(extractedSkills)], // 去重
    projects: projects.slice(0, 5) // 最多返回5个项目
  }
}

// API路由

// 上传简历
app.post('/api/resume/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: '请选择文件' })
    }
    
    const resumeId = crypto.randomUUID()
    const fileUrl = `http://localhost:${PORT}/resumes/${req.file.filename}`
    
    // 保存简历信息
    const resumeInfo = {
      id: resumeId,
      name: req.file.originalname,
      filename: req.file.filename,
      path: req.file.path,
      url: fileUrl,
      size: req.file.size,
      mimetype: req.file.mimetype,
      uploadTime: new Date(),
      status: 'uploaded'
    }
    
    resumeStore.set(resumeId, resumeInfo)
    
    res.json({
      id: resumeId,
      url: fileUrl,
      name: req.file.originalname,
      size: req.file.size
    })
    
  } catch (error) {
    console.error('文件上传失败:', error)
    res.status(500).json({ error: '文件上传失败' })
  }
})

// 解析简历
app.post('/api/resume/parse', async (req, res) => {
  try {
    const { fileUrl } = req.body
    
    if (!fileUrl) {
      return res.status(400).json({ error: '文件URL不能为空' })
    }
    
    // 读取文件并转换为base64
    const filename = path.basename(fileUrl)
    const filePath = path.join(__dirname, 'uploads/resumes', filename)
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: '文件不存在' })
    }
    
    const fileBuffer = fs.readFileSync(filePath)
    const fileBase64 = fileBuffer.toString('base64')
    
    // 调用讯飞API进行OCR识别
    const ocrResult = await callXunfeiOCR(fileBase64)
    
    // 提取技能和项目经历
    const extractedData = extractSkillsAndProjects(ocrResult)
    
    res.json({
      skills: extractedData.skills,
      projects: extractedData.projects,
      rawOcrResult: ocrResult // 可选：返回原始识别结果
    })
    
  } catch (error) {
    console.error('简历解析失败:', error)
    res.status(500).json({ 
      error: '简历解析失败',
      details: error.message 
    })
  }
})

// 删除简历
app.delete('/api/resume/:id', (req, res) => {
  try {
    const resumeId = req.params.id
    const resume = resumeStore.get(resumeId)
    
    if (!resume) {
      return res.status(404).json({ error: '简历不存在' })
    }
    
    // 删除文件
    if (fs.existsSync(resume.path)) {
      fs.unlinkSync(resume.path)
    }
    
    // 从存储中删除
    resumeStore.delete(resumeId)
    
    res.json({ message: '删除成功' })
    
  } catch (error) {
    console.error('删除失败:', error)
    res.status(500).json({ error: '删除失败' })
  }
})

// 获取简历列表
app.get('/api/resume/list', (req, res) => {
  try {
    const resumes = Array.from(resumeStore.values()).map(resume => ({
      id: resume.id,
      name: resume.name,
      url: resume.url,
      size: resume.size,
      uploadTime: resume.uploadTime,
      status: resume.status
    }))
    
    res.json(resumes)
    
  } catch (error) {
    console.error('获取简历列表失败:', error)
    res.status(500).json({ error: '获取简历列表失败' })
  }
})

// 获取简历详情
app.get('/api/resume/:id', (req, res) => {
  try {
    const resumeId = req.params.id
    const resume = resumeStore.get(resumeId)
    
    if (!resume) {
      return res.status(404).json({ error: '简历不存在' })
    }
    
    res.json(resume)
    
  } catch (error) {
    console.error('获取简历详情失败:', error)
    res.status(500).json({ error: '获取简历详情失败' })
  }
})

// 获取预览URL
app.get('/api/resume/:id/preview', (req, res) => {
  try {
    const resumeId = req.params.id
    const resume = resumeStore.get(resumeId)
    
    if (!resume) {
      return res.status(404).json({ error: '简历不存在' })
    }
    
    res.json({ 
      previewUrl: resume.url,
      type: resume.mimetype
    })
    
  } catch (error) {
    console.error('获取预览URL失败:', error)
    res.status(500).json({ error: '获取预览URL失败' })
  }
})

// 错误处理中间件
app.use((error, req, res, next) => {
  console.error('服务器错误:', error)
  
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: '文件大小超过限制' })
    }
  }
  
  res.status(500).json({ error: '服务器内部错误' })
})

// 启动服务器
app.listen(PORT, () => {
  console.log(`简历管理服务器运行在 http://localhost:${PORT}`)
  console.log('支持的API端点:')
  console.log('- POST /api/resume/upload - 上传简历')
  console.log('- POST /api/resume/parse - 解析简历')
  console.log('- DELETE /api/resume/:id - 删除简历')
  console.log('- GET /api/resume/list - 获取简历列表')
  console.log('- GET /api/resume/:id - 获取简历详情')
  console.log('- GET /api/resume/:id/preview - 获取预览URL')
}) 