#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据访问对象
"""

from typing import Optional, List, Dict, Any
from app.models import db
from app.models.user import User
from loguru import logger


class UserDAO:
    """用户数据访问对象"""
    
    @staticmethod
    def create_user(username: str, email: str, phone: str, password: str) -> Optional[User]:
        """创建用户"""
        try:
            user = User(username=username, email=email, phone=phone)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建用户失败: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.filter_by(id=user_id, deleted_at=None).first()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return User.query.filter_by(username=username, deleted_at=None).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email, deleted_at=None).first()
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return User.query.filter_by(phone=phone, deleted_at=None).first()
    
    @staticmethod
    def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> bool:
        """更新用户资料"""
        try:
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False
            
            # 更新基础信息
            if 'name' in profile_data:
                user.name = profile_data['name']
            if 'gender' in profile_data:
                user.gender = profile_data['gender']
            if 'birth_date' in profile_data:
                user.birth_date = profile_data['birth_date']
            if 'contact' in profile_data:
                user.contact = profile_data['contact']
            if 'avatar' in profile_data:
                user.avatar = profile_data['avatar']
            
            # 更新扩展信息
            if 'education_info' in profile_data:
                user.education_info = profile_data['education_info']
            if 'skills' in profile_data:
                user.skills = profile_data['skills']
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新用户资料失败: {e}")
            return False
    
    @staticmethod
    def update_user_preferences(user_id: int, preferences_data: Dict[str, Any]) -> bool:
        """更新用户偏好设置"""
        try:
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False
            
            if 'job_preferences' in preferences_data:
                user.job_preferences = preferences_data['job_preferences']
            if 'interview_preferences' in preferences_data:
                user.interview_preferences = preferences_data['interview_preferences']
            if 'privacy_settings' in preferences_data:
                user.privacy_settings = preferences_data['privacy_settings']
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新用户偏好失败: {e}")
            return False
    
    @staticmethod
    def update_user_password(user_id: int, new_password: str) -> bool:
        """更新用户密码"""
        try:
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False
            
            user.set_password(new_password)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新用户密码失败: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户（软删除）"""
        try:
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False
            
            from datetime import datetime
            user.deleted_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除用户失败: {e}")
            return False
    
    @staticmethod
    def get_all_users() -> List[User]:
        """获取所有用户"""
        return User.query.filter_by(deleted_at=None).all() 