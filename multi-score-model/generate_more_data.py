import json
import random
import re

# 面试问题模板
interview_questions = [
    "请介绍一下你的项目经验",
    "你在团队合作中遇到过什么困难？如何解决的？",
    "描述一个你解决技术难题的经历",
    "你对这个职位的理解是什么？",
    "你的职业规划是什么？",
    "你认为自己的优势和劣势是什么？",
    "你如何处理工作压力？",
    "描述一次你主动学习新技术的经历",
    "你在实习/工作中学到了什么？",
    "你对我们公司了解多少？",
    "你为什么选择这个专业/行业？",
    "描述一个你领导团队的经历",
    "你如何平衡学习和工作？",
    "你遇到过的最大挑战是什么？",
    "你如何与不同性格的同事合作？"
]

# 回答模板和变体
answer_templates = [
    {
        "template": "我在{company}实习期间，负责{project}项目。通过{method}方法，成功{result}。这个经历让我学会了{learning}。",
        "companies": ["腾讯", "阿里巴巴", "百度", "字节跳动", "华为", "小米", "美团", "滴滴", "京东", "网易"],
        "projects": ["用户画像系统", "推荐算法优化", "数据分析平台", "移动应用开发", "后端服务架构", "机器学习模型", "前端界面设计", "测试自动化"],
        "methods": ["敏捷开发", "数据驱动", "用户调研", "A/B测试", "代码重构", "性能优化", "团队协作", "技术调研"],
        "results": ["提升了20%的用户活跃度", "减少了30%的响应时间", "优化了系统性能", "改善了用户体验", "提高了代码质量", "增强了系统稳定性"],
        "learnings": ["团队协作的重要性", "技术选型的考量", "用户需求分析", "项目管理技能", "沟通表达能力", "问题解决思路"]
    },
    {
        "template": "我认为{skill}是非常重要的。在{situation}时，我通过{action}，最终{outcome}。",
        "skills": ["沟通能力", "学习能力", "解决问题的能力", "团队合作", "创新思维", "时间管理", "抗压能力", "适应能力"],
        "situations": ["项目紧急上线", "团队意见分歧", "技术难题攻关", "客户需求变更", "系统故障处理", "新技术学习", "跨部门协作"],
        "actions": ["主动沟通协调", "深入研究学习", "制定详细计划", "寻求专家建议", "组织团队讨论", "分析问题根源", "优化工作流程"],
        "outcomes": ["项目按时交付", "团队达成共识", "问题得到解决", "效率显著提升", "质量明显改善", "经验得到积累", "能力得到提升"]
    }
]

def generate_answer(template_data):
    """根据模板生成回答"""
    template = template_data["template"]
    result = template
    
    for key, values in template_data.items():
        if key != "template":
            placeholder = "{" + key.rstrip("s") + "}"
            if placeholder in result:
                result = result.replace(placeholder, random.choice(values))
    
    return result

def generate_scores():
    """生成随机但合理的评分"""
    # 基础分数在6-9之间，然后添加一些随机变化
    base_score = random.uniform(6.0, 9.0)
    scores = {}
    
    dimensions = ["clarity", "relevance", "logic", "fluency", "confidence", "professionality", "completeness", "empathy"]
    
    for dim in dimensions:
        # 在基础分数基础上添加±1.5的随机变化
        score = base_score + random.uniform(-1.5, 1.5)
        # 确保分数在0-10范围内
        score = max(0.0, min(10.0, score))
        scores[dim] = round(score, 1)
    
    return scores

def generate_training_data(num_samples=200):
    """生成训练数据"""
    data = []
    
    for i in range(num_samples):
        # 随机选择问题和回答模板
        question = random.choice(interview_questions)
        template = random.choice(answer_templates)
        answer = generate_answer(template)
        
        # 组合问题和回答
        text = f"问题: {question}\n回答: {answer}"
        
        # 生成评分
        scores = generate_scores()
        
        # 创建数据条目
        item = {"text": text}
        item.update(scores)
        
        data.append(item)
    
    return data

def save_data(data, filename):
    """保存数据到JSONL文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    print("正在生成训练数据...")
    
    # 读取现有数据
    existing_data = []
    try:
        with open('data/train.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    existing_data.append(json.loads(line))
        print(f"现有数据: {len(existing_data)}条")
    except FileNotFoundError:
        print("未找到现有数据文件")
    
    # 生成新数据
    new_data = generate_training_data(190)  # 生成190条新数据，加上现有10条，总共200条
    
    # 合并数据
    all_data = existing_data + new_data
    
    # 保存到新文件
    save_data(all_data, 'data/train_expanded.jsonl')
    
    print(f"数据生成完成！")
    print(f"总数据量: {len(all_data)}条")
    print(f"已保存到: data/train_expanded.jsonl")
    
    # 显示一些样本
    print("\n样本数据:")
    for i, item in enumerate(all_data[-3:], 1):
        print(f"\n样本 {i}:")
        print(f"文本: {item['text'][:100]}...")
        print(f"评分: clarity={item['clarity']}, relevance={item['relevance']}, logic={item['logic']}")

if __name__ == "__main__":
    main()
