#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试记录与评估ORM模型
"""

import json
from datetime import datetime
from . import db

class Interview(db.Model):
    """面试记录表"""
    
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    
    # 面试基本信息
    interview_type = db.Column(db.String(50), nullable=False)  # technical, behavioral, comprehensive, custom
    interview_mode = db.Column(db.String(50), default='technical')  # technical, pressure, case, comprehensive
    position = db.Column(db.String(200), nullable=True)  # 目标岗位
    company = db.Column(db.String(100), nullable=True)  # 目标公司
    difficulty_level = db.Column(db.String(20), default='middle')  # primary, middle, high
    question_count = db.Column(db.Integer, default=5)  # 问题数量
    time_limit = db.Column(db.Integer, nullable=True)  # 时间限制(分钟)
    duration = db.Column(db.Integer, nullable=True)  # 实际面试时长（秒）

    # 面试偏好设置
    interviewer_expression = db.Column(db.String(20), default='friendly')  # 面试官表情: friendly, serious, pressure
    interaction_mode = db.Column(db.String(20), default='frequent')  # 互动模式: frequent, listener, counter
    voice_speed = db.Column(db.Numeric(3, 1), default=1.0)  # 语音速度 (0.5-2.0)
    enable_emotion_feedback = db.Column(db.Boolean, default=True)  # 是否启用微表情反馈
    feedback_types = db.Column(db.JSON, default=lambda: ['nod'])  # 反馈类型: nod, frown, timer
    recording_type = db.Column(db.String(20), default='video')  # 录制类型: video, audio
    ai_highlight = db.Column(db.Boolean, default=True)  # AI高亮标记
    improvement_marking = db.Column(db.Boolean, default=True)  # 改进点标记
    background_noises = db.Column(db.JSON, default=lambda: [])  # 背景噪音设置

    # 面试状态
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled, paused
    total_questions = db.Column(db.Integer, default=0)  # 总问题数
    answered_questions = db.Column(db.Integer, default=0)  # 已回答问题数

    # 面试数据（JSON格式存储）
    questions_data = db.Column(db.JSON, nullable=True)  # 面试问题数据
    transcriptions_data = db.Column(db.JSON, nullable=True)  # 语音转写数据
    ai_evaluations_data = db.Column(db.JSON, nullable=True)  # AI评估数据
    real_time_feedback_data = db.Column(db.JSON, nullable=True)  # 实时反馈数据
    interview_config = db.Column(db.JSON, nullable=True)  # 面试配置（存储偏好设置）
    interview_config = db.Column(db.JSON, nullable=True)  # 面试配置

    # 评分数据
    overall_score = db.Column(db.Numeric(5, 2), nullable=True)  # 综合评分
    technical_score = db.Column(db.Numeric(5, 2), nullable=True)  # 技术能力评分
    expression_logic_score = db.Column(db.Numeric(5, 2), nullable=True)  # 表达逻辑评分
    adaptability_score = db.Column(db.Numeric(5, 2), nullable=True)  # 应变能力评分
    behavior_etiquette_score = db.Column(db.Numeric(5, 2), nullable=True)  # 行为礼仪评分
    english_communication_score = db.Column(db.Numeric(5, 2), nullable=True)  # 英语沟通评分
    cultural_fit_score = db.Column(db.Numeric(5, 2), nullable=True)  # 文化匹配评分

    # 报告数据
    report_data = db.Column(db.JSON, nullable=True)  # 面试报告数据
    
    # 时间戳
    scheduled_at = db.Column(db.DateTime, nullable=True)  # 计划时间
    started_at = db.Column(db.DateTime, nullable=True)  # 开始时间
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_questions_data(self):
        """获取面试问题数据"""
        return self.questions_data or []

    def set_questions_data(self, data):
        """设置面试问题数据"""
        self.questions_data = data

    def get_transcriptions_data(self):
        """获取语音转写数据"""
        return self.transcriptions_data or []

    def set_transcriptions_data(self, data):
        """设置语音转写数据"""
        self.transcriptions_data = data

    def get_ai_evaluations_data(self):
        """获取AI评估数据"""
        return self.ai_evaluations_data or []

    def set_ai_evaluations_data(self, data):
        """设置AI评估数据"""
        self.ai_evaluations_data = data

    def get_real_time_feedback_data(self):
        """获取实时反馈数据"""
        return self.real_time_feedback_data or []

    def set_real_time_feedback_data(self, data):
        """设置实时反馈数据"""
        self.real_time_feedback_data = data

    def get_interview_config(self):
        """获取面试配置"""
        return self.interview_config or {}

    def set_interview_config(self, config):
        """设置面试配置"""
        self.interview_config = config

    def get_report_data(self):
        """获取面试报告数据"""
        return self.report_data or {}

    def set_report_data(self, data):
        """设置面试报告数据"""
        self.report_data = data
    
    def start_interview(self):
        """开始面试"""
        self.status = 'in_progress'
        self.started_at = datetime.utcnow()

    def complete_interview(self):
        """完成面试"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration = int((self.completed_at - self.started_at).total_seconds())

    def pause_interview(self):
        """暂停面试"""
        self.status = 'paused'

    def resume_interview(self):
        """恢复面试"""
        self.status = 'in_progress'

    def cancel_interview(self):
        """取消面试"""
        self.status = 'cancelled'

    def add_question(self, question_data):
        """添加面试问题"""
        questions = self.get_questions_data()
        questions.append(question_data)
        self.set_questions_data(questions)
        self.total_questions = len(questions)

    def add_transcription(self, transcription_data):
        """添加语音转写记录"""
        transcriptions = self.get_transcriptions_data()
        transcriptions.append(transcription_data)
        self.set_transcriptions_data(transcriptions)

    def add_ai_evaluation(self, evaluation_data):
        """添加AI评估记录"""
        evaluations = self.get_ai_evaluations_data()
        evaluations.append(evaluation_data)
        self.set_ai_evaluations_data(evaluations)

    def add_real_time_feedback(self, feedback_data):
        """添加实时反馈记录"""
        feedbacks = self.get_real_time_feedback_data()
        feedbacks.append(feedback_data)
        self.set_real_time_feedback_data(feedbacks)

    def get_interview_preferences(self):
        """获取面试偏好设置"""
        return {
            'interviewer_expression': self.interviewer_expression,
            'interaction_mode': self.interaction_mode,
            'voice_speed': self.voice_speed,
            'enable_emotion_feedback': self.enable_emotion_feedback,
            'feedback_types': self.feedback_types or ['nod'],
            'recording_type': self.recording_type,
            'ai_highlight': self.ai_highlight,
            'improvement_marking': self.improvement_marking,
            'background_noises': self.background_noises or []
        }

    def set_interview_preferences(self, preferences):
        """设置面试偏好"""
        self.interviewer_expression = preferences.get('interviewer_expression', 'friendly')
        self.interaction_mode = preferences.get('interaction_mode', 'frequent')
        self.voice_speed = preferences.get('voice_speed', 1.0)
        self.enable_emotion_feedback = preferences.get('enable_emotion_feedback', True)
        self.feedback_types = preferences.get('feedback_types', ['nod'])
        self.recording_type = preferences.get('recording_type', 'video')
        self.ai_highlight = preferences.get('ai_highlight', True)
        self.improvement_marking = preferences.get('improvement_marking', True)
        self.background_noises = preferences.get('background_noises', [])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'interview_type': self.interview_type,
            'interview_mode': self.interview_mode,
            'position': self.position,
            'company': self.company,
            'difficulty_level': self.difficulty_level,
            'question_count': self.question_count,
            'time_limit': self.time_limit,
            'duration': self.duration,
            'status': self.status,
            'total_questions': self.total_questions,
            'answered_questions': self.answered_questions,
            # 面试偏好设置
            'interview_preferences': self.get_interview_preferences(),
            'questions_data': self.get_questions_data(),
            'transcriptions_data': self.get_transcriptions_data(),
            'ai_evaluations_data': self.get_ai_evaluations_data(),
            'real_time_feedback_data': self.get_real_time_feedback_data(),
            'interview_config': self.get_interview_config(),
            'overall_score': float(self.overall_score) if self.overall_score else None,
            'technical_score': float(self.technical_score) if self.technical_score else None,
            'expression_logic_score': float(self.expression_logic_score) if self.expression_logic_score else None,
            'adaptability_score': float(self.adaptability_score) if self.adaptability_score else None,
            'behavior_etiquette_score': float(self.behavior_etiquette_score) if self.behavior_etiquette_score else None,
            'english_communication_score': float(self.english_communication_score) if self.english_communication_score else None,
            'cultural_fit_score': float(self.cultural_fit_score) if self.cultural_fit_score else None,
            'report_data': self.get_report_data(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Interview {self.id}>'


