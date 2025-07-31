#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户业务逻辑服务
"""

from typing import Optional, Dict, Any, Tuple
from app.dao.user_dao import UserDAO
from app.models.user import User
from loguru import logger
import re


class UserService:
    """用户业务逻辑服务"""
    
    @staticmethod
    def register_user(username: str, email: str, phone: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册业务逻辑
        
        Returns:
            (是否成功, 消息, 用户对象)
        """
        try:
            # 1. 参数验证
            if not all([username, email, phone, password]):
                return False, "所有字段都是必填的", None
            
            # 2. 用户名验证
            if len(username) < 3 or len(username) > 20:
                return False, "用户名长度必须在3-20个字符之间", None
            
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return False, "用户名只能包含字母、数字和下划线", None
            
            # 3. 邮箱验证
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "邮箱格式不正确", None
            
            # 4. 手机号验证
            phone_pattern = r'^1[3-9]\d{9}$'
            if not re.match(phone_pattern, phone):
                return False, "手机号格式不正确", None
            
            # 5. 密码验证
            if len(password) < 6:
                return False, "密码长度至少6位", None
            
            # 6. 检查用户是否已存在
            if UserDAO.get_user_by_username(username):
                return False, "用户名已存在", None
            
            if UserDAO.get_user_by_email(email):
                return False, "邮箱已被注册", None
            
            if UserDAO.get_user_by_phone(phone):
                return False, "手机号已被注册", None
            
            # 7. 创建用户
            user = UserDAO.create_user(username, email, phone, password)
            if not user:
                return False, "用户创建失败", None
            
            return True, "注册成功", user
            
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return False, "注册失败，请稍后重试", None
    
    @staticmethod
    def login_user(username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录业务逻辑
        
        Returns:
            (是否成功, 消息, 用户对象)
        """
        try:
            # 1. 参数验证
            if not username or not password:
                return False, "用户名和密码不能为空", None
            
            # 2. 查找用户
            user = UserDAO.get_user_by_username(username)
            if not user:
                return False, "用户名或密码错误", None
            
            # 3. 检查用户状态
            if user.deleted_at:
                return False, "账户已被删除", None
            
            if not user.is_active:
                return False, "账户已被禁用", None
            
            # 4. 验证密码
            if not user.check_password(password):
                return False, "用户名或密码错误", None
            
            return True, "登录成功", user
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return False, "登录失败，请稍后重试", None
    
    @staticmethod
    def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新用户资料业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户是否存在
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 数据验证
            if 'email' in profile_data:
                email = profile_data['email']
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, email):
                    return False, "邮箱格式不正确"
                
                # 检查邮箱是否被其他用户使用
                existing_user = UserDAO.get_user_by_email(email)
                if existing_user and existing_user.id != user_id:
                    return False, "邮箱已被其他用户使用"
            
            if 'phone' in profile_data:
                phone = profile_data['phone']
                phone_pattern = r'^1[3-9]\d{9}$'
                if not re.match(phone_pattern, phone):
                    return False, "手机号格式不正确"
                
                # 检查手机号是否被其他用户使用
                existing_user = UserDAO.get_user_by_phone(phone)
                if existing_user and existing_user.id != user_id:
                    return False, "手机号已被其他用户使用"
            
            # 3. 更新资料
            success = UserDAO.update_user_profile(user_id, profile_data)
            if not success:
                return False, "更新失败"
            
            return True, "资料更新成功"
            
        except Exception as e:
            logger.error(f"更新用户资料失败: {e}")
            return False, "更新失败，请稍后重试"
    
    @staticmethod
    def get_user_profile(user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取用户资料业务逻辑
        
        Returns:
            (是否成功, 消息, 用户资料)
        """
        try:
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 构建用户资料
            profile = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'name': user.name,
                'gender': user.gender,
                'birth_date': user.birth_date.isoformat() if user.birth_date else None,
                'contact': user.contact,
                'avatar': user.avatar,
                'education_info': user.education_info,
                'skills': user.skills,
                'job_preferences': user.job_preferences,
                'interview_preferences': user.interview_preferences,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
            
            return True, "获取成功", profile
            
        except Exception as e:
            logger.error(f"获取用户资料失败: {e}")
            return False, "获取失败", None
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证旧密码
            if not user.check_password(old_password):
                return False, "原密码错误"
            
            # 3. 验证新密码
            if len(new_password) < 6:
                return False, "新密码长度至少6位"
            
            if old_password == new_password:
                return False, "新密码不能与原密码相同"
            
            # 4. 更新密码
            success = UserDAO.update_user_password(user_id, new_password)
            if not success:
                return False, "密码更新失败"
            
            return True, "密码修改成功"
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return False, "修改失败，请稍后重试" 