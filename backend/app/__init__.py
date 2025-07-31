#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用包初始化
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from datetime import datetime
from .models import db, jwt, migrate, cors
# 控制器导入将在下面单独处理
from .controllers.interview_socket_controller import socketio, register_socket_handlers

def create_app(config_name='default'):
    """
    应用工厂函数
    """
    app = Flask(__name__)
    
    # 1. 加载配置
    app.config.from_object(config[config_name])
    
    # 2. 初始化扩展
    db.init_app(app)
    jwt.init_app(app)

    # JWT错误处理器
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'Token已过期'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'success': False, 'message': 'Token无效'}), 422

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'success': False, 'message': '缺少Token'}), 401

    cors.init_app(app,
                  origins=app.config['CORS_ORIGINS'],
                  supports_credentials=app.config['CORS_ALLOW_CREDENTIALS'])

    # 确保上传目录存在
    import os
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        # 创建头像上传子目录
        avatar_folder = os.path.join(upload_folder, 'avatars')
        if not os.path.exists(avatar_folder):
            os.makedirs(avatar_folder)

    # 初始化Socket.IO
    socketio.init_app(app)

    # 3. 注册路由
    # 上传文件访问路由
    from flask import send_from_directory

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # 健康检查路由
    @app.route('/')
    def health_check():
        return jsonify({
            'success': True,
            'message': '面试系统后端服务正常运行',
            'version': '1.0.0'
        })

    @app.route('/api/health')
    def api_health_check():
        return jsonify({
            'success': True,
            'message': 'API服务正常',
            'timestamp': datetime.now().isoformat()
        })

    # 调试路由 - 列出所有注册的路由
    @app.route('/api/debug/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        return jsonify({
            'success': True,
            'routes': routes
        })

    from app.controllers.auth_controller import register_auth_routes
    from app.controllers.profile_controller import register_profile_routes
    from app.controllers.preference_controller import register_preference_routes
    from app.controllers.resume_controller import register_resume_routes
    from app.controllers.interview_controller import register_interview_routes
    from app.controllers.result_controller import register_result_routes

    register_auth_routes(app)
    register_profile_routes(app)
    register_preference_routes(app)
    register_resume_routes(app)
    register_interview_routes(app)
    register_result_routes(app)

    # 注册Socket.IO事件处理器
    register_socket_handlers()

    return app, socketio