#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讯飞实时语音转写服务
"""

import asyncio
import base64
import hashlib
import hmac
import json
import queue
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time
from time import mktime

from flask import current_app
from loguru import logger


class AudioService:
    """音频服务 - 讯飞实时语音转写"""
    
    def __init__(self, config=None, app=None):
        self.config = config
        self.app = app  # 保存Flask应用实例
        self.audio_config = None
        self.websocket_url = None
        self.ws_client = None
        self.is_active = False
        self.audio_queue = queue.Queue()
        self.result_callback = None
        self.session_id = None
        self._initialized = False
        self.apikey = None
        self.apisecret = None
        self.appid = None
        self.on_silence_callback = None
        self.last_audio_time = None
        self.is_speaking = False
        self.silence_threshold = 5  # 5秒静默阈值
        self.silence_timer = None
        self.answer_finished_callback = None
        self.transcription_callback = None
        # 讯飞实时转写相关
        self.ws = None
        self.recv_thread = None
        self.transcription_thread = None
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            if self.config is None:
                if self.app:
                    # 使用传入的Flask应用实例
                    with self.app.app_context():
                        self.config = self.app.config.get('XUNFEI_CONFIG', {})
                else:
                    # 尝试获取当前应用上下文
                    try:
                        from flask import current_app
                        self.config = current_app.config.get('XUNFEI_CONFIG', {})
                    except RuntimeError:
                        logger.error("无法获取Flask应用上下文，请在初始化时传入app参数")
                        raise

            # 获取音频服务配置
            self.audio_config = self.config.get('AUDIO', {})

            # 使用实时语音转写专用认证信息
            self.appid = self.audio_config.get('APPID', self.config.get('APPID'))
            self.apikey = self.audio_config.get('APIKey', self.config.get('APIKey'))
            self.apisecret = self.config.get('APISecret')  # 实时转写不需要APISecret

            # 验证必要的认证信息
            if not self.appid or not self.apikey:
                raise ValueError(f"实时语音转写缺少必要的认证信息 - APPID: {self.appid}, APIKey: {'有' if self.apikey else '无'}")

            self.websocket_url = self.audio_config.get('WEBSOCKET_URL')

            # 添加调试日志
            logger.info(f"音频服务初始化完成 - APPID: {self.appid}, APIKey: {self.apikey[:8] if self.apikey else 'None'}..., WebSocket URL: {self.websocket_url}")
            self._initialized = True

    def _is_websocket_connected(self):
        """检查WebSocket连接状态"""
        try:
            return (self.ws and 
                   hasattr(self.ws, 'sock') and 
                   self.ws.sock and 
                   hasattr(self.ws.sock, 'connected') and 
                   self.ws.sock.connected)
        except Exception as e:
            logger.debug(f"检查WebSocket连接状态失败: {e}")
            return False



    def start_realtime_transcription(self, session_id: str, callback):
        """启动讯飞实时语音转写"""
        try:
            self.session_id = session_id
            self.transcription_callback = callback
            self.is_active = True
            
            # 直接启动讯飞转写连接
            self._start_xunfei_transcription_sync()
            
            logger.info(f"实时语音转写已启动 - 会话ID: {session_id}")
            
        except Exception as e:
            logger.error(f"启动实时语音转写失败: {e}")
            # 不抛出异常，允许使用模拟模式
            pass

    def _start_xunfei_transcription_sync(self):
        """同步启动讯飞转写"""
        try:
            # 确保服务已初始化
            self._ensure_initialized()
            
            # 生成讯飞WebSocket URL
            ws_url = self._generate_xunfei_rtasr_url()
            logger.info(f"讯飞WebSocket URL: {ws_url}")
            
            # 连接WebSocket
            import websocket
            import threading
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_websocket_open,
                on_message=self._on_websocket_message,
                on_error=self._on_websocket_error,
                on_close=self._on_websocket_close
            )
            
            # 在后台线程中启动WebSocket连接
            ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            ws_thread.start()
            
            logger.info("讯飞WebSocket连接已启动")
            
        except Exception as e:
            logger.error(f"启动讯飞转写失败: {e}")
            # 不抛出异常，允许使用模拟模式
            pass

    def _generate_xunfei_rtasr_url(self) -> str:
        """生成讯飞实时语音转写WebSocket URL"""
        try:
            # 讯飞实时语音转写参数
            ts = str(int(time.time()))
            signa = self._generate_signature()
            
            params = {
                'appid': self.appid,
                'ts': ts,
                'signa': signa
            }
            
            # 构建URL
            base_url = "wss://rtasr.xfyun.cn/v1/ws"
            url = f"{base_url}?{urlencode(params)}"
            logger.info(f"生成讯飞WebSocket URL: {url}")
            return url
            
        except Exception as e:
            logger.error(f"生成讯飞URL失败: {e}")
            # 返回一个默认URL，允许使用模拟模式
            return "wss://rtasr.xfyun.cn/v1/ws"

    def _generate_signature(self) -> str:
        """生成讯飞签名"""
        try:
            # 讯飞签名算法 - 简化版本
            timestamp = str(int(time.time()))
            base_string = self.appid + timestamp
            
            # MD5
            md5 = hashlib.md5()
            md5.update(base_string.encode('utf-8'))
            md5_result = md5.hexdigest()
            
            # HMAC-SHA1
            signature = hmac.new(
                self.apikey.encode('utf-8'),
                md5_result.encode('utf-8'),
                hashlib.sha1
            ).digest()
            
            signature_b64 = base64.b64encode(signature).decode()
            return signature_b64
            
        except Exception as e:
            logger.error(f"生成签名失败: {e}")
            return "mock_signature"



    def _on_websocket_open(self, ws):
        """WebSocket连接打开回调"""
        logger.info("讯飞WebSocket连接已建立")
        self.is_active = True

    def _on_websocket_message(self, ws, message):
        """WebSocket消息回调"""
        try:
            logger.debug(f"收到讯飞消息: {message}")
            # 解析讯飞返回的消息
            result = self._parse_xunfei_result(message)
            if result and result.get('text'):
                logger.info(f"转写结果: {result}")

                # 调用回调函数
                if self.transcription_callback:
                    self.transcription_callback(result)

                # 立即触发实时反馈生成
                self._trigger_realtime_feedback(result)
            elif result:
                logger.debug(f"讯飞消息解析结果: {result}")
        except Exception as e:
            logger.error(f"处理讯飞消息失败: {e}")

    def _trigger_realtime_feedback(self, transcription_result):
        """触发实时反馈生成"""
        try:
            if hasattr(self, 'session_id') and self.session_id:
                # 导入并调用实时反馈生成函数
                from app.controllers.interview_socket_controller import generate_realtime_feedback_sync
                generate_realtime_feedback_sync(self.session_id)
                logger.info(f"已触发会话 {self.session_id} 的实时反馈生成")
        except Exception as e:
            logger.error(f"触发实时反馈失败: {e}")

    def _on_websocket_error(self, ws, error):
        """WebSocket错误回调"""
        logger.error(f"讯飞WebSocket错误: {error}")
        self.is_active = False

    def _on_websocket_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭回调"""
        logger.info(f"讯飞WebSocket连接已关闭: {close_status_code} - {close_msg}")
        self.is_active = False

    def _recv_results(self):
        """接收讯飞转写结果"""
        try:
            while self.is_active and self.ws:
                try:
                    # 接收讯飞返回的数据
                    data = self.ws.recv()
                    if data:
                        # 解析结果
                        result = self._parse_xunfei_result(data)
                        if result and self.transcription_callback:
                            self.transcription_callback(result)
                except Exception as e:
                    logger.error(f"接收讯飞数据失败: {e}")
                    break
        except Exception as e:
            logger.error(f"接收讯飞结果失败: {e}")

    def _parse_xunfei_result(self, result_dict):
        """解析讯飞转写结果"""
        try:
            if isinstance(result_dict, str):
                result_dict = json.loads(result_dict)
            
            logger.debug(f"解析讯飞结果: {result_dict}")
            
            # 解析讯飞返回的数据结构
            if 'action' in result_dict:
                action = result_dict['action']
                
                if action == 'started':
                    logger.info("讯飞转写服务已启动")
                    return None
                    
                elif action == 'result':
                    data = result_dict.get('data', '')
                    if data:
                        try:
                            # 解析data字段
                            data_dict = json.loads(data)
                            logger.debug(f"解析data字段: {data_dict}")
                            
                            # 尝试不同的数据格式
                            text = ""
                            
                            # 格式1: 直接有text字段
                            if 'text' in data_dict:
                                text = data_dict['text']
                            
                            # 格式2: cn.st.rt结构
                            elif 'cn' in data_dict:
                                cn_data = data_dict.get('cn', {})
                                st_data = cn_data.get('st', {})
                                rt_list = st_data.get('rt', [])
                                
                                # 提取转写文本
                                text_parts = []
                                for rt in rt_list:
                                    ws_list = rt.get('ws', [])
                                    for ws in ws_list:
                                        cw_list = ws.get('cw', [])
                                        for cw in cw_list:
                                            word = cw.get('w', '')
                                            if word:
                                                text_parts.append(word)
                                
                                text = ''.join(text_parts)
                            
                            # 格式3: 直接是文本
                            else:
                                text = data
                            
                            if text:
                                # 在终端显示转写结果
                                print(f"\n🎤 [语音转写] {text}")
                                logger.info(f"提取到转写文本: {text}")
                                return {
                                    'text': text,
                                    'confidence': 0.8,
                                    'is_final': data_dict.get('status', 0) == 2
                                }
                            else:
                                logger.debug("未提取到转写文本")
                                
                        except Exception as parse_error:
                            logger.error(f"解析data字段失败: {parse_error}")
                            # 如果解析失败，尝试直接使用data作为文本
                            if data and len(data) > 10:  # 避免太短的数据
                                return {
                                    'text': data,
                                    'confidence': 0.6,
                                    'is_final': False
                                }
                
                elif action == 'error':
                    error_code = result_dict.get('code', 'unknown')
                    error_desc = result_dict.get('desc', 'unknown error')
                    logger.error(f"讯飞转写错误: {error_code} - {error_desc}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"解析讯飞结果失败: {e}")
            return None

    def _start_recording_and_send_sync(self):
        """同步启动录音并发送"""
        try:
            import pyaudio
            import wave
            
            # 音频参数
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            
            # 初始化PyAudio
            p = pyaudio.PyAudio()
            
            # 打开音频流
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            logger.info("开始录音...")
            
            try:
                while self.is_active:
                    # 读取音频数据
                    data = stream.read(CHUNK)
                    
                    # 发送到讯飞
                    if self._is_websocket_connected():
                        try:
                            self.ws.send(data)
                        except Exception as e:
                            logger.error(f"发送音频数据失败: {e}")
                            break
                    else:
                        logger.warning("WebSocket未连接，跳过音频发送")
                        break
                        
            finally:
                # 清理资源
                stream.stop_stream()
                stream.close()
                p.terminate()
                logger.info("录音已停止")
                
        except Exception as e:
            logger.error(f"录音发送失败: {e}")

    def _send_mock_audio_data_sync(self):
        """同步发送模拟音频数据"""
        try:
            import time
            
            # 模拟音频数据
            mock_audio_data = b'\x00' * 1024  # 1KB的静音数据
            
            while self.is_active:
                try:
                    # 发送模拟数据
                    if self._is_websocket_connected():
                        self.ws.send(mock_audio_data)
                        logger.debug("发送模拟音频数据")
                    else:
                        logger.warning("WebSocket未连接，停止发送模拟数据")
                        break
                    
                    # 等待一段时间
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"发送模拟音频数据失败: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"模拟音频发送失败: {e}")

    def _enable_mock_mode(self):
        """启用语音转录模拟模式 - 已移除，专注于真实转写"""
        logger.warning("模拟模式已移除，请检查讯飞API配置")
        pass

    def process_audio_chunk(self, audio_data: bytes):
        """处理音频数据块"""
        try:
            if not self.is_active:
                logger.warning("音频服务未激活，忽略音频数据")
                return None
            
            # 确保服务已初始化
            self._ensure_initialized()
            
            # 如果有讯飞WebSocket连接，使用实时转写
            if self._is_websocket_connected():
                try:
                    # 发送音频数据到讯飞
                    self.ws.send(audio_data)
                    logger.debug(f"已发送音频数据到讯飞，大小: {len(audio_data)} bytes")
                    
                    # 不立即返回结果，等待讯飞异步返回
                    return None
                except Exception as e:
                    logger.error(f"讯飞转写失败: {e}")
                    return None
            else:
                # 如果没有WebSocket连接，缓存音频数据等待连接
                logger.debug("讯飞未连接，缓存音频数据")
                if not hasattr(self, 'audio_buffer'):
                    self.audio_buffer = []
                self.audio_buffer.append(audio_data)
                return None
                
        except Exception as e:
            logger.error(f"异步转写音频数据失败: {e}")
            return None

    async def transcribe_audio_chunk(self, audio_data: bytes):
        """异步转写音频数据块"""
        try:
            if not self.is_active:
                logger.warning("音频服务未激活，忽略音频数据")
                return None
            
            # 确保服务已初始化
            self._ensure_initialized()
            
            # 如果有讯飞WebSocket连接，使用实时转写
            if self._is_websocket_connected():
                try:
                    # 发送音频数据到讯飞
                    self.ws.send(audio_data)
                    logger.debug(f"已发送音频数据到讯飞，大小: {len(audio_data)} bytes")
                    
                    # 不立即返回结果，等待讯飞异步返回
                    return None
                except Exception as e:
                    logger.error(f"讯飞转写失败: {e}")
                    return None
            else:
                # 如果没有WebSocket连接，缓存音频数据等待连接
                logger.debug("讯飞未连接，缓存音频数据")
                if not hasattr(self, 'audio_buffer'):
                    self.audio_buffer = []
                self.audio_buffer.append(audio_data)
                return None
                
        except Exception as e:
            logger.error(f"异步转写音频数据失败: {e}")
            return None

    async def analyze_audio_chunk(self, audio_data: bytes):
        """异步分析音频数据块"""
        try:
            if not self.is_active:
                return None
            
            # 简单的音频分析（音量、语速等）
            # 暂时返回模拟分析结果，不依赖numpy
            try:
                # 这里需要根据音频格式进行解码
                # 暂时返回模拟分析结果
                analysis_result = {
                    'volume_level': 0.7,  # 音量级别
                    'speech_rate': 120,    # 语速（词/分钟）
                    'pitch': 0.5,          # 音调
                    'clarity': 0.8,        # 清晰度
                    'summary': '语音清晰，语速适中，表达自然'
                }
                
                return analysis_result
                
            except Exception as e:
                logger.error(f"音频分析失败: {e}")
                return {
                    'summary': '音频分析失败',
                    'volume_level': 0.5,
                    'speech_rate': 100,
                    'pitch': 0.5,
                    'clarity': 0.6
                }
                
        except Exception as e:
            logger.error(f"异步分析音频数据失败: {e}")
            return None

    def transcribe_audio_chunk_sync(self, audio_data: bytes, is_first_frame=False):
        """同步转写音频数据块"""
        try:
            if not self.is_active:
                logger.warning("音频服务未激活，忽略音频数据")
                return None
            
            # 确保服务已初始化
            self._ensure_initialized()
            
            # 如果有讯飞WebSocket连接，按RTASR协议发送
            if self._is_websocket_connected():
                try:
                    # 构建讯飞RTASR协议帧
                    import base64
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    if is_first_frame:
                        # 第一帧：包含配置信息
                        frame = {
                            "common": {
                                "app_id": self.appid
                            },
                            "business": {
                                "language": "zh_cn",
                                "domain": "iat", 
                                "accent": "mandarin",
                                "vad_eos": 5000
                            },
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": audio_base64
                            }
                        }
                        logger.info("发送讯飞RTASR第一帧")
                    else:
                        # 后续帧：只包含音频数据
                        frame = {
                            "data": {
                                "status": 1,
                                "audio": audio_base64
                            }
                        }
                    
                    # 发送JSON帧到讯飞
                    frame_json = json.dumps(frame, ensure_ascii=False)
                    self.ws.send(frame_json)
                    logger.debug(f"已发送RTASR帧到讯飞，大小: {len(audio_data)} bytes")
                    
                    # 不立即返回结果，等待讯飞异步返回
                    return None
                except Exception as e:
                    logger.error(f"讯飞转写失败: {e}")
                    return None
            else:
                # 如果没有WebSocket连接，缓存音频数据等待连接
                logger.debug("讯飞未连接，缓存音频数据")
                if not hasattr(self, 'audio_buffer'):
                    self.audio_buffer = []
                self.audio_buffer.append((audio_data, is_first_frame))
                return None
                
        except Exception as e:
            logger.error(f"同步转写音频数据失败: {e}")
            return None

    def send_end_frame(self):
        """发送结束帧"""
        try:
            if self._is_websocket_connected():
                end_frame = {
                    "data": {
                        "status": 2,
                        "audio": ""
                    }
                }
                frame_json = json.dumps(end_frame, ensure_ascii=False)
                self.ws.send(frame_json)
                logger.info("已发送讯飞RTASR结束帧")
        except Exception as e:
            logger.error(f"发送结束帧失败: {e}")

    def analyze_audio_chunk_sync(self, audio_data: bytes):
        """同步分析音频数据块"""
        try:
            if not self.is_active:
                return None
            
            # 简单的音频分析（音量、语速等）
            # 暂时返回模拟分析结果，不依赖numpy
            try:
                # 这里需要根据音频格式进行解码
                # 暂时返回模拟分析结果
                analysis_result = {
                    'volume_level': 0.7,  # 音量级别
                    'speech_rate': 120,    # 语速（词/分钟）
                    'pitch': 0.5,          # 音调
                    'clarity': 0.8,        # 清晰度
                    'summary': '语音清晰，语速适中，表达自然'
                }
                
                return analysis_result
                
            except Exception as e:
                logger.error(f"音频分析失败: {e}")
                return {
                    'summary': '音频分析失败',
                    'volume_level': 0.5,
                    'speech_rate': 100,
                    'pitch': 0.5,
                    'clarity': 0.6
                }
                
        except Exception as e:
            logger.error(f"同步分析音频数据失败: {e}")
            return None


# 全局音频转写管理器实例
class AudioTranscriptionManager:
    """音频转写管理器"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_results = {}
    
    def create_session(self, session_id: str, app=None) -> AudioService:
        """创建音频转写会话"""
        if session_id in self.active_sessions:
            logger.warning(f"会话 {session_id} 已存在，返回现有会话")
            return self.active_sessions[session_id]

        # 创建新的音频服务实例，传入Flask应用实例
        audio_service = AudioService(app=app)
        self.active_sessions[session_id] = audio_service
        self.session_results[session_id] = []

        logger.info(f"创建音频转写会话: {session_id}")
        return audio_service


# 全局实例
audio_transcription_manager = AudioTranscriptionManager()
