# AI模拟面试多维度评分模型

本项目旨在训练一个多标签回归模型，用于将面试者的自然语言回答转换为8个维度的量化评分。这些评分可以用于生成雷达图、热力图等可视化报告，为面试官提供更结构化的评估依据。

## 项目结构

```
your_project/
│
├── train.py             # 模型训练：加载数据、训练、保存模型
├── predict.py           # 模型使用：加载模型、输入预测、输出打分结果
│
├── models.py            # 自定义模型结构（BertRegression）
├── dataset.py           # Dataset 类和数据加载逻辑
├── metrics.py           # MSE、MAE、Pearson 等评估指标
├── utils.py             # 工具函数（如保存JSON、分数标准化等）
│
├── data/
│   └── train.jsonl      # 你的训练数据（JSONL格式，每行一个JSON对象）
│
├── saved_model/         # 训练完成后保存的模型目录
│
└── config.json          # 配置文件，包含模型参数和训练设置
```

## 评分维度

模型将对以下8个维度进行评分（0-10的浮点数）：

| 维度编号 | 名称（英文）    | 中文含义       | 评价说明（打分参考）                               |
| -------- | --------------- | -------------- | -------------------------------------------------- |
| 1        | clarity         | 表达清晰度     | 语言是否准确、句式完整、意思清楚                   |
| 2        | relevance       | 回答相关性     | 是否紧扣提问主题，是否跑题                         |
| 3        | logic           | 思维逻辑性     | 表达是否条理清晰，有逻辑、有因果、有结构           |
| 4        | fluency         | 语言流畅度     | 有没有卡顿、重复语、语法错误等                     |
| 5        | confidence      | 自信程度       | 语气是否坚定、有信心，语速是否自然                 |
| 6        | professionality | 专业性         | 是否展现出专业知识或行业理解                       |
| 7        | completeness    | 回答完整性     | 回答是否覆盖问题要点，是否有遗漏                   |
| 8        | empathy         | 共情力 / 沟通亲和力 | 表达是否有温度，是否表现出倾听与理解能力           |

## 环境搭建

1.  **克隆项目**：
    ```bash
    git clone <项目仓库地址>
    cd <项目目录>
    ```

2.  **安装依赖**：
    ```bash
    pip install torch transformers scikit-learn scipy
    ```

## 数据准备

训练数据应为JSONL格式，每行一个JSON对象，包含`text`字段（面试回答文本）和对应的8个评分维度的浮点数（0-10）。例如：

```json
{"text": "我曾在某科技公司担任实习生，主要负责前端开发，参与了多个项目的需求分析、设计和实现。", "clarity": 8.5, "relevance": 7.0, "logic": 7.5, "fluency": 8.0, "confidence": 7.0, "professionality": 8.0, "completeness": 7.5, "empathy": 6.0}
{"text": "嗯...就是...我做过一些...那个...网页开发...", "clarity": 3.0, "relevance": 5.0, "logic": 4.0, "fluency": 3.5, "confidence": 2.0, "professionality": 4.0, "completeness": 3.0, "empathy": 5.0}
```

将您的训练数据保存到 `data/train.jsonl` 文件中。

## 模型训练

运行 `train.py` 脚本来训练模型。训练完成后，模型文件和分词器将保存到 `saved_model/` 目录下。

```bash
python train.py --data_path data/train.jsonl --output_dir saved_model/
```

您可以通过修改 `config.json` 文件来调整训练参数，例如 `model_name`, `max_len`, `batch_size`, `num_epochs`, `learning_rate` 等。

## 模型预测

运行 `predict.py` 脚本来使用训练好的模型进行预测。您需要指定模型所在的目录和要评估的文本。

```bash
python predict.py --model_dir saved_model/ --text "我主要参与了推荐系统的设计与优化..."
```

输出示例：

```json
{
  "text": "我主要参与了推荐系统的设计与优化...",
  "clarity": 8.2,
  "relevance": 7.9,
  "logic": 8.0,
  "fluency": 7.5,
  "confidence": 8.3,
  "professionality": 8.8,
  "completeness": 8.0,
  "empathy": 7.2
}
```

## 部署为API (Flask)

您可以将 `predict.py` 封装成一个Flask API，以便后端系统调用。以下是一个简单的示例：

```python
from flask import Flask, request, jsonify
from predict import predict_scores
import os

app = Flask(__name__)

MODEL_DIR = "./saved_model/" # 确保模型已训练并保存在此目录

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        scores = predict_scores(MODEL_DIR, text)
        return jsonify(scores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    if not os.path.exists(MODEL_DIR):
        print(f"Error: Model directory \'{MODEL_DIR}\' not found. Please train the model first.")
    else:
        app.run(host="0.0.0.0", port=5000)
```

将上述代码保存为 `app.py`，然后运行 `python app.py` 即可启动API服务。

## 进一步开发

- **数据收集**：根据实际面试场景，收集更多高质量的文本回答和多维度评分数据，以提高模型性能。
- **模型优化**：尝试不同的预训练模型（如TinyBERT, MacBERT, BGE），调整模型结构和超参数。
- **评估指标**：除了Pearson相关系数，还可以考虑其他回归评估指标，如MSE, MAE等。
- **前端集成**：将API集成到面试报告页面，并使用雷达图、热力图等方式可视化评分结果。


