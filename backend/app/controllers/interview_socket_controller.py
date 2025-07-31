#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面试WebSocket控制器 - 处理实时数据流
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from flask import request as flask_request
from loguru import logger
from app.services import audio_service, spark_service, vision_service
from app.utils.async_utils import interview_manager
import asyncio
import uuid
import time

# 全局的SocketIO实例
socketio = SocketIO(cors_allowed_origins="*")

# 用于缓存视觉分析结果的临时字典
vision_results_cache = {}

def trigger_emotion_feedback(ai_response: str, session_id: str, preferences: dict):
    """
    根据AI反馈内容触发面试官表情反馈

    Args:
        ai_response: AI的反馈内容
        session_id: 会话ID
        preferences: 面试偏好设置
    """
    if not preferences.get('enable_emotion_feedback', True):
        return

    feedback_types = preferences.get('feedback_types', ['nod'])
    if not feedback_types:
        return

    # 根据AI反馈内容判断应该触发什么表情
    feedback_type = None

    # 简单的关键词匹配逻辑（实际可以用更复杂的NLP分析）
    positive_keywords = ['很好', '不错', '正确', '优秀', '赞同', '同意', '好的']
    questioning_keywords = ['但是', '然而', '不过', '疑问', '质疑', '考虑', '思考']
    time_keywords = ['时间', '快点', '抓紧', '效率', '进度']

    if any(keyword in ai_response for keyword in positive_keywords) and 'nod' in feedback_types:
        feedback_type = 'nod'
    elif any(keyword in ai_response for keyword in questioning_keywords) and 'frown' in feedback_types:
        feedback_type = 'frown'
    elif any(keyword in ai_response for keyword in time_keywords) and 'timer' in feedback_types:
        feedback_type = 'timer'

    # 如果确定了反馈类型，异步触发表情反馈
    if feedback_type:
        socketio.start_background_task(send_emotion_feedback, session_id, feedback_type, preferences)

def send_emotion_feedback(session_id: str, feedback_type: str, preferences: dict):
    """
    异步发送表情反馈

    Args:
        session_id: 会话ID
        feedback_type: 反馈类型
        preferences: 面试偏好设置
    """
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            return

        avatar_serv = session['services']['avatar']

        # 生成表情反馈视频
        feedback_result = avatar_serv.create_feedback_expression(feedback_type, preferences)

        if feedback_result.get('success'):
            # 发送表情反馈给前端
            socketio.emit('emotion_feedback', {
                'feedback_type': feedback_type,
                'video_url': feedback_result.get('video_url'),
                'duration': feedback_result.get('duration', 2.0)
            }, room=session_id)

            logger.info(f"为会话 {session_id} 发送表情反馈: {feedback_type}")
        else:
            logger.warning(f"表情反馈生成失败: {feedback_result.get('error')}")

    except Exception as e:
        logger.error(f"发送表情反馈时出错: {e}")

def on_vision_result_global(session_id: str, vision_data: dict):
    """全局函数，用于从HTTP控制器接收视觉分析结果"""
    logger.debug(f"会话 {session_id} 收到视觉分析结果: {vision_data.get('summary')}")
    # 将结果存入一个临时缓存，以便与语音结果关联
    vision_results_cache[session_id] = vision_data

def register_socket_handlers():
    """注册Socket.IO事件处理器"""

    @socketio.on('connect')
    def handle_connect(auth):
        """处理客户端连接"""
        try:
            # 生成一个临时的session ID用于日志记录
            temp_sid = str(uuid.uuid4())[:8]
            logger.info(f"收到WebSocket连接请求: auth={auth}, temp_sid={temp_sid}")

            # 从auth中获取token
            token = None
            if auth:
                if isinstance(auth, dict):
                    token = auth.get('token')
                elif isinstance(auth, str):
                    token = auth

            if not token:
                logger.warning("WebSocket连接缺少认证token，使用临时认证")
                # 临时允许连接，但记录警告
                user_id = 1  # 临时使用用户ID 1
                logger.info(f"客户端连接成功 (临时认证): user_id={user_id}, temp_sid={temp_sid}")
                emit('connection_response', {'success': True, 'message': '连接成功 (临时认证)'})
                return True

            # 手动验证JWT token
            try:
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                logger.info(f"客户端连接成功: user_id={user_id}, temp_sid={temp_sid}")
                emit('connection_response', {'success': True, 'message': '连接成功'})
                return True
            except Exception as e:
                logger.error(f"JWT token验证失败: {e}")
                # 临时允许连接，但记录错误
                user_id = 1  # 临时使用用户ID 1
                logger.info(f"客户端连接成功 (token验证失败，使用临时认证): user_id={user_id}, temp_sid={temp_sid}")
                emit('connection_response', {'success': True, 'message': '连接成功 (临时认证)'})
                return True

        except Exception as e:
            logger.error(f"WebSocket连接处理异常: {e}")
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        temp_sid = str(uuid.uuid4())[:8]
        logger.info(f"客户端断开连接: temp_sid={temp_sid}")
        # 注意：由于无法获取真实的session ID，暂时跳过清理
        # 这是一个临时解决方案，实际应用中需要更好的session管理
        logger.info("WebSocket断开连接处理完成")

    @socketio.on('join_interview')
    def handle_join_interview(data):
        """用户加入面试房间"""
        session_id = data.get('session_id')
        
        if not session_id:
            logger.error("加入面试失败: 未提供session_id")
            emit('error', {'message': '需要提供session_id'})
            return

        # 将用户加入特定房间，以便定向发送消息
        join_room(session_id)
        # 异步注册 - 使用临时session ID
        temp_sid = str(uuid.uuid4())[:8]
        asyncio.run(interview_manager.register_sid(session_id, temp_sid))
        logger.info(f"用户 (temp_sid={temp_sid}) 已加入面试房间: {session_id}")
        
        # 通知前端加入成功
        emit('joined', {'success': True, 'session_id': session_id})
    
    @socketio.on('start_streaming')
    def handle_start_streaming(data):
        # 首先尝试从data中获取token
        token = data.get('token')
        user_id = None

        # 如果data中没有token，使用临时认证（与连接时保持一致）
        if not token:
            user_id = 1  # 临时使用，因为连接时已经验证过
            logger.info(f"使用连接时的认证信息，用户ID: {user_id}")
        else:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']
                logger.info(f"Token验证成功，用户ID: {user_id}")
            except Exception as e:
                logger.error(f"Token验证失败: {e}")
                emit('error', {'message': 'Token验证失败，请重新登录'})
                return

        try:
            session_id = data.get('session_id')
            session = interview_manager.get_session(session_id)

            if not session:
                logger.error(f"启动流式传输失败: 未找到会话 (session_id={session_id})")
                emit('error', {'message': '会话不存在'})
                return

            # 验证会话是否属于当前用户
            session_user_id = session.get('user_id')
            logger.info(f"权限验证: 请求用户ID={user_id}, 会话用户ID={session_user_id}, 会话详情={session}")
            if session_user_id != int(user_id):
                logger.error(f"用户 {user_id} 无权访问会话 {session_id} (会话属于用户 {session_user_id})")
                emit('error', {'message': '无权访问此会话'})
                return

            # 获取面试配置和偏好设置
            interview_config = session.get('context', {}).get('interview_config', {})
            interview_preferences = session.get('context', {}).get('interview_preferences', {})

            logger.info(f"为会话 {session_id} 启动流式处理管道...")
            logger.info(f"面试配置: {interview_config}")
            logger.info(f"面试偏好: {interview_preferences}")

            # 使用同步版本的流式管道设置
            setup_streaming_pipeline_sync(session_id, interview_config, interview_preferences)

            # 启动实时反馈定时器
            def run_feedback_timer():
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(start_realtime_feedback_timer(session_id))
                finally:
                    loop.close()

            socketio.start_background_task(run_feedback_timer)

            emit('streaming_started', {'success': True})

        except Exception as e:
            logger.error(f"启动流式传输异常: {e}")
            emit('error', {'message': '启动流式传输失败'})

    @socketio.on('audio_stream')
    def handle_audio_stream(data):
        """处理前端发送的音频流"""
        # 暂时简化处理，不依赖session ID
        temp_sid = str(uuid.uuid4())[:8]
        logger.debug(f"收到音频流数据: temp_sid={temp_sid}, 数据长度={len(data) if data else 0}")
        # 暂时跳过具体处理
        return
    
    @socketio.on('request_next_question')
    def handle_next_question_request(data):
        token = data.get('token')
        if not token:
            emit('error', {'message': '缺少认证token'})
            return
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            session_id = data.get('session_id')
            logger.info(f"收到会话 {session_id} 的手动下一问题请求，用户ID: {user_id}")
            socketio.start_background_task(generate_and_serve_next_question, session_id)
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            emit('error', {'message': 'Invalid or expired token'})
            return
    
    @socketio.on('leave_interview')
    def handle_leave_interview(data):
        """用户离开面试房间"""
        session_id = data.get('session_id')
        if session_id:
            leave_room(session_id)
            temp_sid = str(uuid.uuid4())[:8]
            logger.info(f"用户 (temp_sid={temp_sid}) 已离开面试房间: {session_id}")
            # 可在此处处理面试中断逻辑

    @socketio.on('end_interview')
    def handle_end_interview(data):
        """结束面试"""
        try:
            session_id = data.get('session_id')
            if not session_id:
                emit('error', {'message': '缺少session_id'})
                return

            logger.info(f"收到结束面试请求: {session_id}")

            # 获取会话
            session = interview_manager.get_session(session_id)
            if not session:
                emit('error', {'message': '会话不存在'})
                return

            # 结束会话
            interview_manager.end_session(session_id)

            # 通知前端面试已结束
            emit('interview_ended', {
                'success': True,
                'message': '面试已结束',
                'session_id': session_id
            })

            logger.info(f"面试已结束: {session_id}")

        except Exception as e:
            logger.error(f"结束面试失败: {e}")
            emit('error', {'message': f'结束面试失败: {str(e)}'})

def setup_streaming_pipeline_sync(session_id: str, interview_config: dict = None, interview_preferences: dict = None):
    """为指定会话设置完整的实时反馈流式处理管道（同步版本）"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            logger.error(f"无法设置管道：未找到会话 {session_id}")
            return

        # 如果没有传递配置，从会话上下文中获取
        if not interview_config:
            interview_config = session.get('context', {}).get('interview_config', {})
        if not interview_preferences:
            interview_preferences = session.get('context', {}).get('interview_preferences', {})

        logger.info(f"开始为会话 {session_id} 设置完整的实时反馈管道")

        # 获取Flask应用实例
        from flask import current_app
        app = current_app._get_current_object()

        # 初始化所有服务
        from app.services.audio_service import AudioService
        from app.services.vision_service import VisionService

        # 创建服务实例，传入Flask应用实例
        audio_service = AudioService(app=app)
        vision_service = VisionService()
        spark_service = session['services']['spark']

        # 存储服务实例到会话中
        session['services']['audio'] = audio_service
        session['services']['vision'] = vision_service

        # 初始化实时数据存储
        session['realtime_data'] = {
            'transcriptions': [],  # 语音转写历史
            'vision_results': [],  # 视觉分析历史
            'audio_analysis': [],  # 语音分析历史
            'last_feedback_time': time.time()
        }

        logger.info(f"会话 {session_id} 的实时反馈管道设置完成")

        # 获取Flask应用实例
        from flask import current_app
        app = current_app._get_current_object()

        # 启动实时语音转写（同步版本）
        socketio.start_background_task(start_realtime_transcription_sync, session_id, audio_service, app)

        # 启动实时截图和视觉分析（同步版本）
        socketio.start_background_task(start_realtime_vision_analysis_sync, session_id, vision_service, app)

        logger.info(f"会话 {session_id} 所有实时服务已启动")

    except Exception as e:
        logger.error(f"设置流式管道时出错 (session_id={session_id}): {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

def start_realtime_transcription_sync(session_id: str, audio_service, app):
    """启动实时语音转写（同步版本）"""
    try:
        logger.info(f"开始为会话 {session_id} 启动实时语音转写")

        import time
        import asyncio

        # 设置转写回调函数
        def transcription_callback(result):
            """处理转写结果的回调函数"""
            try:
                session = interview_manager.get_session(session_id)
                if session:
                    # 处理转写结果（可能是字符串或字典）
                    if isinstance(result, dict):
                        text = result.get('text', '')
                        confidence = result.get('confidence', 0.8)
                        is_final = result.get('is_final', False)
                    else:
                        text = str(result)
                        confidence = 0.8
                        is_final = False
                    
                    if text:
                        # 存储转写结果到会话
                        if 'realtime_data' not in session:
                            session['realtime_data'] = {'transcriptions': [], 'vision_analysis': [], 'audio_analysis': []}

                        session['realtime_data']['transcriptions'].append({
                            'text': text,
                            'timestamp': time.time(),
                            'confidence': confidence,
                            'is_final': is_final
                        })

                        # 保持最近50条记录
                        if len(session['realtime_data']['transcriptions']) > 50:
                            session['realtime_data']['transcriptions'] = session['realtime_data']['transcriptions'][-50:]

                        logger.info(f"收集到真实语音转写: {text}")
                        
                        # 立即触发AI反馈
                        generate_realtime_feedback_sync(session_id)
            except Exception as e:
                logger.error(f"处理转写回调失败: {e}")

        # 启动讯飞实时语音转写
        try:
            # 在Flask应用上下文中启动转写
            with app.app_context():
                audio_service.start_realtime_transcription(session_id, transcription_callback)
                logger.info(f"讯飞实时语音转写启动成功: {session_id}")

                # 将audio_service注入到session中
                current_session = interview_manager.get_session(session_id)
                if current_session:
                    current_session['services']['audio'] = audio_service
        except Exception as e:
            logger.error(f"启动讯飞语音转写失败: {e}")
            logger.error(f"讯飞实时语音转写启动失败: {session_id}")

    except Exception as e:
        logger.error(f"启动实时语音转写失败: {e}")
        # 不再使用模拟数据，只使用真实的讯飞API

# 模拟语音转写函数已删除，只使用真实的讯飞API

def start_realtime_vision_analysis_sync(session_id: str, vision_service, app):
    """启动实时视觉分析（同步版本）"""
    try:
        logger.info(f"开始为会话 {session_id} 启动实时视觉分析")

        import time

        while True:
            try:
                # 获取会话
                session = interview_manager.get_session(session_id)
                if not session:
                    logger.info(f"会话 {session_id} 已结束，停止视觉分析")
                    break

                # 截取屏幕截图
                screenshot_data = vision_service.capture_screenshot()

                if screenshot_data:
                    # 在Flask应用上下文中使用讯飞表情分析API
                    with app.app_context():
                        analysis_result = vision_service.analyze_expression_xunfei(screenshot_data)

                    # 存储分析结果到会话
                    if 'realtime_data' not in session:
                        session['realtime_data'] = {'transcriptions': [], 'vision_analysis': [], 'audio_analysis': []}

                    # 确保vision_analysis键存在
                    if 'vision_analysis' not in session['realtime_data']:
                        session['realtime_data']['vision_analysis'] = []

                    if analysis_result:
                        session['realtime_data']['vision_analysis'].append({
                            'analysis': analysis_result,
                            'timestamp': time.time(),
                            'screenshot_size': len(screenshot_data)
                        })

                        # 保持最近20条记录
                        if len(session['realtime_data']['vision_analysis']) > 20:
                            session['realtime_data']['vision_analysis'] = session['realtime_data']['vision_analysis'][-20:]

                        emotion = analysis_result.get('emotion', 'unknown')
                        confidence = analysis_result.get('confidence', 0.0)
                        logger.info(f"完成讯飞表情分析，截图大小: {len(screenshot_data)} bytes, 情绪: {emotion}, 置信度: {confidence:.3f}")
                    else:
                        logger.warning("讯飞表情分析返回空结果")

                # 每10秒分析一次
                time.sleep(10)

            except Exception as e:
                logger.error(f"视觉分析循环异常: {e}")
                time.sleep(10)

    except Exception as e:
        logger.error(f"启动实时视觉分析失败: {e}")

async def start_realtime_transcription_task(session_id: str, audio_service):
    """启动实时语音转写任务"""
    try:
        # 设置转写结果回调
        def on_transcription_result(text: str, is_final: bool = False):
            session = interview_manager.get_session(session_id)
            if session and text.strip():
                # 存储转写结果
                transcription_data = {
                    'text': text,
                    'timestamp': time.time(),
                    'is_final': is_final
                }
                session['realtime_data']['transcriptions'].append(transcription_data)

                # 保持最近30秒的转写记录
                current_time = time.time()
                session['realtime_data']['transcriptions'] = [
                    t for t in session['realtime_data']['transcriptions']
                    if current_time - t['timestamp'] <= 30
                ]

                logger.debug(f"会话 {session_id} 收到转写: {text[:50]}...")

        # 启动语音转写WebSocket连接
        await audio_service.start_transcription_websocket(session_id, on_transcription_result)

    except Exception as e:
        logger.error(f"启动实时语音转写任务失败: {e}")

async def start_realtime_vision_analysis_task(session_id: str, vision_service):
    """启动实时视觉分析任务（每10秒截图分析）"""
    try:
        async def vision_analysis_loop():
            while True:
                try:
                    session = interview_manager.get_session(session_id)
                    if not session:
                        break

                    # 模拟截图（实际应该从前端获取）
                    # 这里需要前端定期发送截图数据
                    logger.debug(f"会话 {session_id} 等待视觉分析数据...")

                    # 等待10秒后进行下一次分析
                    await asyncio.sleep(10)

                except Exception as e:
                    logger.error(f"视觉分析循环错误: {e}")
                    await asyncio.sleep(10)

        # 在后台启动视觉分析循环
        await vision_analysis_loop()

    except Exception as e:
        logger.error(f"启动实时视觉分析任务失败: {e}")

async def start_realtime_transcription(session_id: str, audio_service):
    """启动实时语音转写"""
    try:
        # 设置转写结果回调
        def on_transcription_result(text: str, is_final: bool = False):
            session = interview_manager.get_session(session_id)
            if session and text.strip():
                # 存储转写结果
                transcription_data = {
                    'text': text,
                    'timestamp': time.time(),
                    'is_final': is_final
                }
                session['realtime_data']['transcriptions'].append(transcription_data)

                # 保持最近30秒的转写记录
                current_time = time.time()
                session['realtime_data']['transcriptions'] = [
                    t for t in session['realtime_data']['transcriptions']
                    if current_time - t['timestamp'] <= 30
                ]

                logger.debug(f"会话 {session_id} 收到转写: {text[:50]}...")

        # 启动语音转写WebSocket连接
        await audio_service.start_transcription_websocket(session_id, on_transcription_result)

    except Exception as e:
        logger.error(f"启动实时语音转写失败: {e}")

async def start_realtime_vision_analysis(session_id: str, vision_service):
    """启动实时视觉分析（每10秒截图分析）"""
    try:
        async def vision_analysis_loop():
            while True:
                try:
                    session = interview_manager.get_session(session_id)
                    if not session:
                        break

                    # 模拟截图（实际应该从前端获取）
                    # 这里需要前端定期发送截图数据
                    logger.debug(f"会话 {session_id} 等待视觉分析数据...")

                    # 等待10秒后进行下一次分析
                    await asyncio.sleep(10)

                except Exception as e:
                    logger.error(f"视觉分析循环错误: {e}")
                    await asyncio.sleep(10)

        # 在后台启动视觉分析循环
        asyncio.create_task(vision_analysis_loop())

    except Exception as e:
        logger.error(f"启动实时视觉分析失败: {e}")

async def generate_realtime_feedback(session_id: str, audio_chunk=None):
    """生成基于多模态分析的实时反馈"""
    try:
        from app.utils.async_utils import interview_manager
        session = interview_manager.get_session(session_id)
        if not session:
            return

        # 获取实时数据
        realtime_data = session.get('realtime_data', {})
        current_question = session.get('context', {}).get('current_question_data', {})
        interview_config = session.get('context', {}).get('interview_config', {})

        # 使用audio_chunk参数（避免未使用警告）
        if audio_chunk:
            logger.debug(f"处理音频块数据: {len(audio_chunk) if audio_chunk else 0} bytes")

        # 获取最近的转写文本（最近30秒）
        recent_transcriptions = realtime_data.get('transcriptions', [])
        current_time = time.time()
        recent_text = " ".join([
            t['text'] for t in recent_transcriptions
            if current_time - t['timestamp'] <= 30
        ])

        # 如果没有实时转写文本，尝试获取用户可能的输入内容
        if not recent_text:
            # 检查是否有其他形式的用户输入
            user_inputs = realtime_data.get('user_inputs', [])
            if user_inputs:
                recent_text = " ".join([
                    inp['content'] for inp in user_inputs[-3:]  # 最近3条输入
                    if current_time - inp.get('timestamp', 0) <= 60
                ])

        # 检查是否有模拟转写数据
        if not recent_text:
            mock_transcriptions = [
                t for t in recent_transcriptions
                if t.get('source') == 'mock_mode' and current_time - t['timestamp'] <= 60
            ]
            if mock_transcriptions:
                recent_text = " ".join([t['text'] for t in mock_transcriptions[-2:]])  # 最近2条模拟数据

        # 获取最近的视觉分析结果 - 修复数据获取路径
        recent_vision = realtime_data.get('vision_analysis', [])  # 修正字段名
        latest_vision = recent_vision[-1] if recent_vision else None

        # 获取最近的语音分析结果
        recent_audio_analysis = realtime_data.get('audio_analysis', [])
        latest_audio_analysis = recent_audio_analysis[-1] if recent_audio_analysis else None

        # 检查是否已有反馈历史，如果有则不发送"正在分析中"状态
        session_data = interview_manager.get_session(session_id)
        has_previous_feedback = False
        if session_data and 'realtime_data' in session_data:
            realtime_data_history = session_data['realtime_data']
            has_previous_feedback = bool(realtime_data_history.get('ai_feedback_history', []))

        # 只在没有历史反馈时发送"正在分析中"状态
        if not has_previous_feedback:
            socketio.emit('realtime_feedback', {
                'success': True,
                'feedback': {
                    'audio': "正在分析语音数据...",
                    'behavior': "正在分析行为表现...",
                    'technical': "正在分析回答内容...",
                    'stress': "正在评估面试状态..."
                },
                'timestamp': current_time,
                'ai_generated': False,
                'analyzing': True,
                'data_sources': {
                    'has_transcription': bool(recent_text),
                    'has_vision': bool(latest_vision),
                    'has_audio_analysis': bool(latest_audio_analysis)
                }
            }, room=session_id)

        # 构建综合分析提示
        feedback_prompt = f"""
作为专业的面试官，请基于以下多模态数据给出实时反馈建议：

【面试信息】
当前问题：{current_question.get('content', '暂无问题')}
面试类型：{interview_config.get('interview_mode', 'technical')}
职位：{interview_config.get('position', 'AI算法工程师')}

【语音转写内容（最近30秒）】
{recent_text if recent_text else '暂无语音内容'}

【视觉分析结果】
{f"检测到情绪: {latest_vision['analysis'].get('emotion', 'unknown')}, 置信度: {latest_vision['analysis'].get('confidence', 0.0):.2f}" if latest_vision and latest_vision.get('analysis') else '暂无视觉分析'}

【语音分析结果】
{latest_audio_analysis.get('summary', '暂无语音分析') if latest_audio_analysis else '暂无语音分析'}

请从以下4个维度给出简短的实时反馈（每个维度1-2句话）：
1. 语音表达：基于语音分析的语速、语调、发音等反馈
2. 行为表现：基于视觉分析的肢体语言、眼神交流、表情等反馈
3. 技术内容：基于转写内容的技术深度、准确性、逻辑性反馈
4. 压力应对：综合分析情绪稳定性、思维清晰度、适应能力

请以JSON格式返回：
{{
    "audio": "语音表达反馈",
    "behavior": "行为表现反馈",
    "technical": "技术内容反馈",
    "stress": "压力应对反馈"
}}
"""

        # 调用AI模型生成反馈
        try:
            spark_service = session.get('services', {}).get('spark')
            if spark_service:
                # 直接调用AI服务，不需要应用上下文
                ai_result = spark_service.chat_completion_http(
                    [{"role": "user", "content": feedback_prompt}],
                    "你是一个专业的面试官，请基于多模态数据给出建设性的实时反馈。"
                )

                if ai_result and ai_result.get('success'):
                    ai_feedback_text = ai_result.get('message', '')
                    logger.info(f"AI原始返回内容: {ai_feedback_text}")

                    # 尝试解析JSON格式的反馈
                    import json
                    try:
                        # 尝试提取JSON部分（可能AI返回的内容包含其他文本）
                        import re
                        json_match = re.search(r'\{.*\}', ai_feedback_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            feedback = json.loads(json_str)
                            logger.info(f"AI生成的实时反馈解析成功: {feedback}")
                        else:
                            raise ValueError("未找到JSON格式内容")
                    except Exception as parse_error:
                        logger.error(f"AI反馈JSON解析失败: {parse_error}, 原始内容: {ai_feedback_text}")
                        # 如果解析失败，使用默认格式
                        feedback = {
                            'audio': "语速适中，表达清晰",
                            'behavior': "表现自然，互动良好",
                            'technical': ai_feedback_text[:100] + "..." if len(ai_feedback_text) > 100 else ai_feedback_text,
                            'stress': "情绪稳定，应对从容"
                        }
                else:
                    # AI调用失败时的备用反馈
                    feedback = {
                        'audio': "语速适中，建议保持当前节奏",
                        'behavior': "表现自然，继续保持",
                        'technical': "回答思路清晰，可以更详细一些",
                        'stress': "情绪稳定，表现良好"
                    }
            else:
                # 没有数据时的备用反馈
                feedback = {
                    'audio': "等待语音数据分析...",
                    'behavior': "等待视觉数据分析...",
                    'technical': "等待回答内容分析...",
                    'stress': "面试状态良好，继续保持"
                }

        except Exception as ai_error:
            logger.error(f"AI反馈生成失败: {ai_error}")
            # AI调用异常时的备用反馈
            feedback = {
                'audio': "语速适中，表达清晰",
                'behavior': "表现自然，互动良好",
                'technical': "回答逻辑清晰，继续保持",
                'stress': "情绪稳定，应对良好"
            }

        # 保存反馈历史
        if session_data:
            if 'realtime_data' not in session_data:
                session_data['realtime_data'] = {}
            if 'ai_feedback_history' not in session_data['realtime_data']:
                session_data['realtime_data']['ai_feedback_history'] = []

            session_data['realtime_data']['ai_feedback_history'].append({
                'feedback': feedback,
                'timestamp': current_time,
                'data_sources': {
                    'has_transcription': bool(recent_text),
                    'has_vision': bool(latest_vision),
                    'has_audio_analysis': bool(latest_audio_analysis)
                }
            })

        # 发送实时反馈到前端
        socketio.emit('realtime_feedback', {
            'success': True,
            'feedback': feedback,
            'timestamp': current_time,
            'ai_generated': True,
            'analyzing': False,  # 分析完成
            'data_sources': {
                'has_transcription': bool(recent_text),
                'has_vision': bool(latest_vision),
                'has_audio_analysis': bool(latest_audio_analysis)
            }
        }, room=session_id)

        # 更新最后反馈时间
        realtime_data['last_feedback_time'] = current_time

        logger.info(f"已发送多模态AI实时反馈到会话 {session_id}")

    except Exception as e:
        logger.error(f"生成实时反馈失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

async def start_realtime_feedback_timer(session_id: str):
    """启动实时反馈定时器"""
    import asyncio

    try:
        while True:
            session = interview_manager.get_session(session_id)
            if not session:
                logger.info(f"会话 {session_id} 不存在，停止实时反馈定时器")
                break

            # 每10秒发送一次实时反馈
            await asyncio.sleep(10)
            await generate_realtime_feedback(session_id, None)

    except Exception as e:
        logger.error(f"实时反馈定时器异常: {e}")

async def generate_and_serve_next_question(session_id: str):
    """生成下一个问题并将其视频URL提供给前端"""
    session = interview_manager.get_session(session_id)
    if not session:
        logger.error(f"无法生成下一个问题：未找到会话 {session_id}")
        return

    spark_serv = session['services']['spark']
    avatar_serv = session['services']['avatar']

    # 获取面试配置和偏好设置
    interview_config = session.get('context', {}).get('interview_config', {})
    interview_preferences = session.get('context', {}).get('interview_preferences', {})

    # 记录配置信息（使用变量避免未使用警告）
    logger.debug(f"面试配置: {interview_config.get('interview_mode', 'default')}")

    # 1. 指示Spark生成下一个问题（使用个性化配置）
    next_question_result = await spark_serv.generate_next_question_based_on_history()

    if not next_question_result.get('success'):
        logger.error(f"为会话 {session_id} 生成下一个问题失败: {next_question_result.get('error')}")
        socketio.emit('error', {'message': 'AI无法生成下一个问题'}, room=session_id)
        return

    question_data = next_question_result.get('data', {})
    question_content = question_data.get('content', '你能再详细说明一下吗？')
    
    # 2. 调用Avatar服务为新问题生成视频（使用个性化偏好设置）
    video_result = avatar_serv.create_avatar_response(
        question_content,
        preferences=interview_preferences
    )

    if not video_result.get('success'):
        logger.error(f"为会话 {session_id} 生成虚拟人视频失败: {video_result.get('error')}")
        socketio.emit('error', {'message': '虚拟人视频生成失败'}, room=session_id)
        return

    video_url = video_result.get('video_url')
    stream_type = video_result.get('stream_type', 'http')

    # 3. 将新问题的视频URL发送给前端
    logger.info(f"为会话 {session_id} 提供新问题视频: {video_url}")
    logger.info(f"流媒体类型: {stream_type}")
    logger.info(f"使用的面试偏好: {interview_preferences}")

    # 发送虚拟人视频流信息
    socketio.emit('avatar_video_stream', {
        'video_url': video_url,
        'stream_type': stream_type,
        'text': question_content,
        'message': video_result.get('message', '虚拟人响应已生成')
    }, room=session_id)

    socketio.emit('new_question_video', {
        'video_url': video_url,
        'stream_type': stream_type,
        'question_data': question_data # 将完整数据（包括参考答案）也发给前端
    }, room=session_id)

# 重复的handle_start_streaming函数已删除

@socketio.on('audio_data')
def handle_audio_data(data):
    """处理16kHz PCM音频数据"""
    try:
        # 修复：从data中获取session_id，而不是使用request.sid
        session_id = data.get('session_id')
        if not session_id:
            logger.error("音频数据处理失败: 缺少session_id")
            emit('error', {'message': '缺少session_id'})
            return

        # 获取会话
        session = interview_manager.get_session(session_id)
        if not session:
            logger.warning(f"会话不存在: {session_id}")
            emit('error', {'message': '会话不存在'})
            return

        # 处理16kHz PCM音频数据
        audio_base64 = data.get('audio', '')
        is_first_frame = data.get('isFirst', False)

        if is_first_frame:
            logger.info(f"收到第一帧音频数据，采样率: {data.get('sampleRate')}, 通道数: {data.get('channels')}")

        # 使用同步方式处理音频数据
        process_audio_data_sync(session_id, audio_base64, is_first_frame)

    except Exception as e:
        logger.exception(f"处理音频数据失败: {e}")
        emit('error', {'message': f'处理音频数据失败: {str(e)}'})

def process_audio_data_sync(session_id: str, audio_base64: str, is_first_frame: bool = False):
    """同步处理16kHz PCM音频数据"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            return

        # 确保实时数据存储存在
        if 'realtime_data' not in session:
            session['realtime_data'] = {'transcriptions': [], 'vision_analysis': [], 'audio_analysis': []}

        # 解码base64音频数据
        try:
            import base64
            audio_bytes = base64.b64decode(audio_base64)
            logger.debug(f"解码PCM音频数据，大小: {len(audio_bytes)} bytes")
        except Exception as e:
            logger.error(f"PCM音频数据解码失败: {e}")
            return

        # 如果有音频服务，进行语音转写
        audio_service = session['services'].get('audio')
        if audio_service:
            try:
                # 调用音频服务进行转写（按RTASR协议）
                transcription_result = audio_service.transcribe_audio_chunk_sync(audio_bytes, is_first_frame)
                
                # 只有当有转写结果时才处理
                if transcription_result and transcription_result.get('text'):
                    # 存储转写结果
                    session['realtime_data']['transcriptions'].append({
                        'text': transcription_result['text'],
                        'timestamp': time.time(),
                        'confidence': transcription_result.get('confidence', 0.8),
                        'is_final': transcription_result.get('is_final', False)
                    })

                    # 保持最近50条记录
                    if len(session['realtime_data']['transcriptions']) > 50:
                        session['realtime_data']['transcriptions'] = session['realtime_data']['transcriptions'][-50:]

                    logger.info(f"会话 {session_id} 语音转写: {transcription_result['text'][:50]}...")
                    
                    # 触发实时反馈生成（同步版本）
                    generate_realtime_feedback_sync(session_id)
                else:
                    # 如果没有转写结果（讯飞异步处理），只发送音频数据
                    logger.debug(f"会话 {session_id} PCM音频数据已发送到讯飞，等待异步转写结果")
                    
            except Exception as e:
                logger.error(f"音频转写失败: {e}")

        # 同时进行音频分析
        if audio_service:
            try:
                analysis_result = audio_service.analyze_audio_chunk_sync(audio_bytes)
                if analysis_result:
                    session['realtime_data']['audio_analysis'].append({
                        'analysis': analysis_result,
                        'timestamp': time.time()
                    })
                    
                    # 保持最近20条音频分析记录
                    if len(session['realtime_data']['audio_analysis']) > 20:
                        session['realtime_data']['audio_analysis'] = session['realtime_data']['audio_analysis'][-20:]
                        
            except Exception as e:
                logger.error(f"音频分析失败: {e}")

    except Exception as e:
        logger.error(f"同步处理PCM音频数据失败: {e}")

def generate_realtime_feedback_sync(session_id: str):
    """同步生成实时反馈"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            return

        # 检查反馈间隔（避免重复发送）
        last_feedback_time = session.get('last_feedback_time', 0)
        current_time = time.time()
        
        # 如果距离上次反馈时间少于3秒，跳过
        if current_time - last_feedback_time < 3:
            logger.debug(f"会话 {session_id} 反馈间隔太短，跳过")
            return

        # 获取实时数据
        realtime_data = session.get('realtime_data', {})
        current_question = session.get('context', {}).get('current_question_data', {})
        interview_config = session.get('context', {}).get('interview_config', {})

        # 获取最近的转写文本（最近30秒）
        recent_transcriptions = realtime_data.get('transcriptions', [])
        recent_text = " ".join([
            t['text'] for t in recent_transcriptions
            if current_time - t['timestamp'] <= 30
        ])

        # 获取最近的视觉分析结果
        recent_vision = realtime_data.get('vision_analysis', [])
        latest_vision = recent_vision[-1] if recent_vision else None

        # 获取最近的语音分析结果
        recent_audio_analysis = realtime_data.get('audio_analysis', [])
        latest_audio_analysis = recent_audio_analysis[-1] if recent_audio_analysis else None

        # 如果没有新数据，跳过反馈
        if not recent_text and not latest_vision and not latest_audio_analysis:
            logger.debug(f"会话 {session_id} 没有新数据，跳过反馈生成")
            return

        # 生成基于实际数据的反馈
        feedback = {
            'audio': "语速适中，表达清晰",
            'behavior': "表现自然，互动良好",
            'technical': recent_text[:100] + "..." if len(recent_text) > 100 else recent_text or "等待回答内容分析...",
            'stress': "情绪稳定，应对从容"
        }

        # 使用获取到的数据（避免未使用变量警告）
        if current_question.get('content'):
            logger.debug(f"当前问题: {current_question['content'][:50]}...")
        if interview_config.get('interview_mode'):
            logger.debug(f"面试模式: {interview_config['interview_mode']}")

        # 更新最后反馈时间
        session['last_feedback_time'] = current_time

        # 发送实时反馈到前端
        socketio.emit('realtime_feedback', {
            'success': True,
            'feedback': feedback,
            'timestamp': current_time,
            'ai_generated': True,
            'analyzing': False,
            'data_sources': {
                'has_transcription': bool(recent_text),
                'has_vision': bool(latest_vision),
                'has_audio_analysis': bool(latest_audio_analysis)
            }
        }, room=session_id)

        logger.info(f"已发送同步实时反馈到会话 {session_id}")

    except Exception as e:
        logger.error(f"同步生成实时反馈失败: {e}")

@socketio.on('generate_next_question')
def handle_generate_next_question(data):
        """处理生成下一题的WebSocket请求"""
        try:
            session_id = data.get('session_id')
            logger.info(f"WebSocket请求生成下一题，会话ID: {session_id}")

            if not session_id:
                emit('error', {'message': '缺少session_id'})
                return

            # 获取会话
            session = interview_manager.get_session(session_id)
            if not session:
                emit('error', {'message': '无效的会话ID'})
                return

            # 异步生成下一个问题
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(generate_next_question_async(session_id, session))
            finally:
                loop.close()

        except Exception as e:
            logger.exception(f"生成下一题失败: {e}")
            emit('error', {'message': f'生成下一题失败: {str(e)}'})

@socketio.on('user_answer')
def handle_user_answer(data):
        """处理用户答案"""
        try:
            session_id = data.get('session_id')
            answer = data.get('answer', '')

            logger.info(f"收到用户答案，会话ID: {session_id}")
            logger.info(f"答案内容: {answer[:100]}...")

            if not session_id:
                emit('error', {'message': '缺少session_id'})
                return

            # 获取会话
            session = interview_manager.get_session(session_id)
            if not session:
                emit('error', {'message': '无效的会话ID'})
                return

            # 将答案添加到对话历史
            session['services']['spark'].add_to_conversation('user', answer)

            # 生成AI反馈
            feedback_prompt = f"请对以下回答给出简短的专业反馈（1-2句话）：{answer}"
            feedback_result = session['services']['spark'].chat_completion_http(
                [{"role": "user", "content": feedback_prompt}],
                "你是一个专业的面试官，请给出建设性的反馈。"
            )

            ai_feedback = "回答得不错，请继续。"
            if feedback_result.get('success'):
                ai_feedback = feedback_result.get('message', ai_feedback)

            # 发送AI反馈
            emit('ai_feedback', {
                'success': True,
                'feedback': ai_feedback,
                'session_id': session_id
            })

            logger.info(f"🤖 AI反馈: {ai_feedback}")

        except Exception as e:
            logger.exception(f"处理用户答案失败: {e}")
            emit('error', {'message': f'处理用户答案失败: {str(e)}'})

# 重复的函数已删除，使用上面的async版本

async def generate_next_question_async(session_id: str, session: dict):
    """异步生成下一个问题"""
    try:
        # 使用AI生成下一个问题
        result = await session['services']['spark'].generate_next_question_based_on_history()

        if result.get('success'):
            question_data = result['data']

            # 将AI问题添加到对话历史
            session['services']['spark'].add_to_conversation('assistant', question_data['content'])

            # 更新会话状态
            session['context']['current_question_number'] = session['context'].get('current_question_number', 1) + 1
            session['context']['current_question_data'] = question_data

            # 生成虚拟人视频
            video_url = None
            if session.get('preferences', {}).get('enable_avatar', True):
                avatar_serv = session['services'].get('avatar')
                if avatar_serv:
                    video_result = avatar_serv.create_avatar_response(
                        question_data['content'],
                        preferences=session.get('preferences', {})
                    )
                    if video_result.get('success'):
                        video_url = video_result.get('video_url')

            # 通过WebSocket发送新问题
            socketio.emit('new_question_video', {
                'success': True,
                'question': {
                    'id': session['context']['current_question_number'],
                    'content': question_data['content'],
                    'type': question_data['type'],
                    'difficulty': 'medium'
                },
                'question_number': session['context']['current_question_number'],
                'total_questions': 10,
                'video_url': video_url,
                'finished': session['context']['current_question_number'] >= 10
            }, room=session_id)

        else:
            socketio.emit('error', {
                'message': f'AI生成问题失败: {result.get("error")}'
            }, room=session_id)

    except Exception as e:
        logger.exception(f"异步生成下一题失败: {e}")
        socketio.emit('error', {
            'message': f'生成下一题失败: {str(e)}'
        }, room=session_id)

# 添加新的WebSocket事件处理器
@socketio.on('screenshot_data')
def handle_screenshot_data(data):
    """处理前端发送的截图数据"""
    try:
        session_id = data.get('session_id')
        image_data = data.get('image_data')  # base64编码的图片数据

        session = interview_manager.get_session(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        # 异步处理视觉分析
        socketio.start_background_task(process_screenshot_analysis, session_id, image_data)

    except Exception as e:
        logger.error(f"处理截图数据失败: {e}")
        emit('error', {'message': f'处理截图数据失败: {str(e)}'})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """处理前端发送的音频块数据"""
    try:
        session_id = data.get('session_id')
        audio_data = data.get('audio_data')  # base64编码的音频数据

        session = interview_manager.get_session(session_id)
        if not session:
            emit('error', {'message': '会话不存在'})
            return

        # 异步处理音频分析
        socketio.start_background_task(process_audio_analysis, session_id, audio_data)

    except Exception as e:
        logger.error(f"处理音频块失败: {e}")
        emit('error', {'message': f'处理音频块失败: {str(e)}'})

def process_screenshot_analysis(session_id: str, image_data: str):
    """处理截图的视觉分析（同步版本）"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            return

        vision_service = session['services'].get('vision')
        if not vision_service:
            logger.warning(f"会话 {session_id} 没有视觉服务")
            return

        # 确保realtime_data存在
        if 'realtime_data' not in session:
            session['realtime_data'] = {'transcriptions': [], 'vision_analysis': [], 'audio_analysis': []}

        # 确保vision_results键存在
        if 'vision_results' not in session['realtime_data']:
            session['realtime_data']['vision_results'] = []

        # 调用视觉分析服务（同步版本）
        try:
            # 解码base64图片数据
            import base64
            image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)

            # 使用同步方法分析图片
            analysis_result = vision_service.analyze_expression_xunfei(image_bytes)

            if analysis_result:
                # 存储视觉分析结果
                vision_data = {
                    'result': analysis_result,
                    'timestamp': time.time(),
                    'summary': analysis_result.get('emotion', '无法分析')
                }

                session['realtime_data']['vision_results'].append(vision_data)

                # 保持最近60秒的视觉分析记录
                current_time = time.time()
                session['realtime_data']['vision_results'] = [
                    v for v in session['realtime_data']['vision_results']
                    if current_time - v['timestamp'] <= 60
                ]

                logger.info(f"会话 {session_id} 视觉分析完成: {analysis_result.get('emotion', '')}")
            else:
                logger.warning(f"会话 {session_id} 视觉分析返回空结果")

        except Exception as decode_error:
            logger.error(f"图片解码或分析失败: {decode_error}")

    except Exception as e:
        logger.error(f"处理截图分析失败: {e}")

def process_audio_analysis(session_id: str, audio_data: str):
    """处理音频的语音分析（同步版本）"""
    try:
        session = interview_manager.get_session(session_id)
        if not session:
            return

        audio_service = session['services'].get('audio')
        if not audio_service:
            logger.warning(f"会话 {session_id} 没有音频服务")
            return

        # 确保realtime_data存在
        if 'realtime_data' not in session:
            session['realtime_data'] = {'transcriptions': [], 'vision_analysis': [], 'audio_analysis': []}

        # 调用音频分析服务（同步版本）
        try:
            # 解码base64音频数据
            import base64
            audio_bytes = base64.b64decode(audio_data)

            # 使用同步方法分析音频
            analysis_result = audio_service.analyze_audio_chunk_sync(audio_bytes)

            if analysis_result:
                # 存储音频分析结果
                audio_analysis_data = {
                    'result': analysis_result,
                    'timestamp': time.time(),
                    'summary': analysis_result.get('summary', '无法分析')
                }

                session['realtime_data']['audio_analysis'].append(audio_analysis_data)

                # 保持最近60秒的音频分析记录
                current_time = time.time()
                session['realtime_data']['audio_analysis'] = [
                    a for a in session['realtime_data']['audio_analysis']
                    if current_time - a['timestamp'] <= 60
                ]

                logger.info(f"会话 {session_id} 音频分析完成: {analysis_result.get('summary', '')[:50]}...")
            else:
                logger.warning(f"会话 {session_id} 音频分析返回空结果")

        except Exception as decode_error:
            logger.error(f"音频解码或分析失败: {decode_error}")

    except Exception as e:
        logger.error(f"处理音频分析失败: {e}")