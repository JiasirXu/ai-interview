#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟人交互控制（调用对话WebAPI）
"""

import requests
import json
import time
import websockets
import asyncio
import threading
from typing import Dict, Any, Optional, List
from loguru import logger
from flask import current_app
from concurrent.futures import ThreadPoolExecutor
import base64
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime

class AvatarService:
    """虚拟人服务"""
    
    def __init__(self, config=None):
        self.config = config
        self.avatar_config = None
        self.avatar_api_url = None
        self.service_id = None
        self.avatar_appid = None
        self.avatar_apikey = None
        self.avatar_apisecret = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.active_sessions = {}
        self.conversation_cache = {}
        self._initialized = False
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            if self.config is None:
                from flask import current_app
                self.config = current_app.config.get('XUNFEI_CONFIG', {})

            self.avatar_config = self.config.get('AVATAR', {})
            self.avatar_api_url = self.avatar_config.get('SERVICE_URL')
            self.service_id = self.avatar_config.get('SERVICE_ID')
            # --- 虚拟人使用专用认证信息 (APPID: e98176f0) ---
            self.avatar_appid = self.avatar_config.get('APPID')
            self.avatar_apikey = self.avatar_config.get('APIKey')
            self.avatar_apisecret = self.avatar_config.get('APISecret')

            # 添加调试信息
            logger.info(f"虚拟人服务初始化:")
            logger.info(f"  SERVICE_URL: {self.avatar_api_url}")
            logger.info(f"  SERVICE_ID: {self.service_id}")
            logger.info(f"  APPID: {self.avatar_appid}")

            self._initialized = True

    def _generate_auth_url(self) -> str:
        """生成WebSocket认证URL - 参考讯飞TTS WebSocket认证方式"""
        self._ensure_initialized()

        # 基础WebSocket URL
        base_url = "wss://avatar.cn-huadong-1.xf-yun.com/v1/interact"

        # 生成RFC1123格式的时间戳
        from wsgiref.handlers import format_date_time
        from time import mktime
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 生成签名字符串 - 参考讯飞开放平台WebSocket认证
        signature_origin = f"host: avatar.cn-huadong-1.xf-yun.com\ndate: {date}\nGET /v1/interact HTTP/1.1"

        # 使用HMAC-SHA256生成签名
        signature_sha = hmac.new(
            self.avatar_apisecret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

        # 构建authorization字符串
        authorization_origin = f'api_key="{self.avatar_apikey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        # 构建完整URL - 参考讯飞开放平台标准格式
        params = {
            'authorization': authorization,
            'date': date,
            'host': 'avatar.cn-huadong-1.xf-yun.com'
        }

        auth_url = f"{base_url}?{urlencode(params)}"

        # 添加详细的调试信息
        logger.info(f"虚拟人WebSocket认证信息:")
        logger.info(f"  APPID: {self.avatar_appid}")
        logger.info(f"  APIKey: {self.avatar_apikey[:8]}...")
        logger.info(f"  Date: {date}")
        logger.info(f"  Signature: {signature_sha_base64[:20]}...")
        logger.debug(f"  完整URL: {auth_url}")

        return auth_url

    def _generate_http_auth_url(self, endpoint: str) -> str:
        """生成HTTP API认证URL - 基于讯飞官方文档"""
        self._ensure_initialized()

        # 基础URL
        base_url = f"https://vms.cn-huadong-1.xf-yun.com/v1/private/{endpoint}"

        # 生成时间戳
        from wsgiref.handlers import format_date_time
        from time import mktime
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 生成签名字符串
        signature_origin = f"host: vms.cn-huadong-1.xf-yun.com\ndate: {date}\nPOST /v1/private/{endpoint} HTTP/1.1"

        # 使用HMAC-SHA256生成签名
        signature_sha = hmac.new(
            self.avatar_apisecret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

        # 构建authorization字符串
        authorization_origin = f'api_key="{self.avatar_apikey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        # 构建完整URL
        from urllib.parse import urlencode
        params = {
            'host': 'vms.cn-huadong-1.xf-yun.com',
            'date': date,
            'authorization': authorization
        }

        auth_url = f"{base_url}?{urlencode(params)}"

        logger.debug(f"HTTP API认证URL生成: {endpoint}")
        logger.debug(f"  Date: {date}")
        logger.debug(f"  Signature: {signature_sha_base64[:20]}...")

        return auth_url

    def _stop_avatar_session(self, stop_url: str, session: str):
        """停止虚拟人会话"""
        try:
            stop_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "uid": "user_001",
                    "session": session
                }
            }

            response = requests.post(stop_url, json=stop_request, timeout=10)
            if response.status_code == 200:
                logger.info("虚拟人会话已停止")
            else:
                logger.warning(f"停止会话失败: HTTP {response.status_code}")

        except Exception as e:
            logger.warning(f"停止会话异常: {e}")

    async def test_websocket_connection(self) -> Dict[str, Any]:
        """测试WebSocket连接"""
        try:
            ws_url = self._generate_auth_url()
            logger.info(f"测试WebSocket连接: {ws_url}")

            # 尝试连接
            async with websockets.connect(ws_url) as websocket:
                logger.info("WebSocket连接成功!")

                # 发送一个简单的测试消息
                test_message = {
                    "header": {
                        "app_id": self.avatar_appid,
                        "request_id": "test_connection",
                        "ctrl": "start",
                        "scene_id": self.service_id
                    },
                    "parameter": {
                        "avatar": {
                            "stream": {
                                "protocol": "xrtc",
                                "fps": 25,
                                "bitrate": 2000
                            },
                            "avatar_id": "198329296530575360",
                            "width": 1080,
                            "height": 1920
                        }
                    },
                    "payload": {}
                }

                await websocket.send(json.dumps(test_message))
                response = await websocket.recv()
                response_data = json.loads(response)

                logger.info(f"收到响应: {response_data}")

                return {
                    'success': True,
                    'message': 'WebSocket连接测试成功',
                    'response': response_data
                }

        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"WebSocket连接状态码错误: {e.status_code}")
            return {
                'success': False,
                'error': f"连接被拒绝: HTTP {e.status_code}",
                'status_code': e.status_code
            }
        except Exception as e:
            logger.error(f"WebSocket连接测试失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def test_http_api(self) -> Dict[str, Any]:
        """测试HTTP API连接"""
        try:
            self._ensure_initialized()

            # 使用HTTP API测试连接
            test_url = f"https://virtual-man.xfyun.cn/console/api/{self.avatar_appid}/{self.service_id}"

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.avatar_apikey}'
            }

            # 发送简单的测试请求
            response = requests.get(test_url, headers=headers, timeout=10)

            logger.info(f"HTTP API测试响应: {response.status_code}")
            logger.info(f"响应内容: {response.text[:200]}...")

            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text[:500],
                'message': f'HTTP API测试完成，状态码: {response.status_code}'
            }

        except Exception as e:
            logger.error(f"HTTP API测试失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_avatar_http_response(self, text: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """使用HTTP API创建虚拟人响应（基于讯飞官方文档）"""
        try:
            self._ensure_initialized()

            logger.info(f"使用讯飞虚拟人HTTP API生成响应: {text[:50]}...")

            # 1. 生成认证URL（用于HTTP请求）
            start_url = self._generate_http_auth_url("vms2d_start")
            ctrl_url = self._generate_http_auth_url("vms2d_ctrl")
            stop_url = self._generate_http_auth_url("vms2d_stop")

            # 2. 启动虚拟人会话
            start_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "uid": "user_001"
                },
                "parameter": {
                    "vmr": {
                        "stream": {
                            "protocol": "rtmp"  # 使用RTMP协议
                        },
                        "avatar_id": avatar_config.get('avatar_id', '110332017'),  # 沐沐
                        "width": 1280,
                        "height": 720
                    }
                }
            }

            logger.info("步骤1: 启动虚拟人会话...")
            start_response = requests.post(start_url, json=start_request, timeout=30)

            if start_response.status_code != 200:
                raise Exception(f"启动会话失败: HTTP {start_response.status_code}")

            start_result = start_response.json()
            if start_result.get('header', {}).get('code') != 0:
                error_msg = start_result.get('header', {}).get('message', '启动失败')
                raise Exception(f"启动会话错误: {error_msg}")

            # 获取会话信息
            session = start_result.get('header', {}).get('session')
            stream_url = start_result.get('header', {}).get('stream_url')

            if not session:
                raise Exception("未获取到会话session")

            logger.info(f"会话启动成功，session: {session[:20]}...")
            logger.info(f"流媒体地址: {stream_url}")

            # 3. 发送文本驱动请求
            import base64
            text_base64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')

            ctrl_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "session": session,
                    "uid": "user_001"
                },
                "parameter": {
                    "tts": {
                        "vcn": avatar_config.get('vcn', 'x4_yuexiaoni_assist'),
                        "speed": int(avatar_config.get('voice_speed', 1.0) * 50),
                        "pitch": 50,
                        "volume": int(avatar_config.get('voice_volume', 0.8) * 50)
                    }
                },
                "payload": {
                    "text": {
                        "encoding": "utf8",
                        "status": 3,
                        "seq": 1,
                        "text": text_base64
                    },
                    "ctrl_w": {
                        "encoding": "utf8",
                        "format": "json",
                        "status": 3,
                        "seq": 1,
                        "text": ""  # 暂不使用动作控制
                    }
                }
            }

            logger.info("步骤2: 发送文本驱动请求...")
            ctrl_response = requests.post(ctrl_url, json=ctrl_request, timeout=30)

            if ctrl_response.status_code != 200:
                # 尝试停止会话
                self._stop_avatar_session(stop_url, session)
                raise Exception(f"文本驱动失败: HTTP {ctrl_response.status_code}")

            ctrl_result = ctrl_response.json()
            if ctrl_result.get('header', {}).get('code') != 0:
                error_msg = ctrl_result.get('header', {}).get('message', '文本驱动失败')
                # 尝试停止会话
                self._stop_avatar_session(stop_url, session)
                raise Exception(f"文本驱动错误: {error_msg}")

            logger.info("文本驱动成功")

            # 4. 返回成功结果（包含流媒体URL）
            return {
                'success': True,
                'video_url': stream_url,  # RTMP流地址
                'audio_url': None,  # 音频包含在视频流中
                'text': text,
                'duration': len(text) * 0.15,  # 估算时长
                'timestamp': time.time(),
                'method': 'http_api',
                'session': session,
                'message': '使用讯飞虚拟人HTTP API生成响应成功'
            }

        except Exception as e:
            logger.error(f"虚拟人HTTP API调用异常: {e}")
            raise e

    def _create_mock_avatar_response(self, text: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """创建模拟虚拟人响应（当WebSocket连接失败时使用）"""
        try:
            import time
            import uuid

            # 模拟处理时间
            time.sleep(1)

            # 生成模拟的视频URL（实际应用中可以使用静态视频或图片）
            mock_video_url = f"https://mock-avatar-service.com/video/{uuid.uuid4()}.mp4"
            mock_audio_url = f"https://mock-avatar-service.com/audio/{uuid.uuid4()}.wav"

            logger.info(f"生成模拟虚拟人响应: {text[:50]}...")

            return {
                'success': True,
                'video_url': mock_video_url,
                'audio_url': mock_audio_url,
                'text': text,
                'duration': len(text) * 0.1,  # 根据文本长度估算时长
                'timestamp': time.time(),
                'is_mock': True,  # 标识这是模拟响应
                'message': '虚拟人服务暂时不可用，使用模拟响应'
            }

        except Exception as e:
            logger.error(f"创建模拟虚拟人响应失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'is_mock': True
            }

    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证headers"""
        self._ensure_initialized()
        # 根据虚拟人API文档，认证信息在Header中
        return {
            'Content-Type': 'application/json',
            'appId': self.avatar_appid,
            'apiKey': self.avatar_apikey,
            'apiSecret': self.avatar_apisecret,
            # 'X-Service-Id' 可能是自定义头，或者根据具体API文档要求添加
        }
    
    def generate_avatar_speech(self, text: str, voice_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成虚拟人语音
        
        Args:
            text: 要合成的文本
            voice_config: 语音配置
            
        Returns:
            语音生成结果
        """
        self._ensure_initialized()
        try:
            default_config = {
                "voice": "xiaoyan",  # 默认音色
                "speed": 50,        # 语速
                "volume": 50,       # 音量
                "pitch": 50,        # 音调
                "emotion": "neutral" # 情感
            }
            
            if voice_config:
                default_config.update(voice_config)
            
            payload = {
                "header": {
                    "app_id": self.avatar_appid,
                    "uid": "test_user_123" # 示例用户ID，实际应动态生成
                },
                "parameter": {
                    "chat": {
                        "domain": "general",
                        "temperature": 0.5,
                        "max_tokens": 1024
                    }
                },
                "payload": {
                    "message": {
                        "text": [
                            {"role": "user", "content": text}
                        ]
                    }
                }
            }
            
            # 虚拟人交互API通常是WebSocket，但如果没有SDK且文档提供了HTTP接口，则使用requests
            # 此处代码基于一个假设的HTTP接口结构，实际需根据文档调整
            response = requests.post(
                self.avatar_api_url,
                headers=self._get_auth_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析返回结果，提取音频URL等信息
                # 假设返回结构如下
                audio_content = result.get('payload', {}).get('message', {}).get('text', [{}])[0].get('content')
                # 实际可能返回的是音频文件的URL或base64数据
                return {
                    'success': True,
                    'data': result,
                    'audio_url': audio_content, # 假设是URL
                    'duration': result.get('payload', {}).get('duration', 0),
                    'timestamp': time.time()
                }
            else:
                logger.error(f"语音合成失败: {response.status_code}, {response.text}")
                return {
                    'success': False,
                    'error': f"TTS API错误: {response.status_code}, {response.text}"
                }
                
        except Exception as e:
            logger.error(f"语音合成异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_avatar_config_by_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据面试偏好设置获取数字人配置 - 支持新的结构化配置

        Args:
            preferences: 面试偏好设置（支持新旧两种格式）

        Returns:
            数字人配置
        """
        # 检查是否是新的结构化配置
        if isinstance(preferences, dict) and 'avatar_config' in preferences:
            # 新的结构化配置
            avatar_config = preferences.get('avatar_config', {})
            interaction_config = preferences.get('interaction_config', {})
            expression_config = preferences.get('expression_config', {})
            voice_config = preferences.get('voice_config', {})

            # 根据形象风格映射到具体配置
            avatar_style = avatar_config.get('avatar_style', 0)
            avatar_gender = avatar_config.get('avatar_gender', 'neutral')
            avatar_age_range = avatar_config.get('avatar_age_range', 'middle')

            # 形象风格映射 - 5个虚拟人形象与前端选择绑定
            # 前端显示：风格1(沐沐) -> 风格2(马可) -> 风格3(婉仪) -> 风格4(诗雅) -> 风格5(浩然)
            style_mapping = {
                0: {"avatar_id": "110332017", "vcn": "x4_yuexiaoni_assist", "name": "沐沐", "gender": "female", "background": "office_formal", "description": "温和亲切的女性面试官"},
                1: {"avatar_id": "110017006", "vcn": "x4_mingge", "name": "马可", "gender": "male", "background": "office_casual", "description": "专业稳重的男性面试官"},
                2: {"avatar_id": "cnrfb86h2000000004", "vcn": "x4_yezi", "name": "婉仪", "gender": "female", "background": "office_executive", "description": "优雅知性的女性面试官"},
                3: {"avatar_id": "cnrn9jgi2000000005", "vcn": "x4_yiting", "name": "诗雅", "gender": "female", "background": "office_modern", "description": "年轻活力的女性面试官"},
                4: {"avatar_id": "cnr5dg8n2000000003", "vcn": "x4_mingge", "name": "浩然", "gender": "male", "background": "office_tech", "description": "技术专业的男性面试官"}
            }

            base_config = style_mapping.get(avatar_style, style_mapping[0])

            # 应用语音配置
            base_config.update({
                'voice_speed': float(voice_config.get('voice_speed', 1.0)),
                'voice_pitch': float(voice_config.get('voice_pitch', 1.0)),
                'voice_volume': float(voice_config.get('voice_volume', 0.8)),
                'voice_style': voice_config.get('voice_style', 'professional')
            })

            # 应用表情配置
            enabled_expressions = expression_config.get('enabled_expressions', ['nod'])
            base_config.update({
                'emotion_feedback_enabled': len(enabled_expressions) > 0,
                'available_expressions': enabled_expressions,
                'expression_intensity': expression_config.get('expression_intensity', 0.7),
                'expression_frequency': expression_config.get('expression_frequency', 0.5)
            })

            # 应用互动配置
            interaction_mode = interaction_config.get('interaction_mode', 'frequent')
            base_config.update({
                'interaction_mode': interaction_mode,
                'question_frequency': interaction_config.get('question_frequency', 2.0),
                'follow_up_probability': interaction_config.get('follow_up_probability', 0.3)
            })

        else:
            # 兼容旧的扁平结构 - 使用真实的虚拟人形象ID
            interviewer_expressions = {
                'friendly': {
                    "avatar_id": "110332017",  # 沐沐
                    "vcn": "x4_yuexiaoni_assist",
                    "voice_style": "warm",
                    "expression_base": "friendly",
                    "gesture_style": "natural",
                    "background": "office_casual"
                },
                'serious': {
                    "avatar_id": "110017006",  # 马可
                    "vcn": "x4_mingge",
                    "voice_style": "formal",
                    "expression_base": "serious",
                    "gesture_style": "minimal",
                    "background": "office_formal"
                },
                'pressure': {
                    "avatar_id": "cnrfb86h2000000004",  # 婉仪
                    "vcn": "x4_yezi",
                    "voice_style": "authoritative",
                    "expression_base": "stern",
                    "gesture_style": "formal",
                    "background": "office_executive"
                }
            }

            interviewer_expression = preferences.get('interviewer_expression', 'friendly')
            base_config = interviewer_expressions.get(interviewer_expression, interviewer_expressions['friendly'])

            # 根据语音速度调整
            voice_speed = preferences.get('voice_speed', 1.0)
            # 确保voice_speed是float类型，避免Decimal序列化问题
            base_config['voice_speed'] = float(voice_speed)

            # 根据微表情反馈设置调整表情丰富度
            enable_emotion_feedback = preferences.get('enable_emotion_feedback', True)
            if enable_emotion_feedback:
                feedback_types = preferences.get('feedback_types', ['nod'])
                base_config['emotion_feedback_enabled'] = True
                base_config['available_expressions'] = feedback_types
            else:
                base_config['emotion_feedback_enabled'] = False
                base_config['available_expressions'] = ['neutral']

        return base_config

    def get_available_avatars(self) -> List[Dict[str, Any]]:
        """
        获取可用的虚拟人形象列表

        Returns:
            虚拟人形象列表
        """
        # 返回5个虚拟人形象的信息
        avatars = [
            {"id": 0, "avatar_id": "110332017", "name": "沐沐", "gender": "female", "description": "温和亲切的女性面试官", "vcn": "x4_yuexiaoni_assist"},
            {"id": 1, "avatar_id": "110017006", "name": "马可", "gender": "male", "description": "专业稳重的男性面试官", "vcn": "x4_mingge"},
            {"id": 2, "avatar_id": "cnrfb86h2000000004", "name": "婉仪", "gender": "female", "description": "优雅知性的女性面试官", "vcn": "x4_yezi"},
            {"id": 3, "avatar_id": "cnrn9jgi2000000005", "name": "诗雅", "gender": "female", "description": "年轻活力的女性面试官", "vcn": "x4_yiting"},
            {"id": 4, "avatar_id": "cnr5dg8n2000000003", "name": "浩然", "gender": "male", "description": "技术专业的男性面试官", "vcn": "x4_mingge"}
        ]
        return avatars

    def generate_avatar_speech(self, text: str, voice_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成虚拟面试官语音

        Args:
            text: 要合成的文本
            voice_config: 语音配置

        Returns:
            语音生成结果
        """
        try:
            # 构建TTS请求参数
            tts_params = {
                'text': text,
                'voice_speed': voice_config.get('voice_speed', 1.0),
                'voice_pitch': voice_config.get('voice_pitch', 1.0),
                'voice_volume': voice_config.get('voice_volume', 0.8),
                'voice_style': voice_config.get('voice_style', 'professional'),
                'output_format': 'mp3'
            }

            # 调用虚拟人API生成语音
            response = requests.post(
                f"{self.base_url}/tts/generate",
                json=tts_params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    return {
                        'success': True,
                        'audio_url': result.get('audio_url'),
                        'duration': result.get('duration', 3.0),
                        'audio_data': result.get('audio_data')  # base64编码的音频数据
                    }
                else:
                    logger.error(f"TTS生成失败: {result.get('message')}")
                    return {
                        'success': False,
                        'error': result.get('message', 'TTS生成失败')
                    }
            else:
                logger.error(f"TTS API调用失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API调用失败: {response.status_code}'
                }

        except requests.exceptions.Timeout:
            logger.error("TTS生成超时")
            return {
                'success': False,
                'error': 'TTS生成超时'
            }
        except Exception as e:
            logger.error(f"TTS生成异常: {e}")
            return {
                'success': False,
                'error': f'TTS生成异常: {str(e)}'
            }

    def generate_expression_feedback(self, feedback_type: str, intensity: float = 0.7) -> Dict[str, Any]:
        """
        生成微表情反馈

        Args:
            feedback_type: 表情类型 (nod, frown, timer, smile, thinking, surprised)
            intensity: 表情强度 (0-1)

        Returns:
            表情生成结果
        """
        try:
            # 表情映射
            expression_mapping = {
                'nod': {'action': 'nod', 'duration': 1.5},
                'frown': {'action': 'frown', 'duration': 2.0},
                'timer': {'action': 'look_at_watch', 'duration': 1.0},
                'smile': {'action': 'smile', 'duration': 2.0},
                'thinking': {'action': 'thinking', 'duration': 3.0},
                'surprised': {'action': 'surprised', 'duration': 1.5}
            }

            if feedback_type not in expression_mapping:
                return {
                    'success': False,
                    'error': f'不支持的表情类型: {feedback_type}'
                }

            expression_config = expression_mapping[feedback_type]

            # 构建表情请求参数
            expression_params = {
                'action': expression_config['action'],
                'intensity': max(0.1, min(1.0, intensity)),
                'duration': expression_config['duration'],
                'blend_mode': 'smooth'
            }

            # 调用虚拟人API生成表情
            response = requests.post(
                f"{self.base_url}/expression/trigger",
                json=expression_params,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    return {
                        'success': True,
                        'expression_id': result.get('expression_id'),
                        'duration': expression_config['duration'],
                        'video_url': result.get('video_url')  # 表情视频片段URL
                    }
                else:
                    logger.error(f"表情生成失败: {result.get('message')}")
                    return {
                        'success': False,
                        'error': result.get('message', '表情生成失败')
                    }
            else:
                logger.error(f"表情API调用失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API调用失败: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"表情生成异常: {e}")
            return {
                'success': False,
                'error': f'表情生成异常: {str(e)}'
            }

    def create_avatar_response(self,
                             text: str,
                             expression: str = "neutral",
                             gesture: str = "idle",
                             preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建虚拟人响应

        Args:
            text: 响应文本
            expression: 面部表情
            gesture: 手势动作
            preferences: 面试偏好设置

        Returns:
            虚拟人响应结果
        """
        try:
            # 确保服务已初始化
            self._ensure_initialized()

            # 检查配置是否有效
            if not self.avatar_api_url:
                logger.error("虚拟人服务URL未配置")
                return {
                    'success': False,
                    'error': '虚拟人服务未正确配置'
                }

            # 获取个性化配置
            if preferences:
                avatar_config = self._get_avatar_config_by_preferences(preferences)
            else:
                avatar_config = {
                    "avatar_id": "110332017",  # 默认使用沐沐
                    "vcn": "x4_yuexiaoni_assist",
                    "voice_style": "formal",
                    "expression_base": "neutral",
                    "gesture_style": "minimal",
                    "background": "office_formal",
                    "voice_speed": 1.0,
                    "emotion_feedback_enabled": True,
                    "available_expressions": ["neutral"]
                }

            payload = {
                "header": {
                    "app_id": self.avatar_appid
                },
                "parameter": {
                    "avatar": {
                        "avatar_id": avatar_config.get("avatar_id"),
                        "voice_style": avatar_config.get("voice_style"),
                        "voice_speed": avatar_config.get("voice_speed", 1.0)
                    }
                },
                "payload": {
                    "text": {
                        "content": text
                    },
                    "avatar_config": {
                        "expression": expression or avatar_config.get("expression_base"),
                        "gesture": gesture or avatar_config.get("gesture_style"),
                        "animation": "talking",
                        "background": avatar_config.get("background"),
                        "emotion_feedback_enabled": avatar_config.get("emotion_feedback_enabled")
                    },
                    "sync_audio": True,
                    "return_video": True
                }
            }
            
            # 尝试WebSocket连接，失败时使用HTTP API备选方案
            try:
                return asyncio.run(self._create_avatar_websocket_response(text, expression, gesture, avatar_config))
            except Exception as ws_error:
                logger.warning(f"WebSocket连接失败，尝试HTTP API备选方案: {ws_error}")
                # 尝试使用HTTP API
                try:
                    return self._create_avatar_http_response(text, avatar_config)
                except Exception as http_error:
                    logger.warning(f"HTTP API也失败，使用模拟响应: {http_error}")
                    return self._create_mock_avatar_response(text, avatar_config)
                
        except Exception as e:
            logger.error(f"虚拟人生成异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }



    async def _create_avatar_websocket_response(self, text: str, expression: str, gesture: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """使用WebSocket创建虚拟人响应"""

        # 重新启用虚拟人服务，使用完整的实现
        logger.info(f"启动虚拟人服务，生成内容: {text[:50]}...")

        try:
            return await self._create_avatar_websocket_response_impl(text, expression, gesture, avatar_config)
        except Exception as e:
            logger.error(f"虚拟人WebSocket调用失败: {e}")

            # 检查具体的错误类型并提供相应的处理
            error_msg = str(e)

            if "avatar authentication failed" in error_msg or "11200" in error_msg:
                logger.warning(f"虚拟人认证失败，可能是avatar_id或权限问题: {e}")
                # 虚拟人认证失败，但WebSocket连接成功，说明基础认证是对的
                return {
                    'success': True,
                    'video_url': None,
                    'audio_url': None,
                    'text': text,
                    'expression': expression,
                    'gesture': gesture,
                    'duration': len(text) * 0.1,
                    'fallback': True,
                    'error_details': "虚拟人认证失败，可能需要额外的权限或正确的avatar_id",
                    'message': '虚拟人服务认证失败，使用文本模式'
                }
            elif "avatar_id is invalid" in error_msg:
                logger.warning(f"虚拟人avatar_id无效: {e}")
                return {
                    'success': True,
                    'video_url': None,
                    'audio_url': None,
                    'text': text,
                    'expression': expression,
                    'gesture': gesture,
                    'duration': len(text) * 0.1,
                    'fallback': True,
                    'error_details': "avatar_id无效，需要使用正确的虚拟人形象ID",
                    'message': '虚拟人形象ID无效，使用文本模式'
                }
            else:
                # 其他错误的通用处理
                logger.warning(f"虚拟人服务调用失败，使用降级模式: {e}")
                return {
                    'success': True,
                    'video_url': None,
                    'audio_url': None,
                    'text': text,
                    'expression': expression,
                    'gesture': gesture,
                    'duration': len(text) * 0.1,
                    'fallback': True,
                    'error_details': str(e),
                    'message': f'虚拟人服务暂时不可用({type(e).__name__})，使用文本模式'
                }

    async def _create_avatar_websocket_response_impl(self, text: str, expression: str, gesture: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """WebSocket创建虚拟人响应的实际实现"""

        # 设置重试参数
        max_retries = 3
        retry_delay = 2  # 秒

        for retry_count in range(max_retries):
            try:
                logger.info(f"虚拟人WebSocket连接尝试 {retry_count+1}/{max_retries}")
                if retry_count > 0:
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)

                # 生成认证URL
                ws_url = self._generate_auth_url()
                logger.info(f"连接虚拟人WebSocket: {ws_url}")

                # 生成唯一请求ID
                import uuid
                request_id = str(uuid.uuid4())

                # 调试：打印当前使用的avatar配置
                logger.info(f"当前avatar配置: avatar_id={avatar_config.get('avatar_id')}, vcn={avatar_config.get('vcn')}, name={avatar_config.get('name', 'unknown')}")

                # 1. 首先发送启动协议
                start_request = {
                    "header": {
                        "app_id": self.avatar_appid,
                        "request_id": request_id,
                        "ctrl": "start",
                        "scene_id": self.service_id
                    },
                    "parameter": {
                        "avatar": {
                            "stream": {
                                "protocol": "xrtc",  # 支持透明背景
                                "fps": 25,
                                "bitrate": 2000,
                                "alpha": 0  # 0=不透明，1=透明
                            },
                            "avatar_id": "110332017",  # 直接使用沐沐的ID进行测试
                            "mask_region": "[0,0,1080,1920]",  # 形象裁剪参数
                            "width": 1080,  # 分辨率宽度（4的倍数）
                            "height": 1920,  # 分辨率高度（4的倍数）
                            "scale": 1.0,  # 虚拟人缩放大小 [0.1, 1.0]
                            "move_h": 0,  # 水平平移距离 [-4096, +4096]
                            "move_v": 0,  # 垂直移动距离 [-4096, +4096]
                            "audio_format": 1  # 音频驱动采样率：1=16k, 2=24k
                        },
                        "tts": {
                            "vcn": "x4_yuexiaoni_assist",  # 直接使用沐沐的声音进行测试
                            "speed": int(avatar_config.get("voice_speed", 1.0) * 50),  # 合成语速 [0,100]
                            "pitch": 50,  # 合成语调 [0,100]
                            "volume": 50  # 合成音量 [0,100]
                        },
                        "subtitle": {
                            "subtitle": 0,  # 0关闭，1开启云端字幕
                            "font_color": "#FFFFFF",
                            "font_size": 5,
                            "font_name": "mainTitle"
                        }
                    },
                    "payload": {}
                }

                # 调试：打印启动请求的关键信息
                logger.info(f"启动请求关键参数: avatar_id={start_request['parameter']['avatar']['avatar_id']}, vcn={start_request['parameter']['tts']['vcn']}")
                logger.debug(f"完整启动请求: {start_request}")

                # 连接WebSocket
                logger.info(f"尝试连接虚拟人WebSocket...")
                logger.debug(f"认证URL: {ws_url}")

                try:
                    # 设置WebSocket连接参数 - 修复websockets库兼容性问题
                    connect_timeout = 15  # 连接超时时间
                    ping_interval = 20    # 心跳间隔
                    ping_timeout = 10     # 心跳超时

                    logger.info(f"WebSocket连接参数: timeout={connect_timeout}s, ping_interval={ping_interval}s")

                    # 修复websockets库兼容性问题 - 移除timeout参数
                    async with websockets.connect(
                        ws_url,
                        ping_interval=ping_interval,
                        ping_timeout=ping_timeout,
                        max_size=2**20,  # 1MB
                        max_queue=32
                    ) as websocket:
                        # 发送启动请求
                        await websocket.send(json.dumps(start_request))
                        logger.info("已发送虚拟人启动请求")

                        # 接收启动响应
                        stream_url = None
                        start_response = await websocket.recv()
                        start_data = json.loads(start_response)

                        if start_data.get("header", {}).get("code") == 0:
                            payload = start_data.get("payload", {})
                            avatar_info = payload.get("avatar", {})
                            stream_url = avatar_info.get("stream_url")
                            logger.info(f"虚拟人启动成功，流地址: {stream_url}")
                        else:
                            error_msg = start_data.get("header", {}).get("message", "启动失败")
                            logger.error(f"虚拟人启动失败: {error_msg}")
                            return {
                                'success': False,
                                'error': f"虚拟人启动失败: {error_msg}"
                            }

                        # 2. 发送文本驱动协议
                        text_request = {
                            "header": {
                                "app_id": self.avatar_appid,
                                "ctrl": "text_driver",
                                "request_id": str(uuid.uuid4())
                            },
                            "parameter": {
                                "avatar_dispatch": {
                                    "interactive_mode": 1  # 0=追加，1=打断
                                },
                                "tts": {
                                    "vcn": avatar_config.get("voice_style", ""),
                                    "speed": int(avatar_config.get("voice_speed", 1.0) * 50),
                                    "pitch": 50,
                                    "volume": 50
                                },
                                "air": {
                                    "air": 1,  # 开启自动动作（需要支持动作的形象）
                                    "add_nonsemantic": 1  # 开启无指向性动作
                                }
                            },
                            "payload": {
                                "text": {
                                    "content": text  # 驱动文本，不超过2000字符
                                }
                            }
                        }

                        # 发送文本驱动请求
                        await websocket.send(json.dumps(text_request))
                        logger.info(f"已发送文本驱动请求: {text}")

                        # 接收驱动响应
                        driver_response = await websocket.recv()
                        driver_data = json.loads(driver_response)

                        if driver_data.get("header", {}).get("code") == 0:
                            logger.info("文本驱动成功")
                            # 检查流地址类型并处理
                            if stream_url and stream_url.startswith('xrtcs://'):
                                # XRTC流地址，需要特殊处理
                                logger.info(f"获得XRTC流地址: {stream_url}")
                                return {
                                    'success': True,
                                    'video_url': stream_url,  # 返回XRTC流地址
                                    'audio_url': None,
                                    'text': text,
                                    'duration': 5,
                                    'timestamp': time.time(),
                                    'stream_type': 'xrtc',  # 标识流类型
                                    'stream_extend': start_data.get("payload", {}).get("avatar", {}).get("stream_extend"),
                                    'message': '虚拟人XRTC流已启动，需要WebRTC播放器'
                                }
                            else:
                                # 普通HTTP视频URL
                                return {
                                    'success': True,
                                    'video_url': stream_url,
                                    'audio_url': None,
                                    'text': text,
                                    'duration': 5,
                                    'timestamp': time.time(),
                                    'stream_type': 'http',
                                    'stream_extend': start_data.get("payload", {}).get("avatar", {}).get("stream_extend")
                                }
                        else:
                            error_msg = driver_data.get("header", {}).get("message", "驱动失败")
                            logger.error(f"文本驱动失败: {error_msg}")
                            return {
                                'success': False,
                                'error': f"文本驱动失败: {error_msg}"
                            }

                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(f"WebSocket连接被关闭 (尝试 {retry_count+1}/{max_retries}): {e}")
                    if retry_count == max_retries - 1:
                        return {
                            'success': False,
                            'error': f"WebSocket连接被关闭: {e}"
                        }
                    continue

                except websockets.exceptions.InvalidStatusCode as e:
                    logger.error(f"WebSocket连接状态码错误: HTTP {e.status_code} - {e}")
                    if e.status_code == 403:
                        logger.error("403错误通常是IP白名单或认证问题")
                    elif e.status_code == 401:
                        logger.error("401错误通常是认证信息错误")
                    elif e.status_code == 404:
                        logger.error("404错误通常是URL路径错误")
                    # 对于认证错误，不需要重试
                    if e.status_code in [401, 403]:
                        return {
                            'success': False,
                            'error': f"WebSocket连接被拒绝: HTTP {e.status_code}"
                        }
                    # 对于其他错误，可以重试
                    if retry_count == max_retries - 1:
                        return {
                            'success': False,
                            'error': f"WebSocket连接被拒绝: HTTP {e.status_code}"
                        }
                    continue

                except websockets.exceptions.InvalidURI as e:
                    logger.error(f"WebSocket URL格式错误: {e}")
                    return {
                        'success': False,
                        'error': f"WebSocket URL格式错误: {e}"
                    }

                except asyncio.TimeoutError as e:
                    logger.warning(f"WebSocket连接超时 (尝试 {retry_count+1}/{max_retries}): {e}")
                    if retry_count == max_retries - 1:  # 最后一次尝试
                        return {
                            'success': False,
                            'error': "WebSocket连接超时，请检查网络连接或服务状态"
                        }
                    continue  # 继续下一次重试

            except Exception as e:
                logger.warning(f"WebSocket连接异常 (尝试 {retry_count+1}/{max_retries}): {type(e).__name__}: {e}")
                if retry_count == max_retries - 1:  # 最后一次尝试
                    import traceback
                    logger.error(f"详细错误信息: {traceback.format_exc()}")
                    return {
                        'success': False,
                        'error': f"WebSocket连接失败: {type(e).__name__}: {e}"
                    }
                continue  # 继续下一次重试

        # 如果所有重试都失败了
        return {
            'success': False,
            'error': f"WebSocket连接失败，已重试 {max_retries} 次"
        }

    async def text_interact_with_avatar(self, text: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """文本交互协议 - 走语义理解"""
        try:
            ws_url = self._generate_auth_url()
            import uuid
            request_id = str(uuid.uuid4())

            # 文本交互请求
            interact_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "ctrl": "text_interact",
                    "request_id": request_id
                },
                "parameter": {
                    "tts": {
                        "vcn": avatar_config.get("voice_style", ""),
                        "speed": int(avatar_config.get("voice_speed", 1.0) * 50),
                        "pitch": 50,
                        "volume": 50
                    },
                    "air": {
                        "air": 1,  # 开启自动动作
                        "add_nonsemantic": 1  # 开启无指向性动作
                    }
                },
                "payload": {
                    "text": {
                        "content": text  # 走语义理解的文本
                    }
                }
            }

            async with websockets.connect(ws_url) as websocket:
                await websocket.send(json.dumps(interact_request))
                logger.info(f"已发送文本交互请求: {text}")

                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)

                if data.get("header", {}).get("code") == 0:
                    payload = data.get("payload", {})
                    nlp_data = payload.get("nlp", {})
                    avatar_data = payload.get("avatar", {})

                    return {
                        'success': True,
                        'nlp_answer': nlp_data.get("answer", {}).get("text", ""),
                        'tts_text': nlp_data.get("tts_answer", {}).get("text", ""),
                        'hit_question': nlp_data.get("answer", {}).get("hit_question", ""),
                        'service': nlp_data.get("service", ""),
                        'avatar_status': avatar_data.get("vmr_status"),
                        'timestamp': time.time()
                    }
                else:
                    error_msg = data.get("header", {}).get("message", "交互失败")
                    return {
                        'success': False,
                        'error': f"文本交互失败: {error_msg}"
                    }

        except Exception as e:
            logger.error(f"文本交互异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_avatar_command(self, command_type: str, command_value: str, time_offset: int = 0) -> Dict[str, Any]:
        """发送单独指令协议（如动作指令）"""
        try:
            ws_url = self._generate_auth_url()
            import uuid
            request_id = str(uuid.uuid4())

            # 单独指令请求
            cmd_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "ctrl": "cmd",
                    "request_id": request_id
                },
                "payload": {
                    "cmd_text": {
                        "avatar": [
                            {
                                "type": command_type,  # "action" 或 "emotion"
                                "value": command_value,  # 动作名称或情感类型
                                "tb": time_offset  # 时间偏移，0表示立即触发
                            }
                        ]
                    }
                }
            }

            async with websockets.connect(ws_url) as websocket:
                await websocket.send(json.dumps(cmd_request))
                logger.info(f"已发送指令: {command_type}={command_value}")

                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)

                if data.get("header", {}).get("code") == 0:
                    return {
                        'success': True,
                        'message': '指令发送成功',
                        'timestamp': time.time()
                    }
                else:
                    error_msg = data.get("header", {}).get("message", "指令失败")
                    return {
                        'success': False,
                        'error': f"指令发送失败: {error_msg}"
                    }

        except Exception as e:
            logger.error(f"发送指令异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def audio_drive_avatar(self, audio_data: bytes, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """音频驱动协议 - 直接播报音频内容"""
        try:
            ws_url = self._generate_auth_url()
            import uuid
            request_id = str(uuid.uuid4())

            # 将音频数据转换为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # 音频驱动请求
            audio_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "ctrl": "audio_driver",
                    "request_id": request_id
                },
                "parameter": {
                    "avatar_dispatch": {
                        "audio_mode": 0  # 0=非实时音频（音频文件），1=实时音频
                    }
                },
                "payload": {
                    "audio": {
                        "encoding": "raw",  # 音频编码
                        "sample_rate": 16000,  # 采样率
                        "channels": 1,  # 声道数
                        "bit_depth": 16,  # 位深
                        "status": 0,  # 0=开始，1=中间，2=结束
                        "seq": 1,  # 数据序号
                        "audio": audio_base64,  # 音频数据base64
                        "frame_size": 0  # 帧大小
                    }
                }
            }

            async with websockets.connect(ws_url) as websocket:
                await websocket.send(json.dumps(audio_request))
                logger.info("已发送音频驱动请求")

                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)

                if data.get("header", {}).get("code") == 0:
                    avatar_data = data.get("payload", {}).get("avatar", {})
                    return {
                        'success': True,
                        'vmr_status': avatar_data.get("vmr_status"),
                        'frame_num': avatar_data.get("frame_num"),
                        'timestamp': time.time()
                    }
                else:
                    error_msg = data.get("header", {}).get("message", "音频驱动失败")
                    return {
                        'success': False,
                        'error': f"音频驱动失败: {error_msg}"
                    }

        except Exception as e:
            logger.error(f"音频驱动异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def audio_interact_with_avatar(self, audio_data: bytes, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """音频交互协议 - 语音识别+语义理解+虚拟人播报"""
        try:
            ws_url = self._generate_auth_url()
            import uuid
            request_id = str(uuid.uuid4())

            # 将音频数据转换为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # 音频交互请求
            audio_interact_request = {
                "header": {
                    "app_id": self.avatar_appid,
                    "ctrl": "audio_interact",
                    "request_id": request_id
                },
                "parameter": {
                    "asr": {
                        "full_duplex": 0  # 0=按住说话语音识别，1=全双工语音识别
                    }
                },
                "payload": {
                    "audio": {
                        "encoding": "raw",
                        "sample_rate": 16000,
                        "channels": 1,
                        "bit_depth": 16,
                        "status": 0,  # 0=开始，1=中间，2=结束
                        "seq": 1,
                        "audio": audio_base64,
                        "frame_size": 0
                    }
                }
            }

            async with websockets.connect(ws_url) as websocket:
                await websocket.send(json.dumps(audio_interact_request))
                logger.info("已发送音频交互请求")

                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)

                if data.get("header", {}).get("code") == 0:
                    payload = data.get("payload", {})
                    asr_data = payload.get("asr", {})
                    nlp_data = payload.get("nlp", {})
                    avatar_data = payload.get("avatar", {})

                    return {
                        'success': True,
                        'asr_text': asr_data.get("text", ""),  # 语音识别结果
                        'nlp_answer': nlp_data.get("answer", {}).get("text", ""),  # 语义理解结果
                        'tts_text': nlp_data.get("tts_answer", {}).get("text", ""),  # 虚拟人播报文本
                        'hit_question': nlp_data.get("answer", {}).get("hit_question", ""),
                        'service': nlp_data.get("service", ""),
                        'avatar_status': avatar_data.get("vmr_status"),
                        'timestamp': time.time()
                    }
                else:
                    error_msg = data.get("header", {}).get("message", "音频交互失败")
                    return {
                        'success': False,
                        'error': f"音频交互失败: {error_msg}"
                    }

        except Exception as e:
            logger.error(f"音频交互异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_feedback_expression(self,
                                 feedback_type: str,
                                 preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        根据AI反馈创建面试官表情反应

        Args:
            feedback_type: 反馈类型 (nod, frown, timer等)
            preferences: 面试偏好设置

        Returns:
            表情反应结果
        """
        if not preferences or not preferences.get('enable_emotion_feedback', True):
            return {'success': True, 'message': '表情反馈已禁用'}

        feedback_types = preferences.get('feedback_types', ['nod'])
        if feedback_type not in feedback_types:
            return {'success': True, 'message': f'表情类型 {feedback_type} 未启用'}

        try:
            # 获取个性化配置
            avatar_config = self._get_avatar_config_by_preferences(preferences)

            # 根据反馈类型设置表情和动作
            expression_mapping = {
                'nod': {
                    'expression': 'approving',
                    'gesture': 'nod',
                    'duration': 2.0,
                    'text': ''  # 纯表情，无语音
                },
                'frown': {
                    'expression': 'questioning',
                    'gesture': 'slight_frown',
                    'duration': 1.5,
                    'text': ''
                },
                'timer': {
                    'expression': 'concerned',
                    'gesture': 'check_watch',
                    'duration': 2.5,
                    'text': ''
                }
            }

            feedback_config = expression_mapping.get(feedback_type, expression_mapping['nod'])

            # 模拟返回结果（实际需要调用真实的数字人API）
            return {
                'success': True,
                'video_url': f'https://avatar-api.example.com/feedback/{feedback_type}.mp4',
                'feedback_type': feedback_type,
                'duration': feedback_config['duration']
            }

        except Exception as e:
            logger.error(f"创建表情反馈失败: {e}")
            return {'success': False, 'error': f'表情反馈创建失败: {str(e)}'}

    def ask_question(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        虚拟人提问
        
        Args:
            prompt: 问题内容
            context: 上下文信息
            
        Returns:
            提问结果
        """
        try:
            # 根据上下文调整表情和手势
            expression = self._determine_expression(prompt, context)
            gesture = self._determine_gesture(prompt, context)
            
            # 生成虚拟人响应
            avatar_result = self.create_avatar_response(prompt, expression, gesture)
            
            if avatar_result['success']:
                return {
                    'success': True,
                    'question': prompt,
                    'video_url': avatar_result['video_url'],
                    'audio_url': avatar_result['audio_url'],
                    'duration': avatar_result['duration'],
                    'expression': expression,
                    'gesture': gesture,
                    'timestamp': time.time()
                }
            else:
                return avatar_result
                
        except Exception as e:
            logger.error(f"虚拟人提问失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_expression(self, text: str, context: Dict[str, Any] = None) -> str:
        """根据文本内容确定表情"""
        text_lower = text.lower()
        
        # 根据关键词判断表情
        if any(word in text_lower for word in ['欢迎', '很好', '优秀', '赞']):
            return 'happy'
        elif any(word in text_lower for word in ['技术', '编程', '代码', '算法']):
            return 'serious'
        elif any(word in text_lower for word in ['项目', '经验', '工作']):
            return 'interested'
        elif any(word in text_lower for word in ['问题', '困难', '挑战']):
            return 'thoughtful'
        else:
            return 'neutral'
    
    def _determine_gesture(self, text: str, context: Dict[str, Any] = None) -> str:
        """根据文本内容确定手势"""
        text_lower = text.lower()
        
        # 根据关键词判断手势
        if any(word in text_lower for word in ['介绍', '说说', '讲讲']):
            return 'pointing'
        elif any(word in text_lower for word in ['如何', '怎么', '方法']):
            return 'explaining'
        elif any(word in text_lower for word in ['项目', '经验']):
            return 'gesturing'
        else:
            return 'idle'
    
    def provide_feedback(self, 
                        feedback_text: str, 
                        feedback_type: str = "neutral") -> Dict[str, Any]:
        """
        提供反馈
        
        Args:
            feedback_text: 反馈内容
            feedback_type: 反馈类型 (positive, negative, neutral)
            
        Returns:
            反馈结果
        """
        try:
            # 根据反馈类型确定表情
            expression_map = {
                'positive': 'happy',
                'negative': 'concerned',
                'neutral': 'neutral',
                'encouraging': 'encouraging'
            }
            
            expression = expression_map.get(feedback_type, 'neutral')
            gesture = 'explaining' if feedback_type != 'neutral' else 'idle'
            
            # 生成虚拟人反馈
            avatar_result = self.create_avatar_response(feedback_text, expression, gesture)
            
            if avatar_result['success']:
                return {
                    'success': True,
                    'feedback': feedback_text,
                    'feedback_type': feedback_type,
                    'video_url': avatar_result['video_url'],
                    'audio_url': avatar_result['audio_url'],
                    'duration': avatar_result['duration'],
                    'timestamp': time.time()
                }
            else:
                return avatar_result
                
        except Exception as e:
            logger.error(f"虚拟人反馈失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_interview_session(self, session_id: str, interview_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        开始面试会话
        
        Args:
            session_id: 会话ID
            interview_config: 面试配置
            
        Returns:
            会话开始结果
        """
        try:
            # 创建会话
            session = {
                'session_id': session_id,
                'config': interview_config,
                'status': 'active',
                'start_time': time.time(),
                'current_question': 0,
                'questions': interview_config.get('questions', []),
                'responses': []
            }
            
            self.active_sessions[session_id] = session
            self.conversation_cache[session_id] = []
            
            # 生成开场白
            welcome_text = interview_config.get('welcome_message', 
                "欢迎参加面试！我是您的AI面试官，让我们开始今天的面试吧。")
            
            welcome_result = self.ask_question(welcome_text)
            
            if welcome_result['success']:
                session['welcome'] = welcome_result
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'welcome': welcome_result,
                    'total_questions': len(session['questions']),
                    'message': '面试会话已开始'
                }
            else:
                return welcome_result
                
        except Exception as e:
            logger.error(f"开始面试会话失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """
        获取下一个问题

        Args:
            session_id: 会话ID

        Returns:
            下一个问题结果
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }

            session = self.active_sessions[session_id]
            questions = session['questions']
            current_index = session['current_question']
            
            if current_index >= len(questions):
                return {
                    'success': False,
                    'error': '已无更多问题',
                    'completed': True
                }
            
            question = questions[current_index]
            question_text = question.get('content', question) if isinstance(question, dict) else question
            
            # 生成问题
            question_result = self.ask_question(question_text, {'question_index': current_index})
            
            if question_result['success']:
                session['current_question'] += 1
                
                return {
                    'success': True,
                    'question_index': current_index,
                    'total_questions': len(questions),
                    'question': question_result,
                    'remaining': len(questions) - current_index - 1
                }
            else:
                return question_result
                
        except Exception as e:
            logger.error(f"获取下一个问题失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def end_interview_session(self, session_id: str) -> Dict[str, Any]:
        """
        结束面试会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            结束结果
        """
        try:
            if session_id not in self.active_sessions:
                return {
                    'success': False,
                    'error': '会话不存在'
                }
            
            session = self.active_sessions[session_id]
            
            # 生成结束语
            farewell_text = "感谢您参加今天的面试！我们会尽快与您联系，祝您一切顺利！"
            farewell_result = self.provide_feedback(farewell_text, 'positive')
            
            session['status'] = 'completed'
            session['end_time'] = time.time()
            session['duration'] = session['end_time'] - session['start_time']
            
            if farewell_result['success']:
                return {
                    'success': True,
                    'session_id': session_id,
                    'farewell': farewell_result,
                    'duration': session['duration'],
                    'questions_completed': session['current_question'],
                    'message': '面试会话已结束'
                }
            else:
                return farewell_result
                
        except Exception as e:
            logger.error(f"结束面试会话失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                'session_id': session_id,
                'status': session['status'],
                'current_question': session['current_question'],
                'total_questions': len(session['questions']),
                'start_time': session['start_time'],
                'duration': time.time() - session['start_time'] if session['status'] == 'active' else session.get('duration', 0)
            }
        else:
            return {
                'error': '会话不存在'
            }
    
    def cleanup_session(self, session_id: str):
        """清理会话数据"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        if session_id in self.conversation_cache:
            del self.conversation_cache[session_id]
        
        logger.info(f"虚拟人会话数据已清理: {session_id}")
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有会话状态"""
        return {
            session_id: self.get_session_status(session_id)
            for session_id in self.active_sessions.keys()
        }


# 虚拟人WebSocket会话管理器
class AvatarWebSocketManager:
    """虚拟人WebSocket会话管理器"""

    def __init__(self):
        self.active_connections = {}  # 活跃的WebSocket连接
        self.session_streams = {}     # 会话流地址
        self.avatar_service = AvatarService()

    async def start_avatar_session(self, session_id: str, avatar_config: Dict[str, Any]) -> Dict[str, Any]:
        """启动虚拟人会话"""
        try:
            # 生成认证URL
            ws_url = self.avatar_service._generate_auth_url()

            # 生成唯一请求ID
            import uuid
            request_id = str(uuid.uuid4())

            # 启动协议
            start_request = {
                "header": {
                    "app_id": self.avatar_service.avatar_appid,
                    "request_id": request_id,
                    "ctrl": "start",
                    "scene_id": self.avatar_service.service_id
                },
                "parameter": {
                    "avatar": {
                        "stream": {
                            "protocol": "xrtc",
                            "fps": 25,
                            "bitrate": 2000,
                            "alpha": 0
                        },
                        "avatar_id": avatar_config.get("avatar_id", "198329296530575360"),
                        "width": 1080,
                        "height": 1920,
                        "scale": 1.0,
                        "move_h": 0,
                        "move_v": 0
                    },
                    "tts": {
                        "vcn": avatar_config.get("voice_style", ""),
                        "speed": int(avatar_config.get("voice_speed", 1.0) * 50),
                        "pitch": 50,
                        "volume": 50
                    }
                },
                "payload": {}
            }

            # 连接WebSocket
            websocket = await websockets.connect(ws_url)

            # 发送启动请求
            await websocket.send(json.dumps(start_request))

            # 接收启动响应
            start_response = await websocket.recv()
            start_data = json.loads(start_response)

            if start_data.get("header", {}).get("code") == 0:
                payload = start_data.get("payload", {})
                avatar_info = payload.get("avatar", {})
                stream_url = avatar_info.get("stream_url")
                stream_extend = avatar_info.get("stream_extend")

                # 保存连接和流信息
                self.active_connections[session_id] = websocket
                self.session_streams[session_id] = {
                    'stream_url': stream_url,
                    'stream_extend': stream_extend,
                    'avatar_config': avatar_config
                }

                logger.info(f"虚拟人会话启动成功: {session_id}, 流地址: {stream_url}")

                return {
                    'success': True,
                    'session_id': session_id,
                    'stream_url': stream_url,
                    'stream_extend': stream_extend,
                    'timestamp': time.time()
                }
            else:
                error_msg = start_data.get("header", {}).get("message", "启动失败")
                await websocket.close()
                return {
                    'success': False,
                    'error': f"虚拟人启动失败: {error_msg}"
                }

        except Exception as e:
            logger.error(f"启动虚拟人会话异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_text_to_avatar(self, session_id: str, text: str) -> Dict[str, Any]:
        """向虚拟人发送文本"""
        if session_id not in self.active_connections:
            return {
                'success': False,
                'error': '会话不存在'
            }

        try:
            websocket = self.active_connections[session_id]
            avatar_config = self.session_streams[session_id]['avatar_config']

            # 文本驱动请求
            import uuid
            text_request = {
                "header": {
                    "app_id": self.avatar_service.avatar_appid,
                    "ctrl": "text_driver",
                    "request_id": str(uuid.uuid4())
                },
                "parameter": {
                    "avatar_dispatch": {
                        "interactive_mode": 1
                    },
                    "tts": {
                        "vcn": avatar_config.get("voice_style", ""),
                        "speed": int(avatar_config.get("voice_speed", 1.0) * 50),
                        "pitch": 50,
                        "volume": 50
                    },
                    "air": {
                        "air": 1,
                        "add_nonsemantic": 1
                    }
                },
                "payload": {
                    "text": {
                        "content": text
                    }
                }
            }

            await websocket.send(json.dumps(text_request))

            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)

            if data.get("header", {}).get("code") == 0:
                return {
                    'success': True,
                    'message': '文本发送成功',
                    'timestamp': time.time()
                }
            else:
                error_msg = data.get("header", {}).get("message", "发送失败")
                return {
                    'success': False,
                    'error': f"文本发送失败: {error_msg}"
                }

        except Exception as e:
            logger.error(f"发送文本异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def close_avatar_session(self, session_id: str) -> Dict[str, Any]:
        """关闭虚拟人会话"""
        try:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                await websocket.close()
                del self.active_connections[session_id]

            if session_id in self.session_streams:
                del self.session_streams[session_id]

            return {
                'success': True,
                'message': '会话已关闭'
            }

        except Exception as e:
            logger.error(f"关闭会话异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        if session_id in self.session_streams:
            return {
                'success': True,
                'session_info': self.session_streams[session_id]
            }
        else:
            return {
                'success': False,
                'error': '会话不存在'
            }


# 全局虚拟人服务实例
avatar_service = AvatarService()
avatar_ws_manager = AvatarWebSocketManager()