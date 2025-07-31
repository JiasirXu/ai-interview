#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试控制器
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger
import json
from datetime import datetime
import re # Added for regex in end_interview

from app.services import spark_service, vision_service, avatar_service
from app.business.interview_service import InterviewService
from app.utils.async_utils import interview_manager

# 核心：从socket控制器导入on_vision_result_global，用于跨控制器通信
from .interview_socket_controller import on_vision_result_global, socketio

bp = Blueprint('interview', __name__, url_prefix='/api/interview')

@bp.route('/test-avatar', methods=['POST'])
@jwt_required()
def test_avatar_connection():
    """测试虚拟人WebSocket连接"""
    try:
        import asyncio

        # 测试WebSocket连接
        result = asyncio.run(avatar_service.test_websocket_connection())

        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error'),
            'response': result.get('response'),
            'status_code': result.get('status_code')
        })

    except Exception as e:
        logger.error(f"测试虚拟人连接异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/test-avatar-http', methods=['POST'])
@jwt_required()
def test_avatar_http():
    """测试虚拟人HTTP API连接"""
    try:
        # 测试HTTP API连接
        result = avatar_service.test_http_api()

        return jsonify({
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'error': result.get('error'),
            'status_code': result.get('status_code'),
            'response': result.get('response')
        })

    except Exception as e:
        logger.error(f"测试虚拟人HTTP API异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/config', methods=['GET'])
@jwt_required()
def get_interview_config():
    """
    获取面试配置选项（根据用户职业偏好过滤岗位）
    """
    try:
        user_id = int(get_jwt_identity())
        
        # 定义所有岗位（这里可以移到Business层或配置文件中）
        all_positions = {
            'ai': [
                {'value': 'ai_algorithm_engineer', 'label': 'AI算法工程师'},
                {'value': 'machine_learning_engineer', 'label': '机器学习工程师'},
                {'value': 'ai_product_manager', 'label': 'AI产品经理'},
                {'value': 'ai_data_scientist', 'label': 'AI数据科学家'}
            ],
            'big_data': [
                {'value': 'big_data_engineer', 'label': '大数据开发工程师'},
                {'value': 'data_analyst', 'label': '数据分析师'},
                {'value': 'data_engineer', 'label': '数据工程师'}
            ],
            'software': [
                {'value': 'frontend_engineer', 'label': '前端工程师'},
                {'value': 'backend_engineer', 'label': '后端工程师'},
                {'value': 'fullstack_engineer', 'label': '全栈工程师'},
                {'value': 'mobile_engineer', 'label': '移动端工程师'}
            ]
        }
        
        # 面试类型配置
        interview_types = [
            {'value': 'technical', 'label': '技术面试'},
            {'value': 'behavioral', 'label': '行为面试'},
            {'value': 'comprehensive', 'label': '综合面试'},
            {'value': 'custom', 'label': '自定义面试'}
        ]
        
        # 难度级别配置
        difficulty_levels = [
            {'value': 'primary', 'label': '初级'},
            {'value': 'middle', 'label': '中级'},
            {'value': 'high', 'label': '高级'}
        ]

        config_data = {
            'job_positions': all_positions,
            'interview_types': interview_types,
            'difficulty_levels': difficulty_levels
        }
        
        logger.info(f"面试配置数据: {config_data}")
        
        response_data = {
            'success': True,
            'message': '获取配置成功',
            'config': config_data,
            'data': config_data,
            'job_positions': all_positions,
            'interview_types': interview_types,
            'difficulty_levels': difficulty_levels
        }
        
        logger.info(f"面试配置响应: {response_data}")
        
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"获取面试配置失败: {e}")
        return jsonify({
            'success': False,
            'message': '获取配置失败，请稍后重试'
        }), 500

@bp.route('/start', methods=['POST'])
@jwt_required()
def start_interview():
    """开始面试"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供面试信息'
            }), 400
        
        # 调用业务服务
        interview_service = InterviewService()
        
        # 如果有interview_id，说明是启动已创建的面试
        interview_id = data.get('interview_id')
        if interview_id:
            success, message = interview_service.start_interview(user_id, interview_id)
            if success:
                # 生成session_id，使用与interview_manager一致的格式
                session_id = f"session_{interview_id}_{user_id}"
                
                # 创建会话
                from app.utils.async_utils import interview_manager
                from app.services.spark_service import spark_service
                interview_manager.create_session(user_id, interview_id, {'spark': spark_service})
                
                # 生成虚拟人欢迎视频
                try:
                    from app.services.avatar_service import avatar_service
                    welcome_message = "欢迎继续面试，我是您的AI面试官。让我们继续吧！"
                    video_result = avatar_service.create_avatar_response(
                        welcome_message,
                        {
                            'expression': 'friendly',
                            'voice_speed': 1.0,
                            'background': 'office'
                        }
                    )
                    
                    if video_result.get('success'):
                        first_question_video_url = video_result.get('video_url')
                        stream_type = video_result.get('stream_type', 'http')
                    else:
                        first_question_video_url = None
                        stream_type = None
                        logger.warning(f"虚拟人视频生成失败: {video_result.get('error')}")
                except Exception as e:
                    logger.error(f"生成虚拟人视频失败: {e}")
                    first_question_video_url = None
                    stream_type = None
                
                return jsonify({
                    'success': True,
                    'message': message,
                    'data': {
                        'session_id': session_id,
                        'interview_id': interview_id,
                        'first_question_video_url': first_question_video_url,
                        'stream_type': stream_type
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
        else:
            # 创建新面试
            success, message, interview_info = interview_service.create_interview(user_id, data)
            
            if success:
                # 生成session_id，使用与interview_manager一致的格式
                session_id = f"session_{interview_info['id']}_{user_id}"
                
                # 创建会话
                from app.utils.async_utils import interview_manager
                from app.services.spark_service import spark_service
                interview_manager.create_session(user_id, interview_info['id'], {'spark': spark_service})
                
                # 生成虚拟人欢迎视频
                try:
                    from app.services.avatar_service import avatar_service
                    welcome_message = "欢迎参加面试，我是您的AI面试官。让我们开始吧！"
                    video_result = avatar_service.create_avatar_response(
                        welcome_message,
                        {
                            'expression': 'friendly',
                            'voice_speed': 1.0,
                            'background': 'office'
                        }
                    )
                    
                    if video_result.get('success'):
                        first_question_video_url = video_result.get('video_url')
                        stream_type = video_result.get('stream_type', 'http')
                    else:
                        first_question_video_url = None
                        stream_type = None
                        logger.warning(f"虚拟人视频生成失败: {video_result.get('error')}")
                except Exception as e:
                    logger.error(f"生成虚拟人视频失败: {e}")
                    first_question_video_url = None
                    stream_type = None

                return jsonify({
                    'success': True,
                    'message': message,
                    'data': {
                        'session_id': session_id,
                        'interview_id': interview_info['id'],
                        'interview': interview_info,
                        'first_question_video_url': first_question_video_url,
                        'stream_type': stream_type
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400

    except Exception as e:
        logger.error(f"开始面试失败: {e}")
        return jsonify({
            'success': False,
            'message': '开始失败，请稍后重试'
        }), 500

@bp.route('/next-question', methods=['POST'])
@jwt_required()
def get_next_question():
    """获取下一个问题"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供面试信息'
            }), 400
        
        interview_id = data.get('interview_id')
        if not interview_id:
            return jsonify({
                'success': False,
                'message': '请提供面试ID'
            }), 400
        
        # 调用业务服务
        interview_service = InterviewService()
        success, message, question_data = interview_service.get_next_question(user_id, interview_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'question': question_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400

    except Exception as e:
        logger.error(f"获取下一个问题失败: {e}")
        return jsonify({
            'success': False,
            'message': '获取失败，请稍后重试'
        }), 500

@bp.route('/submit-answer', methods=['POST'])
@jwt_required()
def submit_answer():
    """提交答案"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供答案信息'
            }), 400
        
        interview_id = data.get('interview_id')
        answer = data.get('answer')
        
        if not interview_id or not answer:
            return jsonify({
                'success': False,
                'message': '请提供面试ID和答案'
            }), 400
        
        # 调用业务服务
        interview_service = InterviewService()
        success, message = interview_service.submit_answer(user_id, interview_id, answer)
        
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
        logger.error(f"提交答案失败: {e}")
        return jsonify({
            'success': False,
            'message': '提交失败，请稍后重试'
        }), 500

@bp.route('/end', methods=['POST'])
@jwt_required()
def end_interview():
    """结束面试"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供面试信息'
            }), 400
        
        interview_id = data.get('interview_id')
        if not interview_id:
            return jsonify({
                'success': False,
                'message': '请提供面试ID'
            }), 400
        
        # 调用业务服务
        interview_service = InterviewService()
        success, message = interview_service.complete_interview(user_id, interview_id)
        
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
        logger.error(f"结束面试失败: {e}")
        return jsonify({
            'success': False,
            'message': '结束失败，请稍后重试'
        }), 500

@bp.route('/frame/<session_id>', methods=['POST'])
@jwt_required()
def analyze_frame(session_id: str):
    """分析视频帧"""
    try:
        user_id = int(get_jwt_identity())
        
        # 这里可以添加视频帧分析的逻辑
        return jsonify({
            'success': True,
            'message': '帧分析完成'
        }), 200

    except Exception as e:
        logger.error(f"分析视频帧失败: {e}")
        return jsonify({
            'success': False,
            'message': '分析失败'
        }), 500

@bp.route('/list', methods=['GET'])
@jwt_required()
def get_interviews():
    """获取面试列表"""
    try:
        user_id = int(get_jwt_identity())
        
        # 调用业务服务
        interview_service = InterviewService()
        success, message, interview_list = interview_service.get_user_interviews(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'interviews': interview_list
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"获取面试列表失败: {e}")
        return jsonify({
            'success': False,
            'message': '获取失败，请稍后重试'
        }), 500

@bp.route('/transcription/start', methods=['POST'])
@jwt_required()
def start_transcription():
    """开始语音转文字"""
    try:
        # 这里可以添加开始语音转文字的逻辑
        return jsonify({
            'success': True,
            'message': '语音转文字已开始'
        }), 200

    except Exception as e:
        logger.error(f"开始语音转文字失败: {e}")
        return jsonify({
            'success': False,
            'message': '开始失败'
        }), 500

@bp.route('/transcription/stop', methods=['POST'])
@jwt_required()
def stop_transcription():
    """停止语音转文字"""
    try:
        # 这里可以添加停止语音转文字的逻辑
        return jsonify({
            'success': True,
            'message': '语音转文字已停止'
        }), 200
        
    except Exception as e:
        logger.error(f"停止语音转文字失败: {e}")
        return jsonify({
            'success': False,
            'message': '停止失败'
        }), 500

def register_interview_routes(app):
    """注册面试路由"""
    app.register_blueprint(bp)