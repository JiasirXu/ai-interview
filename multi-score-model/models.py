import torch
from transformers import BertModel

# 定义前端6个评估维度（从8个维度中选择6个）
FRONTEND_LABELS = [
    "technical_ability",    # 技术能力 <- professionality
    "behavior_etiquette",   # 行为礼仪 <- empathy  
    "expression_logic",     # 表达逻辑 <- logic
    "adaptability",         # 应变能力 <- confidence
    "cultural_fit",         # 文化匹配 <- relevance
    "expression_clarity"    # 表达能力 <- clarity
]

# 原始8个维度到前端6个维度的映射
DIMENSION_MAPPING = {
    "technical_ability": "professionality",
    "behavior_etiquette": "empathy",
    "expression_logic": "logic", 
    "adaptability": "confidence",
    "cultural_fit": "relevance",
    "expression_clarity": "clarity"
}

# 反向映射（从原始维度到前端维度）
REVERSE_MAPPING = {v: k for k, v in DIMENSION_MAPPING.items()}

NUM_LABELS = len(FRONTEND_LABELS)

# 定义 BERT + 回归头结构（6个输出）
class BertRegression6D(torch.nn.Module):
    def __init__(self, num_labels=6, model_name="bert-base-chinese"):
        super().__init__()
        self.bert = BertModel.from_pretrained(model_name)
        self.regressor = torch.nn.Linear(self.bert.config.hidden_size, num_labels)
        self.loss_fn = torch.nn.MSELoss()

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        logits = self.regressor(pooled_output)

        loss = None
        if labels is not None:
            loss = self.loss_fn(logits, labels)

        return (loss, logits) if loss is not None else logits

def convert_8d_to_6d_scores(scores_8d):
    """将8维度评分转换为6维度评分"""
    scores_6d = {}
    
    # 8个原始维度
    original_dims = ["clarity", "relevance", "logic", "fluency", 
                    "confidence", "professionality", "completeness", "empathy"]
    
    # 映射到6个前端维度
    for frontend_dim, original_dim in DIMENSION_MAPPING.items():
        if original_dim in scores_8d:
            scores_6d[frontend_dim] = scores_8d[original_dim]
    
    return scores_6d

def get_dimension_info():
    """获取6个维度的详细信息"""
    return {
        "technical_ability": {
            "name": "技术能力", 
            "description": "专业知识掌握程度和技术理解能力",
            "original": "professionality"
        },
        "behavior_etiquette": {
            "name": "行为礼仪", 
            "description": "沟通亲和力和情商表现",
            "original": "empathy"
        },
        "expression_logic": {
            "name": "表达逻辑", 
            "description": "思维条理性和逻辑结构",
            "original": "logic"
        },
        "adaptability": {
            "name": "应变能力", 
            "description": "自信程度和应对压力的能力",
            "original": "confidence"
        },
        "cultural_fit": {
            "name": "文化匹配", 
            "description": "回答与企业文化和岗位的匹配度",
            "original": "relevance"
        },
        "expression_clarity": {
            "name": "表达能力", 
            "description": "语言表达的清晰度和准确性",
            "original": "clarity"
        }
    }
