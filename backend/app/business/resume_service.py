#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历业务逻辑服务
"""

import os
from typing import Optional, Dict, Any, Tuple, List
from app.dao.resume_dao import ResumeDAO
from app.dao.user_dao import UserDAO
from app.models.resume import Resume
from app.models import db
from app.services.resume_service import ResumeService
from loguru import logger


class ResumeBusinessService:
    """简历业务逻辑服务"""
    
    def __init__(self):
        self.resume_service = ResumeService()
    
    def upload_resume(self, user_id: int, file, resume_name: str = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        上传简历业务逻辑
        
        Returns:
            (是否成功, 消息, 简历信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 验证文件
            if not file or not file.filename:
                return False, "没有选择文件", None
            
            # 3. 保存文件
            success, file_path, error_msg = self.resume_service.save_uploaded_file(file, user_id)
            if not success:
                return False, error_msg, None
            
            # 4. 创建简历记录
            original_filename = file.filename
            file_type = original_filename.rsplit('.', 1)[1].lower()
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
            
            # 使用文件名作为简历名称（如果没有提供）
            if not resume_name:
                resume_name = original_filename.rsplit('.', 1)[0]
            
            resume = ResumeDAO.create_resume(
                user_id=user_id,
                name=resume_name,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size
            )
            
            if not resume:
                return False, "创建简历记录失败", None
            
            # 5. 异步处理简历解析（这里只是创建记录，实际解析在后台进行）
            # TODO: 启动后台任务进行简历解析
            
            return True, "简历上传成功", {
                'id': resume.id,
                'name': resume.name,
                'original_filename': resume.original_filename,
                'file_type': resume.file_type,
                'file_size': resume.file_size,
                'status': resume.status,
                'created_at': resume.created_at.isoformat() if resume.created_at else None
            }
            
        except Exception as e:
            logger.error(f"上传简历失败: {e}")
            return False, "上传失败，请稍后重试", None
    
    def get_user_resumes(self, user_id: int) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        获取用户简历列表业务逻辑
        
        Returns:
            (是否成功, 消息, 简历列表)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取简历列表
            resumes = ResumeDAO.get_user_resumes(user_id)
            
            # 3. 构建响应数据
            resume_list = []
            for resume in resumes:
                resume_data = {
                    'id': resume.id,
                    'name': resume.name,
                    'title': resume.title,
                    'original_filename': resume.original_filename,
                    'file_type': resume.file_type,
                    'file_size': resume.file_size,
                    'status': resume.status,
                    'created_at': resume.created_at.isoformat() if resume.created_at else None,
                    'updated_at': resume.updated_at.isoformat() if resume.updated_at else None
                }
                resume_list.append(resume_data)
            
            return True, "获取成功", resume_list
            
        except Exception as e:
            logger.error(f"获取用户简历列表失败: {e}")
            return False, "获取失败", None
    
    def get_resume_detail(self, user_id: int, resume_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取简历详情业务逻辑
        
        Returns:
            (是否成功, 消息, 简历详情)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取简历
            resume = ResumeDAO.get_resume_by_user_id(user_id, resume_id)
            if not resume:
                return False, "简历不存在", None
            
            # 3. 构建简历详情
            resume_detail = {
                'id': resume.id,
                'name': resume.name,
                'title': resume.title,
                'original_filename': resume.original_filename,
                'file_type': resume.file_type,
                'file_size': resume.file_size,
                'status': resume.status,
                'raw_text': resume.raw_text,
                'personal_info': resume.get_personal_info(),
                'education': resume.get_education(),
                'work_experience': resume.get_work_experience(),
                'skills': resume.get_skills(),
                'projects': resume.get_projects(),
                'certifications': resume.get_certifications(),
                'ai_skills_tags': resume.get_ai_skills_tags(),
                'ai_positions': resume.get_ai_positions(),
                'ai_analysis': resume.get_ai_analysis(),
                'created_at': resume.created_at.isoformat() if resume.created_at else None,
                'updated_at': resume.updated_at.isoformat() if resume.updated_at else None
            }
            
            return True, "获取成功", resume_detail
            
        except Exception as e:
            logger.error(f"获取简历详情失败: {e}")
            return False, "获取失败", None
    
    def delete_resume(self, user_id: int, resume_id: int) -> Tuple[bool, str]:
        """
        删除简历业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证简历
            resume = ResumeDAO.get_resume_by_user_id(user_id, resume_id)
            if not resume:
                return False, "简历不存在"
            
            # 3. 删除文件
            if os.path.exists(resume.file_path):
                try:
                    os.remove(resume.file_path)
                except Exception as e:
                    logger.warning(f"删除简历文件失败: {e}")
            
            # 4. 删除数据库记录
            success = ResumeDAO.delete_resume(resume_id)
            if not success:
                return False, "删除简历失败"
            
            return True, "删除成功"
            
        except Exception as e:
            logger.error(f"删除简历失败: {e}")
            return False, "删除失败，请稍后重试"
    
    def update_resume_name(self, user_id: int, resume_id: int, new_name: str) -> Tuple[bool, str]:
        """
        更新简历名称业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证简历
            resume = ResumeDAO.get_resume_by_user_id(user_id, resume_id)
            if not resume:
                return False, "简历不存在"
            
            # 3. 验证新名称
            if not new_name or len(new_name.strip()) == 0:
                return False, "简历名称不能为空"
            
            if len(new_name) > 100:
                return False, "简历名称长度不能超过100个字符"
            
            # 4. 更新名称
            resume.name = new_name.strip()
            success = ResumeDAO.update_resume_name(resume_id, new_name.strip())
            
            if success:
                return True, "更新成功"
            else:
                return False, "更新失败"
            
        except Exception as e:
            logger.error(f"更新简历名称失败: {e}")
            return False, "更新失败，请稍后重试"
    
    def get_resume_statistics(self, user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取简历统计信息业务逻辑
        
        Returns:
            (是否成功, 消息, 统计信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取统计数据
            total_count = ResumeDAO.get_resume_count_by_user(user_id)
            completed_count = len(ResumeDAO.get_completed_resumes_by_user(user_id))
            processing_count = len(ResumeDAO.get_processing_resumes_by_user(user_id))
            
            statistics = {
                'total_count': total_count,
                'completed_count': completed_count,
                'processing_count': processing_count,
                'completion_rate': (completed_count / total_count * 100) if total_count > 0 else 0
            }
            
            return True, "获取成功", statistics
            
        except Exception as e:
            logger.error(f"获取简历统计信息失败: {e}")
            return False, "获取失败", None 