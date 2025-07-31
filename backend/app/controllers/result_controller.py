#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果控制器
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger
from app.business.interview_service import InterviewService
import json
from datetime import datetime

def register_result_routes(app):
    """注册结果路由"""
    
    @app.route('/api/result/<int:interview_id>', methods=['GET'])
    @jwt_required()
    def get_result(interview_id):
        """获取面试结果详情"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            interview_service = InterviewService()
            success, message, interview_detail = interview_service.get_interview_detail(user_id, interview_id)
            
            if success:
                # 检查面试是否已完成
                if interview_detail.get('status') != 'completed':
                    return jsonify({
                        'success': False,
                        'message': '面试尚未完成，无法查看结果'
                    }), 400
                
                # 构建结果数据
                result_data = {
                    'id': interview_detail['id'],
                    'interview_id': interview_detail['id'],
                    'interview_type': interview_detail['interview_type'],
                    'interview_mode': interview_detail['interview_mode'],
                    'position': interview_detail['position'],
                    'company': interview_detail['company'],
                    'difficulty_level': interview_detail['difficulty_level'],
                    'overall_score': interview_detail['overall_score'],
                    'technical_score': interview_detail['technical_score'],
                    'expression_logic_score': interview_detail['expression_logic_score'],
                    'adaptability_score': interview_detail['adaptability_score'],
                    'behavior_etiquette_score': interview_detail['behavior_etiquette_score'],
                    'english_communication_score': interview_detail['english_communication_score'],
                    'cultural_fit_score': interview_detail['cultural_fit_score'],
                    'questions_data': interview_detail['questions_data'],
                    'transcriptions_data': interview_detail['transcriptions_data'],
                    'ai_evaluations_data': interview_detail['ai_evaluations_data'],
                    'report_data': interview_detail['report_data'],
                    'duration': interview_detail['duration'],
                    'created_at': interview_detail['created_at'],
                    'started_at': interview_detail['started_at'],
                    'completed_at': interview_detail['completed_at'],
                    'interview_date': interview_detail['created_at']
                }
                
                return jsonify({
                    'success': True,
                    'data': result_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"获取面试结果失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取面试结果失败'
            }), 500

    @app.route('/api/result/list', methods=['GET'])
    @jwt_required()
    def get_results():
        """获取面试结果列表"""
        try:
            user_id = int(get_jwt_identity())
            
            # 获取查询参数
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            interview_type = request.args.get('interview_type')
            
            # 调用业务服务
            interview_service = InterviewService()
            success, message, interview_list = interview_service.get_user_interviews(user_id)
            
            if success:
                # 过滤已完成的面试
                completed_interviews = [
                    interview for interview in interview_list 
                    if interview.get('status') == 'completed'
                ]
                
                # 按类型过滤
                if interview_type:
                    completed_interviews = [
                        interview for interview in completed_interviews
                        if interview.get('interview_type') == interview_type
                    ]
                
                # 分页处理
                total = len(completed_interviews)
                start = (page - 1) * per_page
                end = start + per_page
                paginated_results = completed_interviews[start:end]
                
                # 构建结果数据
                result_list = []
                for interview in paginated_results:
                    result_data = {
                        'id': interview['id'],
                        'interview_type': interview['interview_type'],
                        'position': interview['position'],
                        'company': interview['company'],
                        'overall_score': interview['overall_score'],
                        'created_at': interview['created_at'],
                        'completed_at': interview['completed_at']
                    }
                    result_list.append(result_data)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'results': result_list,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'pages': (total + per_page - 1) // per_page
                        }
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"获取面试结果列表失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取结果列表失败'
            }), 500

    @app.route('/api/result/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        """获取面试结果统计"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            interview_service = InterviewService()
            success, message, statistics = interview_service.get_interview_statistics(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'data': statistics
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"获取面试统计失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取统计失败'
            }), 500

    @app.route('/api/result/<int:interview_id>/analysis', methods=['GET'])
    @jwt_required()
    def get_detailed_analysis(interview_id):
        """获取详细分析"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            interview_service = InterviewService()
            success, message, interview_detail = interview_service.get_interview_detail(user_id, interview_id)
            
            if success:
                # 检查面试是否已完成
                if interview_detail.get('status') != 'completed':
                    return jsonify({
                        'success': False,
                        'message': '面试尚未完成，无法查看分析'
                    }), 400
                
                # 构建分析数据
                analysis_data = {
                    'interview_info': {
                        'id': interview_detail['id'],
                        'interview_type': interview_detail['interview_type'],
                        'position': interview_detail['position'],
                        'company': interview_detail['company'],
                        'difficulty_level': interview_detail['difficulty_level']
                    },
                    'scores': {
                        'overall_score': interview_detail['overall_score'],
                        'technical_score': interview_detail['technical_score'],
                        'expression_logic_score': interview_detail['expression_logic_score'],
                        'adaptability_score': interview_detail['adaptability_score'],
                        'behavior_etiquette_score': interview_detail['behavior_etiquette_score'],
                        'english_communication_score': interview_detail['english_communication_score'],
                        'cultural_fit_score': interview_detail['cultural_fit_score']
                    },
                    'questions_analysis': interview_detail['questions_data'],
                    'ai_evaluations': interview_detail['ai_evaluations_data'],
                    'report': interview_detail['report_data']
                }
                
                return jsonify({
                    'success': True,
                    'data': analysis_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"获取详细分析失败: {e}")
            return jsonify({
                'success': False,
                'message': '获取分析失败'
            }), 500

    @app.route('/api/result/<int:interview_id>/export', methods=['GET'])
    @jwt_required()
    def export_result(interview_id):
        """导出面试结果"""
        try:
            user_id = int(get_jwt_identity())
            
            # 调用业务服务
            interview_service = InterviewService()
            success, message, interview_detail = interview_service.get_interview_detail(user_id, interview_id)
            
            if success:
                # 检查面试是否已完成
                if interview_detail.get('status') != 'completed':
                    return jsonify({
                        'success': False,
                        'message': '面试尚未完成，无法导出结果'
                    }), 400
                
                # 构建导出数据
                export_data = {
                    'interview_info': {
                        'id': interview_detail['id'],
                        'interview_type': interview_detail['interview_type'],
                        'position': interview_detail['position'],
                        'company': interview_detail['company'],
                        'difficulty_level': interview_detail['difficulty_level'],
                        'created_at': interview_detail['created_at'],
                        'completed_at': interview_detail['completed_at']
                    },
                    'scores': {
                        'overall_score': interview_detail['overall_score'],
                        'technical_score': interview_detail['technical_score'],
                        'expression_logic_score': interview_detail['expression_logic_score'],
                        'adaptability_score': interview_detail['adaptability_score'],
                        'behavior_etiquette_score': interview_detail['behavior_etiquette_score'],
                        'english_communication_score': interview_detail['english_communication_score'],
                        'cultural_fit_score': interview_detail['cultural_fit_score']
                    },
                    'questions': interview_detail['questions_data'],
                    'transcriptions': interview_detail['transcriptions_data'],
                    'evaluations': interview_detail['ai_evaluations_data'],
                    'report': interview_detail['report_data']
                }
                
                return jsonify({
                    'success': True,
                    'data': export_data
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': message
                }), 400
                
        except Exception as e:
            logger.error(f"导出面试结果失败: {e}")
            return jsonify({
                'success': False,
                'message': '导出失败'
            }), 500 