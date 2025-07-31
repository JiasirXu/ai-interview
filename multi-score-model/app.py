from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import BertTokenizer
import json
import os
from models_6d import BertRegression6D, NUM_LABELS, FRONTEND_LABELS, get_dimension_info

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量存储模型和分词器
model = None
tokenizer = None
model_loaded = False

def load_model(model_dir="./saved_model_6d"):
    """加载训练好的6维度模型"""
    global model, tokenizer, model_loaded
    
    if not os.path.exists(model_dir):
        return False, f"模型目录 '{model_dir}' 不存在"
    
    try:
        # 加载分词器
        tokenizer = BertTokenizer.from_pretrained(model_dir)
        
        # 加载模型
        model = BertRegression6D(NUM_LABELS)
        
        # 尝试加载模型权重
        model_path = os.path.join(model_dir, 'model.safetensors')
        if not os.path.exists(model_path):
            model_path = os.path.join(model_dir, 'pytorch_model.bin')
        
        if not os.path.exists(model_path):
            return False, "找不到模型权重文件"
            
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=False))
        model.eval()
        model_loaded = True
        
        return True, "6维度模型加载成功"
    except Exception as e:
        return False, f"模型加载失败: {str(e)}"

def predict_scores_6d(text, max_len=128):
    """预测文本的6个维度评分"""
    if not model_loaded:
        return None, "模型未加载"
    
    try:
        # 准备输入
        inputs = tokenizer(text, return_tensors='pt', max_length=max_len, 
                          truncation=True, padding='max_length')
        
        with torch.no_grad():
            outputs = model(input_ids=inputs["input_ids"], 
                          attention_mask=inputs["attention_mask"])
            predictions = outputs.squeeze().tolist()
        
        # 构建结果字典
        result = {"text": text}
        for i, dim in enumerate(FRONTEND_LABELS):
            result[dim] = round(predictions[i], 2)  # 保留两位小数
        
        return result, None
    except Exception as e:
        return None, f"预测失败: {str(e)}"

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        "message": "AI模拟面试6维度评分API",
        "status": "运行中" if model_loaded else "模型未加载",
        "dimensions": len(FRONTEND_LABELS),
        "endpoints": {
            "/predict": "POST - 预测文本评分",
            "/health": "GET - 健康检查",
            "/dimensions": "GET - 获取评分维度说明",
            "/batch_predict": "POST - 批量预测"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model_loaded,
        "dimensions": len(FRONTEND_LABELS)
    })

@app.route('/dimensions', methods=['GET'])
def get_dimensions():
    """获取6个评分维度说明"""
    return jsonify(get_dimension_info())

@app.route('/predict', methods=['POST'])
def predict():
    """预测接口"""
    try:
        # 检查模型是否加载
        if not model_loaded:
            return jsonify({
                "error": "模型未加载，请先训练6维度模型或检查模型文件"
            }), 500
        
        # 获取请求数据
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "error": "请求格式错误，需要包含 'text' 字段"
            }), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({
                "error": "文本内容不能为空"
            }), 400
        
        # 预测评分
        result, error = predict_scores_6d(text)
        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/batch_predict', methods=['POST'])
def batch_predict():
    """批量预测接口"""
    try:
        if not model_loaded:
            return jsonify({
                "error": "模型未加载，请先训练6维度模型或检查模型文件"
            }), 500
        
        data = request.get_json()
        if not data or 'texts' not in data:
            return jsonify({
                "error": "请求格式错误，需要包含 'texts' 数组字段"
            }), 400
        
        texts = data['texts']
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                "error": "texts 必须是非空数组"
            }), 400
        
        results = []
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results.append({
                    "index": i,
                    "error": "文本内容不能为空"
                })
                continue
            
            result, error = predict_scores_6d(text.strip())
            if error:
                results.append({
                    "index": i,
                    "error": error
                })
            else:
                results.append({
                    "index": i,
                    "data": result
                })
        
        return jsonify({
            "success": True,
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "error": f"服务器内部错误: {str(e)}"
        }), 500

@app.route('/convert_format', methods=['POST'])
def convert_format():
    """转换评分格式为前端需要的格式"""
    try:
        data = request.get_json()
        if not data or 'scores' not in data:
            return jsonify({
                "error": "请求格式错误，需要包含 'scores' 字段"
            }), 400
        
        scores = data['scores']
        
        # 转换为前端友好的格式
        frontend_format = {
            "技术能力": scores.get("technical_ability", 0),
            "行为礼仪": scores.get("behavior_etiquette", 0),
            "表达逻辑": scores.get("expression_logic", 0),
            "应变能力": scores.get("adaptability", 0),
            "文化匹配": scores.get("cultural_fit", 0),
            "表达能力": scores.get("expression_clarity", 0)
        }
        
        return jsonify({
            "success": True,
            "frontend_scores": frontend_format
        })
        
    except Exception as e:
        return jsonify({
            "error": f"格式转换失败: {str(e)}"
        }), 500

if __name__ == '__main__':
    # 启动时尝试加载模型
    print("正在启动AI模拟面试6维度评分API...")
    success, message = load_model()
    print(f"模型加载状态: {message}")
    
    if not success:
        print("警告: 6维度模型未成功加载，API将无法进行预测")
        print("请先运行 'python train_6d.py --data_path data/train_expanded.jsonl --output_dir saved_model_6d' 训练模型")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5001, debug=True)
