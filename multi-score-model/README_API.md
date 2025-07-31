# AI模拟面试多维度评分API

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 训练模型（如果还没有训练）
```bash
python train.py
```

### 3. 启动API服务
```bash
python app.py
```

服务将在 `http://localhost:5000` 启动

## API接口文档

### 1. 健康检查
- **URL**: `GET /health`
- **响应**:
```json
{
    "status": "healthy",
    "model_loaded": true
}
```

### 2. 获取评分维度说明
- **URL**: `GET /dimensions`
- **响应**: 返回8个评分维度的详细说明

### 3. 单文本预测
- **URL**: `POST /predict`
- **请求体**:
```json
{
    "text": "我认为这个职位非常适合我，因为我有相关的工作经验..."
}
```
- **响应**:
```json
{
    "success": true,
    "data": {
        "text": "我认为这个职位非常适合我...",
        "clarity": 8.5,
        "relevance": 9.2,
        "logic": 7.8,
        "fluency": 8.9,
        "confidence": 8.1,
        "professionality": 7.5,
        "completeness": 8.3,
        "empathy": 7.9
    }
}
```

### 4. 批量预测
- **URL**: `POST /batch_predict`
- **请求体**:
```json
{
    "texts": [
        "第一段面试回答...",
        "第二段面试回答..."
    ]
}
```

## 评分维度说明

| 维度 | 中文名称 | 评分范围 | 说明 |
|------|----------|----------|------|
| clarity | 表达清晰度 | 0-10 | 语言是否准确、句式完整、意思清楚 |
| relevance | 回答相关性 | 0-10 | 是否紧扣提问主题，是否跑题 |
| logic | 思维逻辑性 | 0-10 | 表达是否条理清晰，有逻辑、有因果、有结构 |
| fluency | 语言流畅度 | 0-10 | 有没有卡顿、重复语、语法错误等 |
| confidence | 自信程度 | 0-10 | 语气是否坚定、有信心，语速是否自然 |
| professionality | 专业性 | 0-10 | 是否展现出专业知识或行业理解 |
| completeness | 回答完整性 | 0-10 | 回答是否覆盖问题要点，是否有遗漏 |
| empathy | 共情力/沟通亲和力 | 0-10 | 表达是否有温度，是否表现出倾听与理解能力 |

## 使用示例

### Python客户端示例
```python
import requests

# 单文本预测
response = requests.post('http://localhost:5000/predict', 
    json={'text': '您的面试回答文本'})
result = response.json()
print(result)

# 批量预测
response = requests.post('http://localhost:5000/batch_predict', 
    json={'texts': ['回答1', '回答2']})
results = response.json()
print(results)
```

### JavaScript客户端示例
```javascript
// 单文本预测
fetch('http://localhost:5000/predict', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: '您的面试回答文本'})
})
.then(response => response.json())
.then(data => console.log(data));
```

## 错误处理

API会返回相应的HTTP状态码和错误信息：
- `400`: 请求参数错误
- `500`: 服务器内部错误（如模型未加载）

## 注意事项

1. 首次使用前必须先训练模型
2. 模型文件较大，首次加载需要一些时间
3. 建议在生产环境中使用更稳定的WSGI服务器（如Gunicorn）
