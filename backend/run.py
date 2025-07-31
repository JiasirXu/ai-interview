#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用启动文件
"""

import os
from app import create_app

# 获取配置环境
config_name = os.getenv('FLASK_CONFIG') or 'default'

# 创建Flask应用实例
app, socketio = create_app(config_name)

if __name__ == '__main__':
    # 确保上传目录存在
    upload_dir = app.config.get('UPLOAD_FOLDER')
    if upload_dir and not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 获取端口号
    port = int(os.getenv('PORT', 5000))
    
    # 打印启动信息
    print("=" * 60)
    print("🚀 软件杯后端服务启动中...")
    print("=" * 60)
    print(f"📡 服务地址: http://127.0.0.1:{port}")
    print(f"🌐 网络地址: http://192.168.1.4:{port}")
    print(f"🔧 调试模式: {'开启' if app.config.get('DEBUG', False) else '关闭'}")
    print(f"📁 上传目录: {upload_dir}")
    print("=" * 60)
    print("✅ 服务启动成功！按 Ctrl+C 停止服务")
    print("=" * 60)

    # 启动应用（使用SocketIO）
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True
    )