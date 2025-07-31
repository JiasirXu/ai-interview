import torch
from transformers import BertTokenizer, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
import json
import os
import argparse
import numpy as np

from models_6d import BertRegression6D, NUM_LABELS, DIMENSION_MAPPING
from dataset import InterviewDataset6D
from metrics import compute_metrics

class InterviewDataset6D(torch.utils.data.Dataset):
    def __init__(self, data, tokenizer, max_len):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        
        # 6个前端维度对应的原始维度
        self.dimension_keys = list(DIMENSION_MAPPING.values())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item["text"]
        
        # 提取对应的6个维度评分
        labels = []
        for original_dim in self.dimension_keys:
            labels.append(float(item[original_dim]))
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(labels, dtype=torch.float)
        }

def train_model_6d(data, model_output_dir, model_name="bert-base-chinese", max_len=128, batch_size=16, num_epochs=3, learning_rate=2e-5):
    # 加载分词器
    tokenizer = BertTokenizer.from_pretrained(model_name)

    # 划分训练集和验证集
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)

    train_dataset = InterviewDataset6D(train_data, tokenizer, max_len)
    val_dataset = InterviewDataset6D(val_data, tokenizer, max_len)

    # 初始化模型
    model = BertRegression6D(NUM_LABELS, model_name)

    # 设置训练参数
    training_args = TrainingArguments(
        output_dir=model_output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f'{model_output_dir}/logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        learning_rate=learning_rate,
    )

    # 初始化训练器
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    # 开始训练
    print("开始训练6维度模型...")
    trainer.train()

    # 保存模型和分词器
    trainer.save_model()
    tokenizer.save_pretrained(model_output_dir)

    print(f"6维度模型已保存到 {model_output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a 6-dimension regression model for interview evaluation.")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the training data file (JSONL format).")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save the trained model and tokenizer.")
    parser.add_argument("--model_name", type=str, default="bert-base-chinese", help="Pre-trained BERT model name.")
    parser.add_argument("--max_len", type=int, default=128, help="Maximum sequence length for tokenizer.")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for training and evaluation.")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--learning_rate", type=float, default=2e-5, help="Learning rate for optimizer.")

    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"开始训练6维度模型，数据文件：{args.data_path}，输出目录：{args.output_dir}")
    
    # 加载数据
    data = []
    with open(args.data_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from line: {line}. Error: {e}")
                    continue

    print(f"加载了 {len(data)} 条训练数据")
    print("维度映射:")
    for frontend_dim, original_dim in DIMENSION_MAPPING.items():
        print(f"  {frontend_dim} <- {original_dim}")

    train_model_6d(
        data=data,
        model_output_dir=args.output_dir,
        model_name=args.model_name,
        max_len=args.max_len,
        batch_size=args.batch_size,
        num_epochs=args.num_epochs,
        learning_rate=args.learning_rate
    )
    print("6维度模型训练完成！")
