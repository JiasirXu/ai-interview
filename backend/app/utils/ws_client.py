#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket客户端封装
"""

import asyncio
import json
import websockets
from loguru import logger
from typing import Optional, Dict, Any, Callable
import threading
import time
import hashlib
import hmac
import base64
from urllib.parse import urlencode, quote
from datetime import datetime

class WebSocketClient:
    """WebSocket客户端封装类"""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.headers = headers or {}
        self.websocket = None
        self.is_connected = False
        self.message_handlers = {}
        self.reconnect_interval = 5
        self.max_reconnect_attempts = 3
        self.reconnect_attempts = 0
        self._stop_event = threading.Event()
        self._loop = None
        self._thread = None

    async def connect(self):
        """连接WebSocket"""
        try:
            self.websocket = await websockets.connect(
                self.url,
                extra_headers=self.headers,
                ping_interval=20,
                ping_timeout=10
            )
            self.is_connected = True
            logger.info(f"WebSocket连接成功: {self.url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            return False

    async def disconnect(self):
        """断开WebSocket连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        self.is_connected = False
        logger.info("WebSocket连接已断开")

    async def send_message(self, message: Dict[str, Any]):
        """发送消息"""
        if not self.is_connected or not self.websocket:
            logger.error("WebSocket未连接，无法发送消息")
            return False
        
        try:
            await self.websocket.send(json.dumps(message, ensure_ascii=False))
            logger.debug(f"发送消息: {message}")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def receive_message(self):
        """接收消息"""
        if not self.is_connected or not self.websocket:
            return None
        
        try:
            message = await self.websocket.recv()
            logger.debug(f"接收消息: {message}")
            return json.loads(message)
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return None

    def register_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler

    async def handle_message(self, message: Dict[str, Any]):
        """处理接收到的消息"""
        message_type = message.get('type', 'unknown')
        handler = self.message_handlers.get(message_type)
        
        if handler:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
        else:
            logger.warning(f"未找到处理器: {message_type}")

    async def listen_messages(self):
        """监听消息"""
        while self.is_connected:
            try:
                message = await self.receive_message()
                if message:
                    await self.handle_message(message)
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket连接已关闭")
                break
            except Exception as e:
                logger.error(f"监听消息异常: {e}")
                break

    def start_background_task(self, coro):
        """在后台线程中启动异步任务"""
        def run_in_thread():
            try:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                self._loop.run_until_complete(coro)
            except Exception as e:
                logger.error(f"后台任务异常: {e}")
            finally:
                if self._loop:
                    self._loop.close()

        self._thread = threading.Thread(target=run_in_thread)
        self._thread.daemon = True
        self._thread.start()

    def stop_background_task(self):
        """停止后台任务"""
        self._stop_event.set()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)

    async def _background_task(self):
        """后台任务"""
        while not self._stop_event.is_set():
            try:
                if not self.is_connected:
                    # 尝试重连
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        logger.info(f"尝试重连... ({self.reconnect_attempts + 1}/{self.max_reconnect_attempts})")
                        if await self.connect():
                            self.reconnect_attempts = 0
                            await self.listen_messages()
                        else:
                            self.reconnect_attempts += 1
                            await asyncio.sleep(self.reconnect_interval)
                    else:
                        logger.error("重连次数超限，停止重连")
                        break
                else:
                    await self.listen_messages()
                    
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"后台任务错误: {e}")
                await asyncio.sleep(5)
    
    def __del__(self):
        """析构函数"""
        if hasattr(self, '_stop_event'):
            self.stop_background_task()


class SparkWebSocketClient(WebSocketClient):
    """讯飞Spark WebSocket客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.spark_config = config.get('SPARK', {})
        self.websocket_url = self.spark_config.get('WEBSOCKET_URL', '')
        self.appid = config.get('APPID', '')
        self.api_key = config.get('APIKey', '')
        self.api_secret = config.get('APISecret', '')
        
        # 构建认证URL
        auth_url = self._build_auth_url()
        super().__init__(auth_url)
        
        self.conversation_id = None
        self.session_active = False
        self.message_queue = asyncio.Queue()
        
    def _build_auth_url(self) -> str:
        """构建带认证的WebSocket URL"""
        try:
            # 讯飞WebSocket认证URL构建
            # 参考：https://www.xfyun.cn/doc/spark/Web.html
            
            # 生成RFC1123格式的时间戳
            now = datetime.utcnow()
            date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            # 拼接字符串
            signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /v3.1/chat HTTP/1.1"
            
            # 进行hmac-sha256加密
            signature_sha = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            
            # 进行base64编码
            signature_sha_str = base64.b64encode(signature_sha).decode('utf-8')
            
            # 构建authorization
            authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_str}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
            
            # 构建请求参数
            params = {
                'authorization': authorization,
                'date': date,
                'host': 'spark-api.xf-yun.com'
            }
            
            # 构建最终URL
            url = f"{self.websocket_url}?{urlencode(params)}"
            logger.debug(f"构建的WebSocket URL: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"构建认证URL失败: {e}")
            return self.websocket_url
    
    async def start_conversation(self, system_prompt: str = None):
        """开始对话会话"""
        if not await self.connect():
            return False
        
        # 注册消息处理器
        self.register_handler('message', self._handle_message)
        self.register_handler('error', self._handle_error)
        
        # 发送初始化消息
        init_message = {
            "header": {
                "app_id": self.appid,
                "uid": "user_001"
            },
            "parameter": {
                "chat": {
                    "domain": "generalv3",
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "system",
                            "content": system_prompt or "你是一个专业的AI助手"
                        }
                    ]
                }
            }
        }
        
        success = await self.send_message(init_message)
        if success:
            self.session_active = True
            logger.info("Spark WebSocket会话启动成功")
            
            # 启动消息监听
            asyncio.create_task(self.listen_messages())
            
        return success
    
    async def send_user_message(self, text: str, emotion_data: Dict[str, Any] = None):
        """发送用户消息"""
        if not self.session_active:
            logger.error("会话未激活")
            return False
        
        message = {
            "header": {
                "app_id": self.appid,
                "uid": "user_001"
            },
            "parameter": {
                "chat": {
                    "domain": "generalv3",
                    "temperature": 0.7,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {
                            "role": "user",
                            "content": text
                        }
                    ]
                }
            }
        }
        
        # 添加情绪数据
        if emotion_data:
            message["payload"]["emotion"] = emotion_data
        
        return await self.send_message(message)
    
    async def _handle_message(self, message: Dict[str, Any]):
        """处理接收到的消息"""
        try:
            # 解析讯飞返回的消息格式
            payload = message.get('payload', {})
            choices = payload.get('choices', {})
            text = choices.get('text', [])
            
            if text:
                content = text[0].get('content', '')
                await self.message_queue.put({
                    'type': 'text',
                    'content': content,
                    'status': payload.get('status', 0)
                })
                
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    async def _handle_error(self, message: Dict[str, Any]):
        """处理错误消息"""
        logger.error(f"WebSocket错误: {message}")
        await self.message_queue.put({
            'type': 'error',
            'error': message
        })
    
    async def receive_ai_response(self):
        """接收AI响应"""
        try:
            # 从消息队列获取响应
            response = await asyncio.wait_for(self.message_queue.get(), timeout=30)
            return response
        except asyncio.TimeoutError:
            logger.warning("等待AI响应超时")
            return None
        except Exception as e:
            logger.error(f"接收AI响应失败: {e}")
            return None
    
    async def end_conversation(self):
        """结束对话"""
        self.session_active = False
        await self.disconnect()
        logger.info("Spark WebSocket会话已结束") 