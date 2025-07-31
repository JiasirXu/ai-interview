#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文档识别HTTP API + 简历结构提取
"""

import os
import requests
import base64
import time
from typing import Dict, Any, Optional, Tuple, List
from loguru import logger
from werkzeug.utils import secure_filename
from flask import current_app
from app.utils.parser import TextCleaner, JSONParser
from app.utils.pdf_processor import PDFProcessor
from app.services.spark_service import spark_service
import pdfplumber
import docx
from PIL import Image
import io

class ResumeService:
    """简历服务"""
    
    def __init__(self, config=None):
        self.config = config
        self.ocr_config = None
        self.ocr_url = None
        self.upload_folder = None
        self.allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
        self._initialized = False
        self.appid = None
        self.apikey = None
        self.apisecret = None
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            if self.config is None:
                from flask import current_app
                self.config = current_app.config.get('XUNFEI_CONFIG', {})
                self.upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')

            # 从主配置中获取通用认证信息
            self.appid = self.config.get('APPID')
            self.apikey = self.config.get('APIKey')
            self.apisecret = self.config.get('APISecret')
            
            self.ocr_config = self.config.get('OCR', {})
            self.ocr_url = self.ocr_config.get('URL')
            self._initialized = True
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证headers"""
        self._ensure_initialized()
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.apikey}",
        }
    
    def save_uploaded_file(self, file, user_id: int) -> Tuple[bool, str, str]:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件对象
            user_id: 用户ID
            
        Returns:
            (是否成功, 文件路径, 错误信息)
        """
        try:
            self._ensure_initialized()
            
            # 验证文件
            if not file or not file.filename:
                return False, "", "没有选择文件"
            
            # 检查文件扩展名
            filename = secure_filename(file.filename)
            if '.' not in filename:
                return False, "", "文件格式错误"
            
            file_ext = filename.rsplit('.', 1)[1].lower()
            if file_ext not in self.allowed_extensions:
                return False, "", f"不支持的文件格式，仅支持: {', '.join(self.allowed_extensions)}"
            
            # 创建用户目录
            user_folder = os.path.join(self.upload_folder, str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            
            # 生成唯一文件名
            timestamp = str(int(time.time() * 1000))
            new_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(user_folder, new_filename)
            
            # 保存文件
            file.save(file_path)
            
            logger.info(f"文件保存成功: {file_path}")
            return True, file_path, ""
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            return False, "", str(e)
    
    def extract_text_from_pdf(self, file_path: str) -> Tuple[bool, str, List]:
        """
        从PDF中提取文本（兼容旧版本）
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            (是否成功, 文本内容, 图片列表)
        """
        try:
            # 使用新的智能文本提取
            result = PDFProcessor.intelligent_extract_text(file_path)
            
            if result['success']:
                if result['method'] == 'text_extraction':
                    # 直接文本提取成功
                    return True, result['text_content'], []
                elif result['method'] == 'ocr_required':
                    # 需要OCR处理
                    return False, result.get('fallback_text', ''), result.get('images', [])
                else:
                    return False, "", []
            else:
                return False, "", []
                
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            return False, "", []
    
    def extract_text_from_docx(self, file_path: str) -> Tuple[bool, str]:
        """
        从Word文档中提取文本
        
        Args:
            file_path: Word文档路径
            
        Returns:
            (是否成功, 文本内容)
        """
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return True, text
        except Exception as e:
            logger.error(f"Word文档提取失败: {e}")
            return False, ""
    
    def call_xunfei_ocr(self, image_data: bytes) -> Dict[str, Any]:
        """
        调用讯飞OCR API
        
        Args:
            image_data: 图片数据
            
        Returns:
            OCR结果
        """
        try:
            self._ensure_initialized()
            
            if not self.ocr_url:
                return {
                    'success': False,
                    'error': 'OCR服务未配置'
                }
            
            # 编码图片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 构造请求参数
            params = {
                'image': image_base64,
                'language_type': 'CHN_ENG',
                'detect_direction': 'true',
                'probability': 'true'
            }
            
            # 发送请求
            response = requests.post(
                self.ocr_url,
                json=params,
                headers=self._get_auth_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("讯飞OCR调用成功")
                return {
                    'success': True,
                    'data': result
                }
            else:
                logger.error(f"讯飞OCR调用失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f"OCR API错误: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"讯飞OCR调用异常: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text_from_doc(self, file_path: str) -> Dict[str, Any]:
        """
        从文档中提取文本（统一入口）
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取结果
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                # 使用新的PDF智能处理
                result = PDFProcessor.intelligent_extract_text(file_path)
                
                if result['success']:
                    if result['method'] == 'text_extraction':
                        # 直接文本提取成功
                        return {
                            'success': True,
                            'text': result['text_content'],
                            'method': 'direct_extraction',
                            'confidence': result['confidence']
                        }
                    elif result['method'] == 'ocr_required':
                        # 需要OCR处理
                        ocr_text = ""
                        images = result.get('images', [])
                        
                        for image_info in images:
                            try:
                                # 解码base64图片
                                image_data = base64.b64decode(image_info['image'])
                                
                                # 调用OCR
                                ocr_result = self.call_xunfei_ocr(image_data)
                                if ocr_result['success']:
                                    ocr_data = ocr_result['data']
                                    if 'words_result' in ocr_data:
                                        for word_info in ocr_data['words_result']:
                                            ocr_text += word_info.get('words', '') + "\n"
                                            
                            except Exception as e:
                                logger.warning(f"OCR处理第{image_info['page']}页失败: {e}")
                                continue
                        
                        return {
                            'success': True,
                            'text': ocr_text,
                            'method': 'ocr_extraction',
                            'confidence': result['confidence']
                        }
                    else:
                        return {
                            'success': False,
                            'error': '无法处理PDF文件'
                        }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', '无法处理PDF文件')
                    }
            
            elif file_ext == '.docx':
                success, text = self.extract_text_from_docx(file_path)
                if success:
                    return {
                        'success': True,
                        'text': text,
                        'method': 'direct_extraction',
                        'confidence': 1.0
                    }
                else:
                    return {
                        'success': False,
                        'error': '无法从Word文档中提取文本'
                    }
            
            elif file_ext in ['.jpg', '.jpeg', '.png']:
                # 直接调用OCR
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                ocr_result = self.call_xunfei_ocr(image_data)
                if ocr_result['success']:
                    ocr_data = ocr_result['data']
                    text = ""
                    if 'words_result' in ocr_data:
                        for word_info in ocr_data['words_result']:
                            text += word_info.get('words', '') + "\n"
                    
                    return {
                        'success': True,
                        'text': text,
                        'method': 'ocr_extraction',
                        'confidence': 0.8
                    }
                else:
                    return {
                        'success': False,
                        'error': ocr_result['error']
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'不支持的文件格式: {file_ext}'
                }
            
        except Exception as e:
            logger.error(f"文档文本提取失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_resume_insight(self, text: str) -> Dict[str, Any]:
        """
        获取简历智能分析结果
        
        Args:
            text: 简历文本
            
        Returns:
            分析结果
        """
        try:
            # 首先清洗文本
            cleaned_text = TextCleaner.clean_resume_text(text)
            
            # 调用Spark服务分析
            analysis_result = spark_service.analyze_resume(cleaned_text)
            
            if analysis_result['success']:
                return {
                    'success': True,
                    'analysis': analysis_result['analysis'],
                    'cleaned_text': cleaned_text
                }
            else:
                return analysis_result
            
        except Exception as e:
            logger.error(f"简历智能分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_resume_file(self, file_path: str) -> Dict[str, Any]:
        """
        处理简历文件（完整流程）
        
        Args:
            file_path: 简历文件路径
            
        Returns:
            处理结果
        """
        try:
            # 1. 验证文件
            validation_result = PDFProcessor.validate_pdf_file(file_path)
            if not validation_result['success'] and file_path.lower().endswith('.pdf'):
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # 2. 提取文本
            extraction_result = self.extract_text_from_doc(file_path)
            
            if not extraction_result['success']:
                return extraction_result
            
            raw_text = extraction_result['text']
            
            # 3. 清洗文本
            cleaned_text = TextCleaner.clean_resume_text(raw_text)
            
            # 4. 提取基本信息
            contact_info = TextCleaner.extract_contact_info(cleaned_text)
            
            # 5. 调用AI分析
            logger.info(f"开始AI分析，文本长度: {len(cleaned_text)}")
            logger.debug(f"清洗后文本前500字符: {cleaned_text[:500]}")
            ai_result = self.get_resume_insight(cleaned_text)
            
            result = {
                'success': True,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'contact_info': contact_info,
                'extraction_method': extraction_result['method'],
                'confidence': extraction_result.get('confidence', 0.8)
            }
            
            # 添加AI分析结果
            if ai_result['success']:
                analysis = ai_result['analysis']
                logger.info(f"AI分析成功，识别到技能数量: {len(analysis.get('skills', []))}")
                logger.info(f"识别到的技能: {analysis.get('skills', [])}")
                logger.info(f"识别到项目数量: {len(analysis.get('projects', []))}")

                result.update({
                    'ai_analysis': analysis,
                    'skills': analysis.get('skills', []),
                    'projects': analysis.get('projects', []),
                    'positions': analysis.get('positions', []),
                    'experience_years': analysis.get('experience_years', 0),
                    'strengths': analysis.get('strengths', '')
                })
            else:
                # AI分析失败时，使用升级版本地分析器作为备用方案
                logger.warning(f"AI分析失败，使用升级版本地分析器: {ai_result.get('error', 'Unknown error')}")
                from app.utils.resume_analyzer import ResumeAnalyzer
                local_analysis = ResumeAnalyzer.analyze_resume(cleaned_text)

                # 使用升级版本地分析器的丰富数据
                result.update({
                    'ai_analysis': None,
                    'ai_error': ai_result['error'],
                    'personal_info': local_analysis.get('personal_info', {}),
                    'skills': local_analysis.get('skills', []),
                    'skill_categories': local_analysis.get('skill_categories', {}),
                    'projects': local_analysis.get('projects', []),
                    'education': local_analysis.get('education', []),
                    'work_experience': local_analysis.get('work_experience', []),
                    'positions': local_analysis.get('recommended_positions', []),  # 本地分析器现在也提供岗位推荐
                    'experience_years': local_analysis.get('stats', {}).get('estimated_experience_years', 0),
                    'completeness_score': local_analysis.get('completeness_score', 0),
                    'strengths': f'使用升级版本地分析器提取的信息 (完整度: {local_analysis.get("completeness_score", 0)}%)',
                    'local_analyzer_version': local_analysis.get('analyzer_version', '2.0')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"处理简历文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_resume_file(self, file_path: str) -> bool:
        """
        删除简历文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"简历文件已删除: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除简历文件失败: {e}")
            return False


# 全局服务实例
resume_service = ResumeService() 