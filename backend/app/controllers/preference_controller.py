#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
偏好设置管理控制器 - 支持面试偏好、求职偏好、账户设置等
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from loguru import logger
from app.business.user_service import UserService
import json

def register_preference_routes(app):
    """注册偏好设置相关路由"""

    @app.route('/api/preferences/career-config', methods=['GET'])
    @jwt_required()
    def get_career_config():
        """获取职业配置信息"""
        try:
            # 定义职业配置（可以移到Business层或配置文件中）
            career_config = {
                'target_field': 'ai',  # 默认值
                'target_fields': [
                    {
                        'value': 'ai',
                        'label': '人工智能',
                        'salary_range': '18-35K/月',
                        'positions': [
                            {'value': 'ai_algorithm_engineer', 'label': 'AI算法工程师'},
                            {'value': 'machine_learning_engineer', 'label': '机器学习工程师'},
                            {'value': 'ai_product_manager', 'label': 'AI产品经理'},
                            {'value': 'ai_data_scientist', 'label': 'AI数据科学家'}
                        ]
                    },
                    {
                        'value': 'big_data',
                        'label': '大数据',
                        'salary_range': '15-30K/月',
                        'positions': [
                            {'value': 'big_data_engineer', 'label': '大数据开发工程师'},
                            {'value': 'data_analyst', 'label': '数据分析师'},
                            {'value': 'data_product_manager', 'label': '数据产品经理'},
                            {'value': 'data_architect', 'label': '数据架构师'}
                        ]
                    },
                    {
                        'value': 'iot',
                        'label': '物联网',
                        'salary_range': '12-25K/月',
                        'positions': [
                            {'value': 'iot_engineer', 'label': '物联网开发工程师'},
                            {'value': 'iot_system_engineer', 'label': '物联网系统工程师'},
                            {'value': 'iot_product_manager', 'label': '物联网产品经理'},
                            {'value': 'iot_solution_architect', 'label': '物联网解决方案架构师'}
                        ]
                    }
                ]
            }

            return jsonify({
                'success': True,
                'data': career_config
            }), 200

        except Exception as e:
            logger.error(f"获取职业配置失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取配置失败'
            }), 500

    @app.route('/api/preferences/career', methods=['GET'])
    @jwt_required()
    def get_career_preferences():
        """获取职业偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)

            if success:
                career_preferences = profile.get('job_preferences', {})
                
                # 确保返回默认值，避免前端出现 null 错误
                if not career_preferences:
                    career_preferences = {
                        'target_field': 'ai',
                        'target_positions': [],
                        'target_companies': [],
                        'work_location': '',
                        'company_size': '',
                        'work_experience': ''
                    }
                
                return jsonify({
                    'success': True,
                    'data': career_preferences
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400

        except Exception as e:
            logger.error(f"获取职业偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取偏好失败'
            }), 500

    @app.route('/api/preferences/career', methods=['PUT'])
    @jwt_required()
    def update_career_preferences():
        """更新职业偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供职业偏好数据'
                }), 400

            # 构建更新数据
            update_data = {'job_preferences': data}
            
            # 调用业务服务
            success, message = UserService.update_user_preferences(user_id, update_data)
            
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
            logger.error(f"更新职业偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500

    @app.route('/api/preferences/interview', methods=['GET'])
    @jwt_required()
    def get_interview_preferences():
        """获取面试偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                interview_preferences = profile.get('interview_preferences', {})
                
                # 确保返回默认值，避免前端出现 null 错误
                if not interview_preferences:
                    interview_preferences = {
                        'selected_avatar': 1,
                        'interaction_mode': 'listener',
                        'feedbacks': ['nod'],
                        'voice_speed': '1',
                        'recording_type': 'audio',
                        'ai_highlight': True,
                        'improvement_marking': True,
                        'background_noises': []
                    }
                
                return jsonify({
                    'success': True,
                    'data': interview_preferences
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取面试偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取偏好失败'
            }), 500
    
    @app.route('/api/preferences/interview', methods=['PUT'])
    @jwt_required()
    def update_interview_preferences():
        """更新面试偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供面试偏好数据'
                }), 400
            
            # 构建更新数据
            update_data = {'interview_preferences': data}
            
            # 调用业务服务
            success, message = UserService.update_user_preferences(user_id, update_data)

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
            logger.error(f"更新面试偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500

    @app.route('/api/preferences/interview/test-voice', methods=['POST'])
    @jwt_required()
    def test_voice_preview():
        """测试语音预览"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供测试数据'
                }), 400

            # 这里可以添加语音预览的逻辑
            return jsonify({
                'success': True,
                'message': '语音预览测试成功'
            }), 200

        except Exception as e:
            logger.error(f"测试语音预览失败: {e}")
            return jsonify({
                'success': False,
                'message': '测试失败'
            }), 500
    
    @app.route('/api/preferences/job', methods=['GET'])
    @jwt_required()
    def get_job_preferences():
        """获取求职偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                job_preferences = profile.get('job_preferences', {})
                
                return jsonify({
                    'success': True,
                    'data': job_preferences
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取求职偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取偏好失败'
            }), 500
    
    @app.route('/api/preferences/job', methods=['PUT'])
    @jwt_required()
    def update_job_preferences():
        """更新求职偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供求职偏好数据'
                }), 400
            
            # 构建更新数据
            update_data = {'job_preferences': data}
            
            # 调用业务服务
            success, message = UserService.update_user_preferences(user_id, update_data)
            
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
            logger.error(f"更新求职偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/preferences/all', methods=['GET'])
    @jwt_required()
    def get_all_preferences():
        """获取所有偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                all_preferences = {
                    'career_preferences': profile.get('job_preferences', {}),
                    'interview_preferences': profile.get('interview_preferences', {}),
                    'privacy_settings': profile.get('privacy_settings', {})
                }
                
                return jsonify({
                    'success': True,
                    'data': all_preferences
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取所有偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取偏好失败'
            }), 500
    
    @app.route('/api/preferences/reset', methods=['POST'])
    @jwt_required()
    def reset_preferences():
        """重置偏好设置"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供重置类型'
                }), 400
            
            reset_type = data.get('type', 'all')
            
            # 根据类型重置不同的偏好
            if reset_type == 'career':
                update_data = {'job_preferences': {}}
            elif reset_type == 'interview':
                update_data = {'interview_preferences': {}}
            elif reset_type == 'privacy':
                update_data = {'privacy_settings': {}}
            else:
                # 重置所有偏好
                update_data = {
                    'job_preferences': {},
                    'interview_preferences': {},
                    'privacy_settings': {}
                }
            
            # 调用业务服务
            success, message = UserService.update_user_preferences(user_id, update_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'{reset_type}偏好重置成功'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"重置偏好失败: {e}")
            return jsonify({
                'success': False,
                'message': '重置失败，请稍后重试'
            }), 500

    @app.route('/api/preferences/avatars', methods=['GET'])
    @jwt_required()
    def get_available_avatars():
        """获取可用的虚拟人列表"""
        try:
            # 这里可以添加获取虚拟人列表的逻辑
            avatars = [
                {'id': 'avatar1', 'name': '面试官A', 'description': '专业严谨'},
                {'id': 'avatar2', 'name': '面试官B', 'description': '友好温和'},
                {'id': 'avatar3', 'name': '面试官C', 'description': '技术专家'}
            ]

            return jsonify({
                'success': True,
                'data': avatars
            }), 200

        except Exception as e:
            logger.error(f"获取虚拟人列表失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败'
            }), 500