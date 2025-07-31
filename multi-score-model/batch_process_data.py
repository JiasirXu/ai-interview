#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理面试数据
将多份面试数据转换为训练格式
"""

import json
import os
from typing import Dict, List, Any


def analyze_answer_quality(answer: str, expression: str, tone: str) -> Dict[str, float]:
    """
    根据回答内容、表达和语调分析8个维度的评分
    基于讯飞星火模型的评估标准
    """
    
    # 基础评分
    base_score = 7.0
    
    # 表达映射（基于面试表现）
    expression_map = {
        "专注": {"clarity": 0.8, "confidence": 0.5, "professionality": 0.5},
        "思考": {"logic": 0.8, "completeness": 0.3, "confidence": -0.2},
        "流畅": {"fluency": 1.0, "confidence": 0.5, "clarity": 0.3},
        "自然": {"fluency": 0.8, "confidence": 0.3, "empathy": 0.5},
        "兴奋": {"confidence": 0.8, "empathy": 0.5, "fluency": 0.3},
        "真诚": {"empathy": 1.0, "confidence": 0.3, "clarity": 0.2},
        "坚定": {"confidence": 1.0, "clarity": 0.5, "logic": 0.3},
        "欣慰": {"empathy": 0.8, "confidence": 0.3, "completeness": 0.2}
    }
    
    # 语调映射
    tone_map = {
        "坚定": {"confidence": 0.8, "clarity": 0.5, "professionality": 0.3},
        "诚恳": {"empathy": 0.8, "confidence": 0.3, "relevance": 0.2},
        "自信": {"confidence": 1.0, "fluency": 0.5, "clarity": 0.3},
        "稳重": {"confidence": 0.6, "logic": 0.5, "professionality": 0.5},
        "清晰": {"clarity": 1.0, "fluency": 0.5, "logic": 0.3},
        "专业": {"professionality": 1.0, "clarity": 0.5, "logic": 0.3},
        "沉稳": {"confidence": 0.5, "professionality": 0.8, "logic": 0.3}
    }
    
    # 初始化评分
    scores = {
        "clarity": base_score,
        "relevance": base_score,
        "logic": base_score,
        "fluency": base_score,
        "confidence": base_score,
        "professionality": base_score,
        "completeness": base_score,
        "empathy": base_score,
    }
    
    # 根据回答内容长度和质量调整
    answer_len = len(answer)
    if answer_len < 50:
        scores["completeness"] -= 2.0
        scores["clarity"] -= 1.0
    elif answer_len > 150:
        scores["completeness"] += 1.0
        scores["professionality"] += 0.5
    
    # 技术关键词分析
    if any(keyword in answer for keyword in ["项目", "实习", "工作", "实践", "经历"]):
        scores["relevance"] += 1.0
        scores["professionality"] += 0.5
    
    # 逻辑词分析
    if any(keyword in answer for keyword in ["首先", "然后", "最后", "因此", "所以", "通过"]):
        scores["logic"] += 1.0
        scores["clarity"] += 0.5
    
    # 数据和成果分析
    if any(keyword in answer for keyword in ["数据", "结果", "提升", "优化", "解决", "%", "倍"]):
        scores["professionality"] += 1.0
        scores["completeness"] += 0.5
    
    # 应用表达调整
    if expression in expression_map:
        for dim, adjustment in expression_map[expression].items():
            scores[dim] += adjustment
    
    # 应用语调调整
    if tone in tone_map:
        for dim, adjustment in tone_map[tone].items():
            scores[dim] += adjustment
    
    # 确保分数在0-10范围内
    for dim in scores:
        scores[dim] = max(0.0, min(10.0, scores[dim]))
    
    return scores


def process_interview_data(interview_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    处理单份面试数据
    """
    training_data = []
    
    for item in interview_data["interview"]:
        question = item["question"]
        answer = item["answer"]
        expression = item["expression"]
        tone = item["tone"]
        
        # 组合文本
        text = f"问题: {question}\n回答: {answer}"
        
        # 分析评分
        scores = analyze_answer_quality(answer, expression, tone)
        
        # 构造训练数据项
        training_item = {
            "text": text,
            **scores
        }
        
        training_data.append(training_item)
    
    return training_data


def batch_process_files(input_dir: str, output_file: str):
    """
    批量处理多个面试数据文件
    """
    all_training_data = []
    
    # 遍历输入目录中的所有JSON文件
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            print(f"处理文件: {filename}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    interview_data = json.load(f)
                
                # 处理单份数据
                training_data = process_interview_data(interview_data)
                all_training_data.extend(training_data)
                
                print(f"  - 处理了 {len(training_data)} 条问答")
                
            except Exception as e:
                print(f"  - 处理文件 {filename} 时出错: {e}")
    
    # 保存合并后的训练数据
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in all_training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"\n批量处理完成:")
    print(f"  - 总共处理了 {len(all_training_data)} 条训练数据")
    print(f"  - 保存到: {output_file}")


def process_single_file(input_file: str, output_file: str):
    """
    处理单个面试数据文件
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        interview_data = json.load(f)
    
    training_data = process_interview_data(interview_data)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"处理完成:")
    print(f"  - 处理了 {len(training_data)} 条问答")
    print(f"  - 保存到: {output_file}")


if __name__ == "__main__":
    # 示例用法
    print("使用方法:")
    print("1. 处理单个文件: python batch_process_data.py single input.json data/train.jsonl")
    print("2. 批量处理目录: python batch_process_data.py batch input_dir/ data/train.jsonl")
    
    # 这里可以添加命令行参数处理
    # 或者直接调用函数
    
    # 示例：处理单个文件
    # process_single_file("sample_interview.json", "data/train.jsonl")
    
    # 示例：批量处理
    # batch_process_files("interview_data/", "data/train.jsonl") 