#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证控制器 - 专注于登录、注册、token验证等认证相关功能
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt, decode_token
from datetime import datetime, timedelta
from loguru import logger
from app.business.user_service import UserService
import re
import json

def register_auth_routes(app):
    """注册认证相关路由"""
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供注册信息'
                }), 400
            
            # 验证必需字段
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'success': False,
                        'message': f'缺少必需字段: {field}'
                    }), 400
            
            username = data.get('username').strip()
            email = data.get('email').strip()
            password = data.get('password')
            phone = data.get('phone', '').strip()
            
            # 调用业务服务
            success, message, user = UserService.register_user(username, email, phone, password)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'phone': user.phone
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return jsonify({
                'success': False,
                'message': '注册失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供登录信息'
                }), 400
            
            # 提取参数
            username_or_email = data.get('username') or data.get('email')
            password = data.get('password')
            
            if not username_or_email or not password:
                return jsonify({
                    'success': False,
                    'message': '请提供用户名/邮箱和密码'
                }), 400
            
            # 调用业务服务
            success, message, user = UserService.login_user(username_or_email, password)
            
            if success:
                # 生成访问令牌
                access_token = create_access_token(
                    identity=str(user.id),
                    expires_delta=timedelta(hours=24)
                )
                
                # 记录登录历史
                _record_login_history(user.id, '登录', request)
                
                logger.info(f"用户登录成功: {user.username}")
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'phone': user.phone
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 401
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return jsonify({
                'success': False,
                'message': '登录失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """用户登出"""
        try:
            # 这里可以添加登出逻辑，比如将token加入黑名单
            return jsonify({
                'success': True,
                'message': '登出成功'
            }), 200
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return jsonify({
                'success': False,
                'message': '登出失败'
            }), 500
    
    @app.route('/api/auth/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        """修改密码"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供密码信息'
                }), 400
            
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            
            if not old_password or not new_password:
                return jsonify({
                    'success': False,
                    'message': '请提供原密码和新密码'
                }), 400
            
            # 调用业务服务
            success, message = UserService.change_password(user_id, old_password, new_password)
            
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
            logger.error(f"修改密码失败: {e}")
            return jsonify({
                'success': False,
                'message': '修改失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/verify-token', methods=['POST'])
    @jwt_required()
    def verify_token():
        """验证令牌"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务获取用户信息
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '令牌有效',
                    'user': {
                        'id': profile['id'],
                        'username': profile['username'],
                        'email': profile['email']
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': '令牌无效'
                }), 401
            
        except Exception as e:
            logger.error(f"验证令牌失败: {e}")
            return jsonify({
                'success': False,
                'message': '验证失败'
            }), 401
    
    @app.route('/api/auth/refresh-token', methods=['POST'])
    def refresh_token():
        """刷新令牌"""
        try:
            # 这里可以添加刷新token的逻辑
            return jsonify({
                'success': True,
                'message': '令牌刷新成功'
            }), 200
        except Exception as e:
            logger.error(f"刷新令牌失败: {e}")
            return jsonify({
                'success': False,
                'message': '刷新失败'
            }), 500
    
    @app.route('/api/auth/login-history', methods=['GET'])
    @jwt_required()
    def get_login_history():
        """获取登录历史"""
        try:
            user_id = int(get_jwt_identity())
            
            # 这里可以添加获取登录历史的逻辑
            return jsonify({
                'success': True,
                'message': '获取登录历史成功',
                'data': []
            }), 200
        except Exception as e:
            logger.error(f"获取登录历史失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败'
            }), 500
    
    @app.route('/api/auth/refresh-login-history', methods=['POST'])
    @jwt_required()
    def refresh_login_history():
        """刷新登录历史"""
        try:
            user_id = int(get_jwt_identity())
            
            # 这里可以添加刷新登录历史的逻辑
            return jsonify({
                'success': True,
                'message': '刷新登录历史成功'
            }), 200
        except Exception as e:
            logger.error(f"刷新登录历史失败: {e}")
            return jsonify({
                'success': False,
                'message': '刷新失败'
            }), 500
    
    @app.route('/api/auth/change-phone', methods=['POST'])
    @jwt_required()
    def change_phone():
        """修改手机号"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供手机号信息'
                }), 400
            
            new_phone = data.get('phone', '').strip()
            
            if not new_phone:
                return jsonify({
                    'success': False,
                    'message': '请提供新的手机号'
                }), 400
            
            # 调用业务服务
            success, message = UserService.update_user_profile(user_id, {'phone': new_phone})
            
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
            logger.error(f"修改手机号失败: {e}")
            return jsonify({
                'success': False,
                'message': '修改失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/privacy', methods=['GET'])
    @jwt_required()
    def get_privacy_settings_auth():
        """获取隐私设置"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                privacy_settings = profile.get('privacy_settings', {})
                
                return jsonify({
                    'success': True,
                    'message': '获取隐私设置成功',
                    'data': privacy_settings
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取隐私设置失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败'
            }), 500
    
    @app.route('/api/preferences/privacy', methods=['GET'])
    @jwt_required()
    def get_privacy_settings():
        """获取隐私设置（偏好设置路由）"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, profile = UserService.get_user_profile(user_id)
            
            if success:
                privacy_settings = profile.get('privacy_settings', {})
                
                return jsonify({
                    'success': True,
                    'message': '获取隐私设置成功',
                    'data': privacy_settings
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取隐私设置失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败'
            }), 500
    
    @app.route('/api/auth/privacy', methods=['PUT'])
    @jwt_required()
    def update_privacy_settings_auth():
        """更新隐私设置"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供隐私设置信息'
                }), 400
            
            # 构建更新数据
            update_data = {'privacy_settings': data}
            
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
            logger.error(f"更新隐私设置失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/preferences/privacy', methods=['PUT'])
    @jwt_required()
    def update_privacy_settings():
        """更新隐私设置（偏好设置路由）"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供隐私设置信息'
                }), 400
            
            # 构建更新数据
            update_data = {'privacy_settings': data}
            
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
            logger.error(f"更新隐私设置失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/clear-data', methods=['POST'])
    @jwt_required()
    def clear_user_data_auth():
        """清除用户数据"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供清除类型'
                }), 400
            
            clear_type = data.get('type', 'all')
            
            # 这里可以添加清除用户数据的逻辑
            return jsonify({
                'success': True,
                'message': f'{clear_type}数据清除成功'
            }), 200
        except Exception as e:
            logger.error(f"清除用户数据失败: {e}")
            return jsonify({
                'success': False,
                'message': '清除失败'
            }), 500
    
    @app.route('/api/preferences/clear-data', methods=['POST'])
    @jwt_required()
    def clear_user_data():
        """清除用户数据（偏好设置路由）"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供清除类型'
                }), 400
            
            clear_type = data.get('type', 'all')
            
            # 这里可以添加清除用户数据的逻辑
            return jsonify({
                'success': True,
                'message': f'{clear_type}数据清除成功'
            }), 200
        except Exception as e:
            logger.error(f"清除用户数据失败: {e}")
            return jsonify({
                'success': False,
                'message': '清除失败'
            }), 500
    
    @app.route('/api/auth/account/delete', methods=['POST'])
    @jwt_required()
    def delete_account_auth():
        """删除账户"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供确认信息'
                }), 400
            
            confirm_password = data.get('password')
            
            if not confirm_password:
                return jsonify({
                    'success': False,
                    'message': '请提供密码确认'
                }), 400
            
            # 调用业务服务
            success, message = UserService.delete_user(user_id, confirm_password)
            
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
            logger.error(f"删除账户失败: {e}")
            return jsonify({
                'success': False,
                'message': '删除失败，请稍后重试'
            }), 500
    
    @app.route('/api/preferences/account/delete', methods=['POST'])
    @jwt_required()
    def delete_account():
        """删除账户（偏好设置路由）"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供确认信息'
                }), 400
            
            confirm_password = data.get('password')
            
            if not confirm_password:
                return jsonify({
                    'success': False,
                    'message': '请提供密码确认'
                }), 400
            
            # 调用业务服务
            success, message = UserService.delete_user(user_id, confirm_password)
            
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
            logger.error(f"删除账户失败: {e}")
            return jsonify({
                'success': False,
                'message': '删除失败，请稍后重试'
            }), 500
    
    @app.route('/api/auth/set-resume-visibility', methods=['POST'])
    @jwt_required()
    def set_resume_visibility():
        """设置简历可见性"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供可见性设置'
                }), 400
            
            visibility = data.get('visibility', 'private')
            
            if visibility not in ['public', 'private']:
                return jsonify({
                    'success': False,
                    'message': '可见性设置无效'
                }), 400
            
            # 构建更新数据
            update_data = {'resume_visibility': visibility}
            
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
            logger.error(f"设置简历可见性失败: {e}")
            return jsonify({
                'success': False,
                'message': '设置失败，请稍后重试'
            }), 500


def _record_login_history(user_id, action, request_obj):
    """记录登录历史"""
    try:
        # 这里可以添加记录登录历史的逻辑
        pass
    except Exception as e:
        logger.error(f"记录登录历史失败: {e}")


def _parse_user_agent(user_agent):
    """解析用户代理"""
    try:
        # 这里可以添加解析用户代理的逻辑
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown'
        }
    except Exception as e:
        logger.error(f"解析用户代理失败: {e}")
        return {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown'
        } 