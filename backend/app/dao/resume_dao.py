#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历数据访问对象
"""

from typing import Optional, List, Dict, Any
from app.models import db
from app.models.resume import Resume
from loguru import logger


class ResumeDAO:
    """简历数据访问对象"""
    
    @staticmethod
    def create_resume(user_id: int, name: str, original_filename: str, 
                     file_path: str, file_type: str, file_size: int = None) -> Optional[Resume]:
        """创建简历记录"""
        try:
            resume = Resume(
                user_id=user_id,
                name=name,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size
            )
            db.session.add(resume)
            db.session.commit()
            return resume
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建简历记录失败: {e}")
            return None
    
    @staticmethod
    def get_resume_by_id(resume_id: int) -> Optional[Resume]:
        """根据ID获取简历"""
        return Resume.query.get(resume_id)
    
    @staticmethod
    def get_resume_by_user_id(user_id: int, resume_id: int) -> Optional[Resume]:
        """根据用户ID和简历ID获取简历"""
        return Resume.query.filter_by(user_id=user_id, id=resume_id).first()
    
    @staticmethod
    def get_user_resumes(user_id: int) -> List[Resume]:
        """获取用户的所有简历"""
        return Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    
    @staticmethod
    def update_resume_status(resume_id: int, status: str) -> bool:
        """更新简历状态"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.status = status
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历状态失败: {e}")
            return False
    
    @staticmethod
    def update_resume_raw_text(resume_id: int, raw_text: str) -> bool:
        """更新简历原始文本"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.raw_text = raw_text
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历原始文本失败: {e}")
            return False
    
    @staticmethod
    def update_resume_personal_info(resume_id: int, personal_info: Dict[str, Any]) -> bool:
        """更新简历个人信息"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_personal_info(personal_info)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历个人信息失败: {e}")
            return False
    
    @staticmethod
    def update_resume_education(resume_id: int, education: List[Dict[str, Any]]) -> bool:
        """更新简历教育经历"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_education(education)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历教育经历失败: {e}")
            return False
    
    @staticmethod
    def update_resume_work_experience(resume_id: int, work_experience: List[Dict[str, Any]]) -> bool:
        """更新简历工作经历"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_work_experience(work_experience)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历工作经历失败: {e}")
            return False
    
    @staticmethod
    def update_resume_skills(resume_id: int, skills: List[Dict[str, Any]]) -> bool:
        """更新简历技能清单"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_skills(skills)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历技能清单失败: {e}")
            return False
    
    @staticmethod
    def update_resume_projects(resume_id: int, projects: List[Dict[str, Any]]) -> bool:
        """更新简历项目经验"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_projects(projects)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历项目经验失败: {e}")
            return False
    
    @staticmethod
    def update_resume_certifications(resume_id: int, certifications: List[Dict[str, Any]]) -> bool:
        """更新简历证书资质"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_certifications(certifications)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历证书资质失败: {e}")
            return False
    
    @staticmethod
    def update_resume_ai_analysis(resume_id: int, ai_analysis: Dict[str, Any]) -> bool:
        """更新简历AI分析结果"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_ai_analysis(ai_analysis)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历AI分析结果失败: {e}")
            return False
    
    @staticmethod
    def update_resume_ai_skills_tags(resume_id: int, skills_tags: List[str]) -> bool:
        """更新简历AI技能标签"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_ai_skills_tags(skills_tags)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历AI技能标签失败: {e}")
            return False
    
    @staticmethod
    def update_resume_ai_positions(resume_id: int, positions: List[str]) -> bool:
        """更新简历AI推荐岗位"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.set_ai_positions(positions)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历AI推荐岗位失败: {e}")
            return False
    
    @staticmethod
    def delete_resume(resume_id: int) -> bool:
        """删除简历"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            db.session.delete(resume)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除简历失败: {e}")
            return False
    
    @staticmethod
    def get_resume_count_by_user(user_id: int) -> int:
        """获取用户的简历数量"""
        return Resume.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_processing_resumes() -> List[Resume]:
        """获取所有处理中的简历"""
        return Resume.query.filter_by(status='processing').all()
    
    @staticmethod
    def get_completed_resumes_by_user(user_id: int) -> List[Resume]:
        """获取用户已完成的简历"""
        return Resume.query.filter_by(user_id=user_id, status='completed').all()
    
    @staticmethod
    def get_processing_resumes_by_user(user_id: int) -> List[Resume]:
        """获取用户处理中的简历"""
        return Resume.query.filter_by(user_id=user_id, status='processing').all()
    
    @staticmethod
    def update_resume_name(resume_id: int, new_name: str) -> bool:
        """更新简历名称"""
        try:
            resume = ResumeDAO.get_resume_by_id(resume_id)
            if not resume:
                return False
            
            resume.name = new_name
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新简历名称失败: {e}")
            return False 