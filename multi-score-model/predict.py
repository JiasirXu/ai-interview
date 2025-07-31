import torch
from transformers import BertTokenizer
import json
import os
import argparse

from models import BertRegression, NUM_LABELS

def predict_scores(model_dir, text, max_len=128):
    # 加载分词器和模型
    tokenizer = BertTokenizer.from_pretrained(model_dir)
    model = BertRegression(NUM_LABELS)
    
    # 尝试加载 model.safetensors，如果不存在则尝试 pytorch_model.bin
    model_path = os.path.join(model_dir, 'model.safetensors')
    if not os.path.exists(model_path):
        model_path = os.path.join(model_dir, 'pytorch_model.bin')

    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=False))
    model.eval()

    # 准备输入
    inputs = tokenizer(text, return_tensors='pt', max_length=max_len, truncation=True, padding='max_length')

    with torch.no_grad():
        outputs = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        predictions = outputs.squeeze().tolist()

    # 定义维度名称
    dimensions = ["clarity", "relevance", "logic", "fluency", "confidence", "professionality", "completeness", "empathy"]

    # 构建结果字典
    result = {"text": text}
    for i, dim in enumerate(dimensions):
        result[dim] = round(predictions[i], 2) # 保留两位小数

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict multi-label scores for interview text.")
    parser.add_argument("--model_dir", type=str, required=True, help="Directory containing the trained model and tokenizer.")
    parser.add_argument("--text", type=str, required=True, help="Text to be evaluated.")
    parser.add_argument("--max_len", type=int, default=128, help="Maximum sequence length for tokenizer.")

    args = parser.parse_args()

    if not os.path.exists(args.model_dir):
        print(f"Error: Model directory '{args.model_dir}' not found.")
    else:
        scores = predict_scores(args.model_dir, args.text, args.max_len)
        print(json.dumps(scores, ensure_ascii=False, indent=2))


