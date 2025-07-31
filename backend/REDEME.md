# 面试系统后端架构说明

## 架构概述

本项目采用Flask + SQLAlchemy架构，严格按照分层设计原则，不使用Blueprint等框架替代方案。

## 目录结构

```
软件杯后端/
├── app/
│   ├── __init__.py           # 应用包初始化
│   ├── main.py              # Flask应用入口
│   ├── controllers/         # 控制器层
│   │   ├── auth_controller.py
│   │   ├── resume_controller.py
│   │   ├── interview_controller.py
│   │   └── result_controller.py
│   ├── services/            # 服务层
│   │   ├── spark_service.py
│   │   ├── resume_service.py
│   │   ├── audio_service.py
│   │   ├── vision_service.py
│   │   └── avatar_service.py
│   ├── models/             # 数据模型层
│   │   ├── user.py
│   │   ├── resume.py
│   │   └── interview.py
│   └── utils/              # 工具层
│       ├── ws_client.py
│       ├── async_utils.py
│       └── parser.py
├── config.py               # 配置文件
├── run.py                  # 应用启动文件
└── requirements.txt        # 依赖包
```

## 架构分层

### 1. 应用入口层 (app/main.py)
- **职责**: Flask应用创建、扩展初始化、路由注册
- **特点**: 不使用Blueprint，采用直接路由注册方式
- **核心函数**: `create_app()`, `register_routes()`

### 2. 控制器层 (app/controllers/)
- **职责**: 处理HTTP请求、参数验证、响应格式化
- **特点**: 只负责路由处理，不包含业务逻辑
- **文件说明**:
  - `auth_controller.py`: 用户认证相关路由
  - `resume_controller.py`: 简历管理相关路由
  - `interview_controller.py`: 面试流程相关路由
  - `result_controller.py`: 面试结果相关路由

### 3. 服务层 (app/services/)
- **职责**: 业务逻辑处理、外部API调用、数据处理
- **特点**: 封装所有AI功能和业务逻辑
- **核心服务**:
  - `SparkService`: 讯飞Spark X1的HTTP + WebSocket调用
  - `ResumeService`: 通用文档识别HTTP API + 简历结构提取
  - `AudioService`: 实时语音转写WebSocket客户端处理
  - `VisionService`: 人脸检测 + 表情识别WebAPI调用
  - `AvatarService`: 虚拟人交互控制

### 4. 模型层 (app/models/)
- **职责**: 数据库模型定义、ORM关系映射
- **特点**: 使用SQLAlchemy ORM，支持JSON字段存储复杂数据
- **核心模型**:
  - `User`: 用户信息模型（包含偏好设置）
  - `Resume`: 简历信息模型（包含结构化数据）
  - `Interview`: 面试记录模型（包含所有面试数据）
  - `SystemConfig`: 系统配置模型

### 5. 工具层 (app/utils/)
- **职责**: 通用工具函数、辅助类
- **特点**: 可复用的功能模块
- **核心工具**:
  - `WSClient`: WebSocket客户端封装
  - `AsyncTaskManager`: 异步任务管理器
  - `JSONParser`: JSON解析工具

## 核心业务流程

### 简历上传流程
1. 前端上传 → 控制器校验身份
2. 服务层存储文件 → 调用resume_service处理
3. OCR/文本提取 → Spark分析
4. 存储结构化数据

### 面试调度流程
1. 初始化多服务协同
2. 并发连接各种AI服务
3. 每轮问答控制
4. 汇总评估

## 技术特点

### 1. 严格分层架构
- 控制器只负责路由和参数校验
- 所有业务逻辑封装在服务层
- 数据访问统一通过模型层

### 2. 服务化设计
- 每个AI功能独立封装
- 支持并发处理和异步任务
- 完整的错误处理和日志记录

### 3. 数据模型设计
- 支持JSON字段存储复杂数据结构
- 完整的关联关系定义
- 支持分页查询和条件过滤

### 4. 可扩展性
- 模块化设计，易于添加新功能
- 统一的错误处理机制
- 完善的日志系统

## 启动方式

1. 安装依赖：`pip install -r requirements.txt`
2. 配置环境变量：复制`env.example`为`.env`并填写配置
3. 启动应用：`python run.py`
4. 测试架构：`python test_app.py`

## 注意事项

1. 本架构不使用Blueprint，所有路由通过直接注册方式
2. 数据库迁移需要手动处理
3. 所有AI服务调用都封装在服务层
4. 确保所有依赖包正确安装

## 开发规范

### 添加新功能
1. 在对应的服务层添加业务逻辑
2. 在控制器层添加路由处理
3. 在模型层添加数据结构（如需要）
4. 在工具层添加通用功能（如需要）

### 错误处理
- 所有异常都应该在控制器层捕获
- 使用统一的错误响应格式
- 记录详细的错误日志

### 代码风格
- 使用中文注释
- 遵循PEP 8规范
- 函数和类都应该有完整的文档字符串 