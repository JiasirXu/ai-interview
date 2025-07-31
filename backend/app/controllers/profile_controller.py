#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户资料管理控制器 - 支持个人信息、教育背景、技能管理等
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from loguru import logger
from app.business.user_service import UserService
import os
import re
from werkzeug.utils import secure_filename

def register_profile_routes(app):
    """注册用户资料相关路由"""
    
    @app.route('/api/profile/personal-info', methods=['GET'])
    @jwt_required()
    def get_personal_info():
        """获取个人基础信息"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                # 提取个人信息
                personal_info = {
                    'name': profile.get('name', ''),
                    'gender': profile.get('gender', ''),
                    'birth_date': profile.get('birth_date', ''),
                    'phone': profile.get('phone', ''),
                    'email': profile.get('email', ''),
                    'contact': profile.get('contact', ''),
                    'avatar': profile.get('avatar', '')
                }
                
                return jsonify({
                    'success': True,
                    'data': personal_info
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取个人信息失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取信息失败'
            }), 500
    
    @app.route('/api/profile/personal-info', methods=['PUT'])
    @jwt_required()
    def update_personal_info():
        """更新个人基础信息"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供更新数据'
                }), 400
            
            # 调用业务服务
            success, message = UserService.update_user_profile(user_id, data)
            
            if success:
                    return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                        return jsonify({
                            'success': False,
                    'message': message
                        }), 400
            
        except Exception as e:
            logger.error(f"更新个人信息失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/profile/education', methods=['GET'])
    @jwt_required()
    def get_education_info():
        """获取教育背景信息"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                education_info = profile.get('education_info', {})
                
                return jsonify({
                    'success': True,
                    'data': education_info
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取教育背景失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取信息失败'
            }), 500
    
    @app.route('/api/profile/education', methods=['PUT'])
    @jwt_required()
    def update_education_info():
        """更新教育背景信息"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供教育背景数据'
                }), 400
            
            # 构建更新数据
            update_data = {'education_info': data}
            
            # 调用业务服务
            success, message = UserService.update_user_profile(user_id, update_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"更新教育背景失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/profile/skills', methods=['GET'])
    @jwt_required()
    def get_skills():
        """获取技能信息"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                skills = profile.get('skills', {})
                
                return jsonify({
                    'success': True,
                    'data': skills
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取技能信息失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取信息失败'
            }), 500
    
    @app.route('/api/profile/skills', methods=['PUT'])
    @jwt_required()
    def update_skills():
        """更新技能信息"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供技能数据'
                }), 400
            
            # 构建更新数据
            update_data = {'skills': data}
            
            # 调用业务服务
            success, message = UserService.update_user_profile(user_id, update_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"更新技能信息失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/profile/avatar', methods=['POST'])
    @jwt_required()
    def upload_avatar():
        """上传头像"""
        try:
            user_id = int(get_jwt_identity())
            
            # 检查文件
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': '没有上传文件'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': '没有选择文件'
                }), 400
            
            # 这里可以添加头像上传的逻辑
            # 调用业务服务
            success, message = UserService.update_user_profile(user_id, {'avatar': 'uploaded_avatar_url'})
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"上传头像失败: {e}")
            return jsonify({
                'success': False,
                'message': '上传失败，请稍后重试'
            }), 500
    
    @app.route('/api/profile/summary', methods=['GET'])
    @jwt_required()
    def get_profile_summary():
        """获取资料完整度摘要"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                # 计算完整度
                completeness = _calculate_profile_completeness(profile)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'completeness': completeness,
                        'profile': profile
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取资料摘要失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取信息失败'
            }), 500


def _calculate_profile_completeness(profile):
    """计算资料完整度"""
    total_fields = 0
    filled_fields = 0
    
    # 基础信息
    basic_fields = ['name', 'gender', 'birth_date', 'phone', 'email', 'contact']
    for field in basic_fields:
        total_fields += 1
        if profile.get(field):
            filled_fields += 1
    
    # 教育信息
    education_info = profile.get('education_info', {})
    if education_info:
        total_fields += 1
        filled_fields += 1
    
    # 技能信息
    skills = profile.get('skills', {})
    if skills:
        total_fields += 1
        filled_fields += 1
    
    # 计算百分比
    completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
    
    return round(completeness, 1) 