#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户信息ORM模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    """用户信息表"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    
    # 个人信息字段
    name = db.Column(db.String(100), nullable=True)  # 真实姓名
    gender = db.Column(db.String(10), nullable=True)  # 性别：male/female
    birth_date = db.Column(db.Date, nullable=True)  # 出生日期
    contact = db.Column(db.String(100), nullable=True)  # 微信/QQ等联系方式
    
    # 扩展信息字段（使用JSON存储）
    education_info = db.Column(db.JSON, nullable=True)  # 教育背景信息
    skills = db.Column(db.JSON, nullable=True)  # 技能信息
    job_preferences = db.Column(db.JSON, nullable=True)  # 求职偏好设置
    interview_preferences = db.Column(db.JSON, nullable=True)  # 面试偏好设置
    privacy_settings = db.Column(db.JSON, nullable=True)  # 隐私设置

    # 职业方向设置
    target_field = db.Column(db.String(50), default='ai')  # 目标领域: ai, big_data, iot
    target_positions = db.Column(db.JSON, nullable=True)  # 目标岗位方向列表（最多3个）
    target_companies = db.Column(db.JSON, nullable=True)  # 目标企业列表（最多15个）
    work_location = db.Column(db.String(100), nullable=True)  # 工作地点
    company_size = db.Column(db.String(50), nullable=True)  # 公司规模
    work_experience = db.Column(db.String(50), nullable=True)  # 工作经验
    
    # 用户状态
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # 账户删除相关
    deleted_at = db.Column(db.DateTime, nullable=True)
    delete_reason = db.Column(db.String(255), nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关联关系
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = password
    
    def check_password(self, password):
        """验证密码"""
        return self.password_hash == password
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'contact': self.contact,
            'education_info': self.education_info,
            'skills': self.skills,
            'job_preferences': self.job_preferences,
            'interview_preferences': self.interview_preferences,
            'privacy_settings': self.privacy_settings,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def get_basic_info(self):
        """获取基础信息"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'name': self.name,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def get_profile_completeness(self):
        """计算资料完整度"""
        total_fields = 0
        completed_fields = 0
        
        # 检查基础信息
        basic_fields = [self.name, self.gender, self.phone, self.email, self.contact, self.avatar]
        total_fields += len(basic_fields)
        completed_fields += sum(1 for field in basic_fields if field)
        
        # 检查教育信息
        total_fields += 3  # school, college, major
        if self.education_info:
            education_fields = ['school', 'college', 'major']
            completed_fields += sum(1 for field in education_fields if self.education_info.get(field))
        
        # 检查技能信息
        total_fields += 1
        if self.skills and len(self.skills) > 0:
            completed_fields += 1
        
        return int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    
    def is_profile_complete(self):
        """检查资料是否完整"""
        required_fields = [self.name, self.email, self.phone]
        return all(field for field in required_fields)
    
    def get_job_preferences(self):
        """获取求职偏好设置"""
        if self.job_preferences:
            return self.job_preferences
        return {
            'selected_field': '',
            'selected_directions': [],
            'selected_companies': [],
            'selected_city': '',
            'selected_company_size': '',
            'selected_experience': '',
            'target_position': '',
            'target_industries': [],
            'expected_salary_min': None,
            'expected_salary_max': None,
            'work_type': '',
            'work_locations': [],
            'availability': ''
        }

    def set_job_preferences(self, preferences):
        """设置求职偏好"""
        self.job_preferences = preferences

    def get_interview_preferences(self):
        """获取面试偏好设置 - 支持新的结构化配置"""
        if self.interview_preferences:
            # 检查是否是新的结构化配置
            if isinstance(self.interview_preferences, dict) and 'avatar_config' in self.interview_preferences:
                return self.interview_preferences
            else:
                # 兼容旧的扁平结构
                return self.interview_preferences

        # 返回默认的结构化配置
        return {
            'avatar_config': {
                'avatar_style': 0,
                'avatar_gender': 'neutral',
                'avatar_age_range': 'middle'
            },
            'interaction_config': {
                'interaction_mode': 'frequent',
                'question_frequency': 2.0,
                'follow_up_probability': 0.3
            },
            'expression_config': {
                'enabled_expressions': ['nod'],
                'expression_intensity': 0.7,
                'expression_frequency': 0.5
            },
            'voice_config': {
                'voice_speed': 1.0,
                'voice_pitch': 1.0,
                'voice_volume': 0.8,
                'voice_style': 'professional'
            },
            'recording_config': {
                'recording_type': 'video',
                'auto_recording': True,
                'recording_quality': 'medium',
                'ai_highlight': True,
                'improvement_marking': True,
                'auto_summary': True
            },
            'noise_config': {
                'enabled_noises': [],
                'noise_volume': 0.3,
                'noise_frequency': 0.2,
                'custom_noise_url': ''
            },
            'advanced_config': {
                'ai_model': 'spark',
                'response_delay': 1000,
                'context_memory': 5,
                'difficulty_adaptation': True
            },
            'metadata': {
                'version': '1.0.0'
            }
        }

    def set_interview_preferences(self, preferences):
        """设置面试偏好"""
        self.interview_preferences = preferences

    def get_privacy_settings(self):
        """获取隐私设置"""
        if self.privacy_settings:
            return self.privacy_settings
        return {
            'profile_visibility': 'private',
            'resume_visibility': 'private',
            'allow_contact': True,
            'show_online_status': True,
            'email_notifications': True,
            'sms_notifications': False,
            'interview_reminders': True,
            'data_retention_days': 365,
            'auto_delete_interviews': False,
            'data_sharing': False,
            'allow_recommendations': True
        }

    def set_privacy_settings(self, settings):
        """设置隐私设置"""
        self.privacy_settings = settings

    def get_career_preferences(self):
        """获取职业偏好设置"""
        return {
            'target_field': self.target_field or 'ai',
            'target_positions': self.target_positions or [],
            'target_companies': self.target_companies or [],
            'work_location': self.work_location or '',
            'company_size': self.company_size or '',
            'work_experience': self.work_experience or ''
        }

    def set_career_preferences(self, preferences):
        """设置职业偏好"""
        self.target_field = preferences.get('target_field', 'ai')

        # 目标岗位（最多3个）
        target_positions = preferences.get('target_positions', [])
        self.target_positions = target_positions[:3] if target_positions else []

        # 目标企业（最多15个）
        target_companies = preferences.get('target_companies', [])
        self.target_companies = target_companies[:15] if target_companies else []

        # 其他偏好设置
        self.work_location = preferences.get('work_location', '')
        self.company_size = preferences.get('company_size', '')
        self.work_experience = preferences.get('work_experience', '')

    def __repr__(self):
        return f'<User {self.username}>'