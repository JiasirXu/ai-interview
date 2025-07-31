#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历上传、识别、技能提取API控制器
"""

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from loguru import logger
from app.business.resume_service import ResumeBusinessService

def register_resume_routes(app):
    """注册简历相关路由"""
    
    resume_service = ResumeBusinessService()
    
    @app.route('/api/resume/test', methods=['POST'])
    def test_upload():
        """测试上传接口"""
        try:
            logger.info("测试上传接口被调用")
            logger.info(f"请求方法: {request.method}")
            logger.info(f"请求headers: {dict(request.headers)}")
            logger.info(f"请求files: {request.files}")
            logger.info(f"请求form: {request.form}")
            
            return jsonify({
                'success': True,
                'message': '测试接口正常',
                'data': {
                    'method': request.method,
                    'files': list(request.files.keys()),
                    'form': dict(request.form)
                }
            }), 200
            
        except Exception as e:
            logger.error(f"测试接口错误: {e}")
            return jsonify({
                'success': False,
                'message': f'测试接口错误: {str(e)}'
            }), 500

    @app.route('/api/resume/upload', methods=['POST'])
    @jwt_required()
    def upload_resume():
        """上传简历文件"""
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
            
            # 获取简历名称（可选）
            resume_name = request.form.get('resume_name')
            
            # 调用业务服务
            success, message, resume_info = resume_service.upload_resume(user_id, file, resume_name)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'resume': resume_info
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"上传简历失败: {e}")
            return jsonify({
                'success': False,
                'message': '上传失败，请稍后重试'
            }), 500
    
    @app.route('/api/resume/list', methods=['GET'])
    @jwt_required()
    def list_resumes():
        """获取简历列表"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, resume_list = resume_service.get_user_resumes(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'resumes': resume_list
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取简历列表失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败，请稍后重试'
            }), 500
    
    @app.route('/api/resume/<int:resume_id>', methods=['GET'])
    @jwt_required()
    def get_resume(resume_id):
        """获取简历详情"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, resume_detail = resume_service.get_resume_detail(user_id, resume_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'resume': resume_detail
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
            
        except Exception as e:
            logger.error(f"获取简历详情失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败，请稍后重试'
            }), 500
    
    @app.route('/api/resume/<int:resume_id>', methods=['PUT'])
    @jwt_required()
    def update_resume(resume_id):
        """更新简历"""
        try:
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请提供更新信息'
                }), 400
            
            # 检查是否要更新名称
            if 'name' in data:
                success, message = resume_service.update_resume_name(user_id, resume_id, data['name'])
            
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
            
            return jsonify({
                'success': False,
                'message': '暂不支持其他字段的更新'
            }), 400
            
        except Exception as e:
            logger.error(f"更新简历失败: {e}")
            return jsonify({
                'success': False,
                'message': '更新失败，请稍后重试'
            }), 500
    
    @app.route('/api/resume/<int:resume_id>', methods=['DELETE'])
    @jwt_required()
    def delete_resume(resume_id):
        """删除简历"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message = resume_service.delete_resume(user_id, resume_id)
            
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
            logger.error(f"删除简历失败: {e}")
            return jsonify({
                'success': False,
                'message': '删除失败，请稍后重试'
            }), 500
    
    @app.route('/api/resume/statistics', methods=['GET'])
    @jwt_required()
    def get_resume_statistics():
        """获取简历统计信息"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            success, message, statistics = resume_service.get_resume_statistics(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'statistics': statistics
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"获取简历统计信息失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取失败，请稍后重试'
            }), 500