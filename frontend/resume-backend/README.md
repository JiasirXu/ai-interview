# 简历管理后端服务

集成讯飞通用文档识别大模型的简历管理后端服务。

## 功能特性

- ✅ 文件上传（支持PDF、Word格式）
- ✅ 讯飞OCR文档识别
- ✅ 智能提取技能和项目经历
- ✅ 文件预览和下载
- ✅ 简历管理CRUD操作
- ✅ 跨域支持

## 技术栈

- Node.js + Express.js
- Multer (文件上传)
- Axios (HTTP请求)
- 讯飞通用文档识别API

## 快速开始

### 1. 安装依赖

```bash
cd resume-backend
npm install
```

### 2. 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

服务器将在 `http://localhost:3000` 启动

### 3. API端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/resume/upload` | 上传简历文件 |
| POST | `/api/resume/parse` | 解析简历内容 |
| DELETE | `/api/resume/:id` | 删除简历 |
| GET | `/api/resume/list` | 获取简历列表 |
| GET | `/api/resume/:id` | 获取简历详情 |
| GET | `/api/resume/:id/preview` | 获取预览URL |

### 4. 讯飞API配置

项目已配置了你提供的讯飞API认证信息：

```javascript
const XUNFEI_CONFIG = {
  APPID: '014f8018',
  APISecret: 'ODQ4NTRlOGRkOGM2Y2NmMWRkN2FmZWFi',
  APIKey: 'a444fdfbce20c52641ce2b3167957e6d',
  OCR_URL: 'https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm'
}
```

## 使用说明

### 文件上传

```bash
curl -X POST http://localhost:3000/api/resume/upload \
  -F "file=@resume.pdf"
```

### 简历解析

```bash
curl -X POST http://localhost:3000/api/resume/parse \
  -H "Content-Type: application/json" \
  -d '{"fileUrl": "http://localhost:3000/resumes/filename.pdf"}'
```

## 项目结构

```
resume-backend/
├── server.js          # 主服务器文件
├── package.json       # 项目配置
├── README.md          # 说明文档
├── uploads/           # 文件上传目录
│   └── resumes/       # 简历文件存储
└── node_modules/      # 依赖包
```

## 注意事项

1. **文件存储**: 当前使用本地文件系统存储，生产环境建议使用云存储
2. **数据存储**: 当前使用内存存储简历信息，重启后数据会丢失
3. **安全性**: 建议添加文件类型检查和病毒扫描
4. **性能**: 大文件处理可能需要优化

## 扩展建议

- 集成数据库（MongoDB/MySQL）
- 添加用户认证和权限控制
- 支持更多文件格式
- 添加文件压缩和优化
- 实现分页和搜索功能 