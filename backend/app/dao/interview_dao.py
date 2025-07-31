#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试数据访问对象
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import db
from app.models.interview import Interview
from loguru import logger


class InterviewDAO:
    """面试数据访问对象"""
    
    @staticmethod
    def create_interview(user_id: int, interview_type: str, position: str = None, 
                        company: str = None, resume_id: int = None) -> Optional[Interview]:
        """创建面试记录"""
        try:
            interview = Interview(
                user_id=user_id,
                interview_type=interview_type,
                position=position,
                company=company,
                resume_id=resume_id
            )
            db.session.add(interview)
            db.session.commit()
            return interview
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建面试记录失败: {e}")
            return None
    
    @staticmethod
    def get_interview_by_id(interview_id: int) -> Optional[Interview]:
        """根据ID获取面试"""
        return Interview.query.get(interview_id)
    
    @staticmethod
    def get_interview_by_user_id(user_id: int, interview_id: int) -> Optional[Interview]:
        """根据用户ID和面试ID获取面试"""
        return Interview.query.filter_by(user_id=user_id, id=interview_id).first()
    
    @staticmethod
    def get_user_interviews(user_id: int) -> List[Interview]:
        """获取用户的所有面试"""
        return Interview.query.filter_by(user_id=user_id).order_by(Interview.created_at.desc()).all()
    
    @staticmethod
    def get_user_completed_interviews(user_id: int) -> List[Interview]:
        """获取用户已完成的面试"""
        return Interview.query.filter_by(user_id=user_id, status='completed').all()
    
    @staticmethod
    def get_user_in_progress_interviews(user_id: int) -> List[Interview]:
        """获取用户进行中的面试"""
        return Interview.query.filter_by(user_id=user_id, status='in_progress').all()
    
    @staticmethod
    def update_interview_status(interview_id: int, status: str) -> bool:
        """更新面试状态"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.status = status
            
            # 根据状态更新时间戳
            if status == 'in_progress' and not interview.started_at:
                interview.started_at = datetime.utcnow()
            elif status == 'completed':
                interview.completed_at = datetime.utcnow()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试状态失败: {e}")
            return False
    
    @staticmethod
    def update_interview_config(interview_id: int, config: Dict[str, Any]) -> bool:
        """更新面试配置"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_interview_config(config)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试配置失败: {e}")
            return False
    
    @staticmethod
    def update_interview_preferences(interview_id: int, preferences: Dict[str, Any]) -> bool:
        """更新面试偏好设置"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_interview_preferences(preferences)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试偏好设置失败: {e}")
            return False
    
    @staticmethod
    def update_interview_questions_data(interview_id: int, questions_data: List[Dict[str, Any]]) -> bool:
        """更新面试问题数据"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_questions_data(questions_data)
            interview.total_questions = len(questions_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试问题数据失败: {e}")
            return False
    
    @staticmethod
    def add_interview_question(interview_id: int, question_data: Dict[str, Any]) -> bool:
        """添加面试问题"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.add_question(question_data)
            interview.total_questions += 1
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加面试问题失败: {e}")
            return False
    
    @staticmethod
    def update_interview_transcriptions_data(interview_id: int, transcriptions_data: List[Dict[str, Any]]) -> bool:
        """更新面试语音转写数据"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_transcriptions_data(transcriptions_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试语音转写数据失败: {e}")
            return False
    
    @staticmethod
    def add_interview_transcription(interview_id: int, transcription_data: Dict[str, Any]) -> bool:
        """添加面试语音转写"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.add_transcription(transcription_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加面试语音转写失败: {e}")
            return False
    
    @staticmethod
    def update_interview_ai_evaluations_data(interview_id: int, evaluations_data: List[Dict[str, Any]]) -> bool:
        """更新面试AI评估数据"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_ai_evaluations_data(evaluations_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试AI评估数据失败: {e}")
            return False
    
    @staticmethod
    def add_interview_ai_evaluation(interview_id: int, evaluation_data: Dict[str, Any]) -> bool:
        """添加面试AI评估"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.add_ai_evaluation(evaluation_data)
            interview.answered_questions += 1
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加面试AI评估失败: {e}")
            return False
    
    @staticmethod
    def update_interview_real_time_feedback_data(interview_id: int, feedback_data: List[Dict[str, Any]]) -> bool:
        """更新面试实时反馈数据"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_real_time_feedback_data(feedback_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试实时反馈数据失败: {e}")
            return False
    
    @staticmethod
    def add_interview_real_time_feedback(interview_id: int, feedback_data: Dict[str, Any]) -> bool:
        """添加面试实时反馈"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.add_real_time_feedback(feedback_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加面试实时反馈失败: {e}")
            return False
    
    @staticmethod
    def update_interview_scores(interview_id: int, scores: Dict[str, float]) -> bool:
        """更新面试评分"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            if 'overall_score' in scores:
                interview.overall_score = scores['overall_score']
            if 'technical_score' in scores:
                interview.technical_score = scores['technical_score']
            if 'expression_logic_score' in scores:
                interview.expression_logic_score = scores['expression_logic_score']
            if 'adaptability_score' in scores:
                interview.adaptability_score = scores['adaptability_score']
            if 'behavior_etiquette_score' in scores:
                interview.behavior_etiquette_score = scores['behavior_etiquette_score']
            if 'english_communication_score' in scores:
                interview.english_communication_score = scores['english_communication_score']
            if 'cultural_fit_score' in scores:
                interview.cultural_fit_score = scores['cultural_fit_score']
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试评分失败: {e}")
            return False
    
    @staticmethod
    def update_interview_report_data(interview_id: int, report_data: Dict[str, Any]) -> bool:
        """更新面试报告数据"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            interview.set_report_data(report_data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新面试报告数据失败: {e}")
            return False
    
    @staticmethod
    def delete_interview(interview_id: int) -> bool:
        """删除面试"""
        try:
            interview = InterviewDAO.get_interview_by_id(interview_id)
            if not interview:
                return False
            
            db.session.delete(interview)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除面试失败: {e}")
            return False
    
    @staticmethod
    def get_interview_count_by_user(user_id: int) -> int:
        """获取用户的面试数量"""
        return Interview.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_completed_interview_count_by_user(user_id: int) -> int:
        """获取用户已完成的面试数量"""
        return Interview.query.filter_by(user_id=user_id, status='completed').count()
    
    @staticmethod
    def get_interviews_by_resume_id(resume_id: int) -> List[Interview]:
        """根据简历ID获取面试"""
        return Interview.query.filter_by(resume_id=resume_id).all()
    
    @staticmethod
    def get_recent_interviews(limit: int = 10) -> List[Interview]:
        """获取最近的面试"""
        return Interview.query.order_by(Interview.created_at.desc()).limit(limit).all() 