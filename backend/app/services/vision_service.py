#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人脸检测 + 表情识别 WebAPI 调用
"""

import requests
import base64
import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from loguru import logger
from flask import current_app
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 条件导入截图相关模块
try:
    import pyautogui
    import io
    from PIL import Image
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    logger.warning("pyautogui或PIL未安装，截图功能将使用模拟数据")

class VisionService:
    """视觉服务"""
    
    def __init__(self, config=None):
        self.config = config
        self.face_config = None
        self.face_detection_url = None
        self.emotion_recognition_url = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.active_sessions = {}
        self.emotion_history = {}
        self._initialized = False
        self.appid = None
        self.apisecret = None
        self.apikey = None
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            if self.config is None:
                from flask import current_app
                self.config = current_app.config.get('XUNFEI_CONFIG', {})
            
            # 从主配置中获取通用认证信息
            self.appid = self.config.get('APPID')
            self.apikey = self.config.get('APIKey')
            self.apisecret = self.config.get('APISecret')

            self.face_config = self.config.get('FACE', {})
            self.face_detection_url = self.face_config.get('DETECTION_URL')
            self.emotion_recognition_url = self.face_config.get('EXPRESSION_URL')
            self._initialized = True
    
    def _get_face_detection_headers(self) -> Dict[str, str]:
        """获取人脸检测API的认证headers"""
        self._ensure_initialized()
        
        # 根据文档，人脸检测WebAPI需要特定的认证头
        # https://www.xfyun.cn/doc/face/xf-face-detect/API.html
        x_time = str(int(time.time()))
        
        # 1. 创建 x-param
        param_dict = {"sdk_version": "1.0"}
        param_base64 = base64.b64encode(json.dumps(param_dict).encode('utf-8')).decode('utf-8')
        
        # 2. 创建 x-check-sum
        checksum_str = self.apikey + x_time + param_base64
        checksum = hashlib.md5(checksum_str.encode('utf-8')).hexdigest()

        return {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'X-Appid': self.appid,
            'X-CurTime': x_time,
            'X-Param': param_base64,
            'X-CheckSum': checksum
        }
    
    def detect_faces(self, image_data: bytes) -> Dict[str, Any]:
        """
        人脸检测
        
        Args:
            image_data: 图片数据
            
        Returns:
            检测结果
        """
        self._ensure_initialized()
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "image": image_base64,
                # 根据文档，attribute和landmark是布尔值
                "attribute": 1,
                "landmark": 1
            }
            
            response = requests.post(
                self.face_detection_url,
                headers=self._get_face_detection_headers(),
                data=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return {
                        'success': True,
                        'data': result.get('data', {}),
                        'face_count': len(result.get('data', {}).get('face_list', [])),
                        'timestamp': time.time()
                    }
                else:
                    logger.error(f"人脸检测API返回错误: {result}")
                    return {
                        'success': False,
                        'error': f"API错误: {result.get('desc', '未知API错误')}"
                    }
            else:
                logger.error(f"人脸检测失败: {response.status_code}, {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP错误: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"人脸检测异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def recognize_emotion(self, image_data: bytes) -> Dict[str, Any]:
        """
        表情识别
        
        Args:
            image_data: 图片数据
            
        Returns:
            识别结果
        """
        self._ensure_initialized()
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "appid": self.appid,
                "image": image_base64,
                "scene": "default", # 'default' 场景更通用
            }
            
            # 表情分析API使用不同的认证方式，通常是签名在请求体内
            # 这里我们假设它不需要特殊的header，凭证在body中
            response = requests.post(
                self.emotion_recognition_url,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                # 根据文档，code为0表示成功
                if result.get('code') == 0:
                    return {
                        'success': True,
                        'data': result.get('data', {}),
                        'timestamp': time.time()
                    }
                else:
                    logger.error(f"表情识别API返回错误: {result}")
                    return {
                        'success': False,
                        'error': f"API错误: {result.get('desc', '未知API错误')}"
                    }
            else:
                logger.error(f"表情识别失败: {response.status_code}, {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP错误: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"表情识别异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_face_and_emotion(self, image_data: bytes) -> Dict[str, Any]:
        """
        综合分析人脸和表情
        
        Args:
            image_data: 图片数据
            
        Returns:
            分析结果
        """
        try:
            # 并行调用人脸检测和表情识别
            face_future = self.executor.submit(self.detect_faces, image_data)
            emotion_future = self.executor.submit(self.recognize_emotion, image_data)
            
            # 等待结果
            face_result = face_future.result(timeout=15)
            emotion_result = emotion_future.result(timeout=15)
            
            # 综合结果
            analysis = {
                'success': True,
                'timestamp': time.time(),
                'face_detection': face_result,
                'emotion_recognition': emotion_result
            }
            
            # 提取关键信息
            if face_result['success'] and emotion_result.get('success', False): # 确保emotion_result也成功
                analysis['summary'] = self._extract_emotion_summary(face_result, emotion_result)
            elif not face_result['success']:
                analysis['success'] = False
                analysis['error'] = face_result.get('error', '人脸检测失败')
            else:
                analysis['summary'] = self._extract_emotion_summary(face_result, {}) # 即使表情识别失败，也尝试提取部分信息
            
            return analysis
            
        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_expression_xunfei(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        使用讯飞人脸表情分析API分析表情

        Args:
            image_data: 图片数据

        Returns:
            分析结果
        """
        try:
            # 确保在Flask应用上下文中初始化
            try:
                self._ensure_initialized()
            except RuntimeError as e:
                if "application context" in str(e):
                    # 如果没有应用上下文，尝试获取
                    from flask import current_app
                    if current_app:
                        with current_app.app_context():
                            self._ensure_initialized()
                    else:
                        logger.error("无法获取Flask应用上下文")
                        return None
                else:
                    raise

            # 讯飞人脸表情分析API地址
            url = "http://tupapi.xfyun.cn/v1/expression"

            # 构建请求头 - 按照讯飞API规范
            headers = self._build_xunfei_expression_headers(image_data)

            # 发送请求 - 图片数据放在请求体中
            response = requests.post(url, headers=headers, data=image_data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"讯飞人脸表情分析成功: {result}")
                return self._parse_expression_result(result)
            else:
                logger.error(f"讯飞人脸表情分析失败: {response.status_code}, {response.text}")
                return None

        except Exception as e:
            logger.error(f"讯飞表情分析异常: {e}")
            return None

    def _build_xunfei_expression_headers(self, image_data: bytes) -> Dict[str, str]:
        """构建讯飞人脸表情分析API请求头"""
        try:
            # 当前UTC时间戳
            cur_time = str(int(time.time()))

            # 业务参数
            param = {
                "image_name": "screenshot.jpg"
            }
            param_str = json.dumps(param)

            # Base64编码参数
            x_param = base64.b64encode(param_str.encode('utf-8')).decode('utf-8')

            # 计算签名 - MD5(APIKey + X-CurTime + X-Param)
            sign_str = self.apikey + cur_time + x_param
            x_checksum = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

            # 构建请求头
            headers = {
                'X-Appid': self.appid,
                'X-CurTime': cur_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum,
                'Content-Type': 'application/octet-stream'
            }

            return headers

        except Exception as e:
            logger.error(f"构建讯飞表情分析请求头失败: {e}")
            return {}

    def _parse_expression_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析讯飞人脸表情分析结果"""
        try:
            if result.get('code') != 0:
                logger.error(f"讯飞表情分析返回错误: {result}")
                return {}

            data = result.get('data', {})
            file_list = data.get('fileList', [])

            if not file_list:
                return {'emotion': 'unknown', 'confidence': 0.0}

            # 获取第一个文件的分析结果
            first_file = file_list[0]
            label = first_file.get('label', -1)
            rate = first_file.get('rate', 0.0)

            # 表情标签映射
            emotion_map = {
                0: 'other',      # 其他(非人脸表情图片)
                1: 'other_expression',  # 其他表情
                2: 'joy',        # 喜悦
                3: 'anger',      # 愤怒
                4: 'sadness',    # 悲伤
                5: 'fear',       # 惊恐
                6: 'disgust',    # 厌恶
                7: 'neutral'     # 中性
            }

            emotion = emotion_map.get(label, 'unknown')

            parsed_result = {
                'emotion': emotion,
                'confidence': rate,
                'label': label,
                'review': first_file.get('review', False),
                'raw_result': result
            }

            logger.info(f"解析表情结果: 情绪={emotion}, 置信度={rate:.3f}")
            return parsed_result

        except Exception as e:
            logger.error(f"解析表情分析结果异常: {e}")
            return {'emotion': 'unknown', 'confidence': 0.0}
    
    def _extract_emotion_summary(self, face_result: Dict[str, Any], emotion_result: Dict[str, Any]) -> Dict[str, Any]:
        """提取表情摘要"""
        summary = {
            'confidence_level': 'low',
            'dominant_emotion': 'neutral',
            'attention_level': 'medium',
            'engagement_score': 0.5
        }
        
        try:
            # 从人脸检测结果中提取信息
            faces = face_result.get('data', {}).get('face_list', [])
            if faces:
                face = faces[0]  # 取第一个人脸
                
                # 提取姿态信息
                pose = face.get('location', {})
                if pose:
                    # 计算注意力水平（简化版）
                    # 假设正脸角度为0，偏离角度越大注意力越低
                    # roll, pitch, yaw 范围通常在-90到90之间
                    head_pose_score = 1.0 - (abs(pose.get('pitch', 0)) + abs(pose.get('yaw', 0))) / 180.0
                    summary['attention_level'] = 'high' if head_pose_score > 0.85 else 'medium' if head_pose_score > 0.6 else 'low'
            
            # 从表情识别结果中提取信息
            emotion_data = emotion_result.get('data', {})
            if emotion_data:
                # 表情API返回的是各类情绪的置信度
                emotion_list = emotion_data.get('expression', [])
                if emotion_list:
                    dominant_emotion = max(emotion_list, key=lambda x: x.get('confidence', 0))
                    summary['dominant_emotion'] = dominant_emotion.get('type', 'neutral')
                    confidence = dominant_emotion.get('confidence', 0) / 100.0 # 转换为0-1
                    summary['confidence_level'] = 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low'
                    
                    # 计算参与度分数
                    positive_emotions = ['happy', 'surprised']
                    negative_emotions = ['sad', 'angry', 'fear', 'disgust']
                    
                    emotion_name = summary['dominant_emotion']
                    if emotion_name in positive_emotions:
                        summary['engagement_score'] = 0.7 + (confidence * 0.3) # 基础分+置信度加权
                    elif emotion_name in negative_emotions:
                        summary['engagement_score'] = 0.4 - (confidence * 0.3)
                    else: # neutral
                        summary['engagement_score'] = 0.5
            
        except Exception as e:
            logger.error(f"提取表情摘要失败: {e}")
        
        return summary
    
    def analyze_and_store_emotion(self, session_id: str, image_data: bytes) -> Dict[str, Any]:
        """
        分析单张图片并为会话存储情感结果
        
        Args:
            session_id: 会话ID
            image_data: 从前端发送的图片数据
            
        Returns:
            分析结果的摘要
        """
        self._ensure_initialized()
        
        analysis_result = self.analyze_face_and_emotion(image_data)
        
        if not analysis_result['success']:
            logger.error(f"会话 {session_id} 的图像分析失败: {analysis_result.get('error')}")
            return analysis_result

        summary = analysis_result.get('summary', {})
        
        # 为会话初始化历史记录
        if session_id not in self.emotion_history:
            self.emotion_history[session_id] = []
        
        # 存储结果
        storage_record = {
            'timestamp': time.time(),
            'summary': summary
        }
        self.emotion_history[session_id].append(storage_record)

        # 保持历史记录不超过200条
        if len(self.emotion_history[session_id]) > 200:
            self.emotion_history[session_id] = self.emotion_history[session_id][-200:]
            
        logger.info(f"为会话 {session_id} 存储了新的情感分析结果: {summary}")
        
        return {
            'success': True,
            'summary': summary
        }

    def start_continuous_monitoring(self, session_id: str, interval: int = 5) -> bool:
        """
        开始持续监控
        
        Args:
            session_id: 会话ID
            interval: 监控间隔（秒）
            
        Returns:
            是否启动成功
        """
        try:
            if session_id in self.active_sessions:
                logger.warning(f"会话 {session_id} 已在监控中")
                return False
            
            # 创建监控任务
            monitor_task = {
                'session_id': session_id,
                'interval': interval,
                'active': True,
                'last_capture': None,
                'results': []
            }
            
            self.active_sessions[session_id] = monitor_task
            self.emotion_history[session_id] = []
            
            # 启动监控任务
            threading.Thread(
                target=self._monitoring_loop, 
                args=(session_id,),
                daemon=True
            ).start()
            
            logger.info(f"视觉监控已启动: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"启动视觉监控失败: {e}")
            return False
    
    def _monitoring_loop(self, session_id: str):
        """监控循环"""
        while self.active_sessions.get(session_id, {}).get('active', False):
            try:
                # 这里需要实现截图逻辑
                # 暂时使用模拟数据
                time.sleep(self.active_sessions[session_id]['interval'])
                
                # 模拟分析结果
                mock_result = {
                    'success': True,
                    'timestamp': time.time(),
                    'summary': {
                        'confidence_level': 'medium',
                        'dominant_emotion': 'neutral',
                        'attention_level': 'high',
                        'engagement_score': 0.7
                    }
                }
                
                # 保存结果
                self.active_sessions[session_id]['results'].append(mock_result)
                self.emotion_history[session_id].append(mock_result)
                
                # 保持历史记录不超过100条
                if len(self.emotion_history[session_id]) > 100:
                    self.emotion_history[session_id] = self.emotion_history[session_id][-100:]
                
            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                break
    
    def stop_continuous_monitoring(self, session_id: str) -> bool:
        """
        停止持续监控
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否停止成功
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['active'] = False
                del self.active_sessions[session_id]
                logger.info(f"视觉监控已停止: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"停止视觉监控失败: {e}")
            return False
    
    def get_monitoring_status(self, session_id: str) -> Dict[str, Any]:
        """获取监控状态"""
        if session_id in self.active_sessions:
            task = self.active_sessions[session_id]
            return {
                'active': task['active'],
                'interval': task['interval'],
                'result_count': len(task['results']),
                'last_capture': task['last_capture']
            }
        else:
            return {
                'active': False,
                'message': '未找到监控会话'
            }
    
    def get_emotion_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取表情历史"""
        if session_id in self.emotion_history:
            history = self.emotion_history[session_id]
            return history[-limit:] if len(history) > limit else history
        return []
    
    def get_emotion_statistics(self, session_id: str) -> Dict[str, Any]:
        """获取表情统计"""
        if session_id not in self.emotion_history:
            return {'error': '未找到历史数据'}
        
        history = self.emotion_history[session_id]
        if not history:
            return {'error': '历史数据为空'}
        
        try:
            # 统计表情分布
            emotion_counts = {}
            total_engagement = 0
            attention_levels = {'high': 0, 'medium': 0, 'low': 0}
            
            for record in history:
                summary = record.get('summary', {})
                
                emotion = summary.get('dominant_emotion', 'neutral')
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                total_engagement += summary.get('engagement_score', 0)
                
                attention = summary.get('attention_level', 'medium')
                attention_levels[attention] = attention_levels.get(attention, 0) + 1
            
            # 计算统计值
            avg_engagement = total_engagement / len(history)
            most_common_emotion = max(emotion_counts, key=emotion_counts.get)
            
            return {
                'total_samples': len(history),
                'emotion_distribution': emotion_counts,
                'most_common_emotion': most_common_emotion,
                'average_engagement': round(avg_engagement, 2),
                'attention_distribution': attention_levels
            }
            
        except Exception as e:
            logger.error(f"计算表情统计失败: {e}")
            return {'error': str(e)}
    
    def clear_session_data(self, session_id: str):
        """清理会话数据"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        if session_id in self.emotion_history:
            del self.emotion_history[session_id]
        
        logger.info(f"会话数据已清理: {session_id}")

    def capture_screenshot(self) -> Optional[bytes]:
        """
        截取屏幕截图

        Returns:
            图片数据（bytes格式）
        """
        try:
            if SCREENSHOT_AVAILABLE:
                # 截取屏幕
                screenshot = pyautogui.screenshot()

                # 转换为bytes
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='JPEG', quality=85)
                img_data = img_buffer.getvalue()

                logger.info(f"截图成功，大小: {len(img_data)} bytes")
                return img_data
            else:
                logger.warning("截图模块不可用，使用模拟截图数据")
                return self._create_mock_image()

        except Exception as e:
            logger.error(f"截图失败: {e}")
            return self._create_mock_image()

    def _create_mock_image(self) -> bytes:
        """创建模拟图片数据"""
        if SCREENSHOT_AVAILABLE:
            try:
                # 创建一个简单的模拟图片
                img = Image.new('RGB', (640, 480), color='lightblue')
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG')
                return img_buffer.getvalue()
            except Exception as e:
                logger.error(f"创建模拟图片失败: {e}")

        # 返回一个最小的JPEG头
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'


# 为VisionService添加新方法
async def analyze_image_method(self, image_data: str):
    """分析图像数据（表情、姿态、眼神等）- 使用真实API"""
    try:
        # 解码base64图片数据
        import base64
        if ',' in image_data:
            image_bytes = base64.b64decode(image_data.split(',')[1])
        else:
            image_bytes = base64.b64decode(image_data)

        # 使用讯飞人脸检测API
        face_result = vision_service.detect_face_xunfei(image_bytes)
        if not face_result or not face_result.get('success'):
            logger.warning("人脸检测失败")
            return self._get_default_analysis_result()

        # 使用讯飞表情分析API
        emotion_result = vision_service.analyze_expression_xunfei(image_bytes)

        # 综合分析结果
        analysis_result = vision_service.comprehensive_analysis(image_bytes)

        # 在终端显示分析结果
        if analysis_result.get('success'):
            summary = analysis_result.get('summary', '分析完成')
            print(f"\n👁️ [视觉分析] {summary}")
            logger.info(f"视觉分析结果: {summary}")

        return analysis_result

    except Exception as e:
        logger.error(f"视觉分析失败: {e}")
        return {
            'success': False,
            'error': str(e),
            'summary': '视觉分析失败'
        }

def _get_default_analysis_result() -> Dict[str, Any]:
    """获取默认分析结果"""
    return {
        'success': True,
        'face_detected': False,
        'emotion': 'neutral',
        'eye_contact': 0.5,
        'posture_score': 0.5,
        'facial_expression': 'neutral',
        'head_pose': {
            'pitch': 0,
            'yaw': 0,
            'roll': 0
        },
        'confidence': 0.5,
        'summary': '无法检测到人脸，建议调整摄像头角度'
    }

# 动态添加方法到VisionService类
VisionService.analyze_image = analyze_image_method

# 全局服务实例
vision_service = VisionService()