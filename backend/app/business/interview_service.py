#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试业务逻辑服务
"""

from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
from app.dao.interview_dao import InterviewDAO
from app.dao.user_dao import UserDAO
from app.dao.resume_dao import ResumeDAO
from app.models.interview import Interview
from app.services.spark_service import SparkService
from loguru import logger


class InterviewService:
    """面试业务逻辑服务"""
    
    def __init__(self):
        self.spark_service = SparkService()
    
    def create_interview(self, user_id: int, interview_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        创建面试业务逻辑
        
        Returns:
            (是否成功, 消息, 面试信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 验证面试数据
            interview_type = interview_data.get('interview_type')
            position = interview_data.get('position')
            company = interview_data.get('company')
            resume_id = interview_data.get('resume_id')
            
            if not interview_type:
                return False, "面试类型不能为空", None
            
            # 3. 验证简历（如果提供了简历ID）
            if resume_id:
                resume = ResumeDAO.get_resume_by_user_id(user_id, resume_id)
                if not resume:
                    return False, "简历不存在", None
            
            # 4. 创建面试记录
            interview = InterviewDAO.create_interview(
                user_id=user_id,
                interview_type=interview_type,
                position=position,
                company=company,
                resume_id=resume_id
            )
            
            if not interview:
                return False, "创建面试记录失败", None
            
            # 5. 设置面试偏好（如果有）
            if 'interview_preferences' in interview_data:
                InterviewDAO.update_interview_preferences(interview.id, interview_data['interview_preferences'])
            
            return True, "面试创建成功", {
                'id': interview.id,
                'interview_type': interview.interview_type,
                'position': interview.position,
                'company': interview.company,
                'status': interview.status,
                'created_at': interview.created_at.isoformat() if interview.created_at else None
            }
            
        except Exception as e:
            logger.error(f"创建面试失败: {e}")
            return False, "创建失败，请稍后重试", None
    
    def get_user_interviews(self, user_id: int) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        获取用户面试列表业务逻辑
        
        Returns:
            (是否成功, 消息, 面试列表)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取面试列表
            interviews = InterviewDAO.get_user_interviews(user_id)
            
            # 3. 构建响应数据
            interview_list = []
            for interview in interviews:
                interview_data = {
                    'id': interview.id,
                    'interview_type': interview.interview_type,
                    'interview_mode': interview.interview_mode,
                    'position': interview.position,
                    'company': interview.company,
                    'difficulty_level': interview.difficulty_level,
                    'status': interview.status,
                    'total_questions': interview.total_questions,
                    'answered_questions': interview.answered_questions,
                    'overall_score': float(interview.overall_score) if interview.overall_score else None,
                    'created_at': interview.created_at.isoformat() if interview.created_at else None,
                    'started_at': interview.started_at.isoformat() if interview.started_at else None,
                    'completed_at': interview.completed_at.isoformat() if interview.completed_at else None
                }
                interview_list.append(interview_data)
            
            return True, "获取成功", interview_list
            
        except Exception as e:
            logger.error(f"获取用户面试列表失败: {e}")
            return False, "获取失败", None
    
    def get_interview_detail(self, user_id: int, interview_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取面试详情业务逻辑
        
        Returns:
            (是否成功, 消息, 面试详情)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取面试
            interview = InterviewDAO.get_interview_by_user_id(user_id, interview_id)
            if not interview:
                return False, "面试不存在", None
            
            # 3. 构建面试详情
            interview_detail = {
                'id': interview.id,
                'interview_type': interview.interview_type,
                'interview_mode': interview.interview_mode,
                'position': interview.position,
                'company': interview.company,
                'difficulty_level': interview.difficulty_level,
                'question_count': interview.question_count,
                'time_limit': interview.time_limit,
                'duration': interview.duration,
                'status': interview.status,
                'total_questions': interview.total_questions,
                'answered_questions': interview.answered_questions,
                'overall_score': float(interview.overall_score) if interview.overall_score else None,
                'technical_score': float(interview.technical_score) if interview.technical_score else None,
                'expression_logic_score': float(interview.expression_logic_score) if interview.expression_logic_score else None,
                'adaptability_score': float(interview.adaptability_score) if interview.adaptability_score else None,
                'behavior_etiquette_score': float(interview.behavior_etiquette_score) if interview.behavior_etiquette_score else None,
                'english_communication_score': float(interview.english_communication_score) if interview.english_communication_score else None,
                'cultural_fit_score': float(interview.cultural_fit_score) if interview.cultural_fit_score else None,
                'questions_data': interview.get_questions_data(),
                'transcriptions_data': interview.get_transcriptions_data(),
                'ai_evaluations_data': interview.get_ai_evaluations_data(),
                'real_time_feedback_data': interview.get_real_time_feedback_data(),
                'interview_config': interview.get_interview_config(),
                'report_data': interview.get_report_data(),
                'created_at': interview.created_at.isoformat() if interview.created_at else None,
                'started_at': interview.started_at.isoformat() if interview.started_at else None,
                'completed_at': interview.completed_at.isoformat() if interview.completed_at else None
            }
            
            return True, "获取成功", interview_detail
            
        except Exception as e:
            logger.error(f"获取面试详情失败: {e}")
            return False, "获取失败", None
    
    def start_interview(self, user_id: int, interview_id: int) -> Tuple[bool, str]:
        """
        开始面试业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证面试
            interview = InterviewDAO.get_interview_by_user_id(user_id, interview_id)
            if not interview:
                return False, "面试不存在"
            
            # 3. 检查面试状态
            if interview.status != 'scheduled':
                return False, "面试状态不正确，无法开始"
            
            # 4. 更新面试状态
            success = InterviewDAO.update_interview_status(interview_id, 'in_progress')
            if not success:
                return False, "开始面试失败"
            
            return True, "面试已开始"
            
        except Exception as e:
            logger.error(f"开始面试失败: {e}")
            return False, "开始失败，请稍后重试"
    
    def complete_interview(self, user_id: int, interview_id: int) -> Tuple[bool, str]:
        """
        完成面试业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证面试
            interview = InterviewDAO.get_interview_by_user_id(user_id, interview_id)
            if not interview:
                return False, "面试不存在"
            
            # 3. 检查面试状态
            if interview.status != 'in_progress':
                return False, "面试状态不正确，无法完成"
            
            # 4. 更新面试状态
            success = InterviewDAO.update_interview_status(interview_id, 'completed')
            if not success:
                return False, "完成面试失败"
            
            return True, "面试已完成"
            
        except Exception as e:
            logger.error(f"完成面试失败: {e}")
            return False, "完成失败，请稍后重试"
    
    def delete_interview(self, user_id: int, interview_id: int) -> Tuple[bool, str]:
        """
        删除面试业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证面试
            interview = InterviewDAO.get_interview_by_user_id(user_id, interview_id)
            if not interview:
                return False, "面试不存在"
            
            # 3. 删除面试
            success = InterviewDAO.delete_interview(interview_id)
            if not success:
                return False, "删除面试失败"
            
            return True, "删除成功"
            
        except Exception as e:
            logger.error(f"删除面试失败: {e}")
            return False, "删除失败，请稍后重试"
    
    def get_next_question(self, user_id: int, interview_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取下一个问题业务逻辑
        
        Returns:
            (是否成功, 消息, 问题数据)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 验证面试
            interview = InterviewDAO.get_interview_by_user_id(user_id, interview_id)
            if not interview:
                return False, "面试不存在", None
            
            # 3. 检查面试状态
            if interview.status != 'in_progress':
                return False, "面试状态不正确，无法获取问题", None
            
            # 4. 调用AI服务生成问题
            # TODO: 这里需要调用AI服务来生成问题
            # 暂时返回模拟数据
            question_data = {
                'question_id': 1,
                'question': '请介绍一下你的技术背景和经验',
                'type': 'technical',
                'time_limit': 120,
                'hints': ['可以从学习经历开始', '重点介绍相关项目经验']
            }
            
            return True, "获取问题成功", question_data
            
        except Exception as e:
            logger.error(f"获取下一个问题失败: {e}")
            return False, "获取失败，请稍后重试", None
    
    def get_interview_statistics(self, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取面试统计信息业务逻辑
        
        Returns:
            (是否成功, 消息, 统计信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取统计数据
            total_count = InterviewDAO.get_interview_count_by_user(user_id)
            completed_count = InterviewDAO.get_completed_interview_count_by_user(user_id)
            in_progress_interviews = InterviewDAO.get_user_in_progress_interviews(user_id)
            
            # 3. 计算平均分
            completed_interviews = InterviewDAO.get_user_completed_interviews(user_id)
            total_score = 0
            scored_count = 0
            
            for interview in completed_interviews:
                if interview.overall_score:
                    total_score += float(interview.overall_score)
                    scored_count += 1
            
            average_score = (total_score / scored_count) if scored_count > 0 else 0
            
            statistics = {
                'total_count': total_count,
                'completed_count': completed_count,
                'in_progress_count': len(in_progress_interviews),
                'completion_rate': (completed_count / total_count * 100) if total_count > 0 else 0,
                'average_score': round(average_score, 2)
            }
            
            return True, "获取成功", statistics
            
        except Exception as e:
            logger.error(f"获取面试统计信息失败: {e}")
            return False, "获取失败", None 