#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历结构ORM模型
"""

import json
from datetime import datetime
from . import db

class Resume(db.Model):
    """简历信息表"""
    
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    
    # 文件信息
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, doc, docx
    file_size = db.Column(db.Integer, nullable=True)
    
    # 原始文本内容
    raw_text = db.Column(db.Text, nullable=True)
    
    # 结构化数据（JSON格式存储）
    personal_info = db.Column(db.Text, nullable=True)  # 个人信息
    education = db.Column(db.Text, nullable=True)      # 教育经历
    work_experience = db.Column(db.Text, nullable=True) # 工作经历
    skills = db.Column(db.Text, nullable=True)         # 技能清单
    projects = db.Column(db.Text, nullable=True)       # 项目经验
    certifications = db.Column(db.Text, nullable=True) # 证书资质
    
    # AI分析结果
    ai_skills_tags = db.Column(db.Text, nullable=True)     # AI提取的技能标签
    ai_positions = db.Column(db.Text, nullable=True)       # AI推荐的岗位
    ai_analysis = db.Column(db.Text, nullable=True)        # AI综合分析
    
    # 状态
    status = db.Column(db.String(20), default='processing')  # processing, completed, error
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_personal_info(self, data):
        """设置个人信息"""
        self.personal_info = json.dumps(data, ensure_ascii=False)
    
    def get_personal_info(self):
        """获取个人信息"""
        if self.personal_info:
            return json.loads(self.personal_info)
        return {}
    
    def set_education(self, data):
        """设置教育经历"""
        self.education = json.dumps(data, ensure_ascii=False)
    
    def get_education(self):
        """获取教育经历"""
        if self.education:
            return json.loads(self.education)
        return []
    
    def set_work_experience(self, data):
        """设置工作经历"""
        self.work_experience = json.dumps(data, ensure_ascii=False)
    
    def get_work_experience(self):
        """获取工作经历"""
        if self.work_experience:
            return json.loads(self.work_experience)
        return []
    
    def set_skills(self, data):
        """设置技能清单"""
        self.skills = json.dumps(data, ensure_ascii=False)
    
    def get_skills(self):
        """获取技能清单"""
        if self.skills:
            return json.loads(self.skills)
        return []
    
    def set_projects(self, data):
        """设置项目经验"""
        self.projects = json.dumps(data, ensure_ascii=False)
    
    def get_projects(self):
        """获取项目经验"""
        if self.projects:
            return json.loads(self.projects)
        return []
    
    def set_certifications(self, data):
        """设置证书资质"""
        self.certifications = json.dumps(data, ensure_ascii=False)
    
    def get_certifications(self):
        """获取证书资质"""
        if self.certifications:
            return json.loads(self.certifications)
        return []
    
    def set_ai_skills_tags(self, data):
        """设置AI技能标签"""
        self.ai_skills_tags = json.dumps(data, ensure_ascii=False)
    
    def get_ai_skills_tags(self):
        """获取AI技能标签"""
        if self.ai_skills_tags:
            return json.loads(self.ai_skills_tags)
        return []
    
    def set_ai_positions(self, data):
        """设置AI推荐岗位"""
        self.ai_positions = json.dumps(data, ensure_ascii=False)
    
    def get_ai_positions(self):
        """获取AI推荐岗位"""
        if self.ai_positions:
            return json.loads(self.ai_positions)
        return []
    
    def set_ai_analysis(self, data):
        """设置AI综合分析"""
        self.ai_analysis = json.dumps(data, ensure_ascii=False)
    
    def get_ai_analysis(self):
        """获取AI综合分析"""
        if self.ai_analysis:
            return json.loads(self.ai_analysis)
        return {}
    
    def to_dict(self):
        """转换为字典"""
        import os
        
        # 构建文件访问URL
        file_url = None
        if self.file_path:
            # 处理文件路径，确保兼容不同的存储格式
            if os.path.isabs(self.file_path):
                # 绝对路径：提取相对于uploads目录的路径
                try:
                    # 标准化路径分隔符为正斜杠
                    normalized_path = self.file_path.replace('\\', '/')
                    
                    # 找到uploads目录在路径中的位置
                    uploads_index = normalized_path.find('uploads')
                    if uploads_index != -1:
                        # 提取从uploads开始的相对路径，跳过'uploads/'
                        relative_path = normalized_path[uploads_index + 8:]  # 8是'uploads/'的长度
                        file_url = f"/uploads/{relative_path}"
                    else:
                        # 如果没有找到uploads，使用文件名构建URL
                        filename = os.path.basename(self.file_path)
                        file_url = f"/uploads/{self.user_id}/{filename}"
                except Exception as e:
                    # 异常情况下使用文件名构建URL
                    filename = os.path.basename(self.file_path)
                    file_url = f"/uploads/{self.user_id}/{filename}"
            else:
                # 相对路径：直接使用，确保正斜杠格式
                normalized_path = self.file_path.replace('\\', '/')
                if normalized_path.startswith('uploads/'):
                    file_url = f"/{normalized_path}"
                else:
                    filename = os.path.basename(self.file_path)
                    file_url = f"/uploads/{self.user_id}/{filename}"
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'title': self.title,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'raw_text': self.raw_text,
            'personal_info': self.get_personal_info(),
            'education': self.get_education(),
            'work_experience': self.get_work_experience(),
            'skills': self.get_skills(),
            'projects': self.get_projects(),
            'certifications': self.get_certifications(),
            'ai_skills_tags': self.get_ai_skills_tags(),
            'ai_positions': self.get_ai_positions(),
            'ai_analysis': self.get_ai_analysis(),
            'status': self.status,
            'url': file_url,  # 添加文件访问URL
            'type': self.file_type,  # 添加文件类型
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Resume {self.name}>' 