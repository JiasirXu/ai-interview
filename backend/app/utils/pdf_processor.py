#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF处理工具类
"""

import os
import re
import base64
from io import BytesIO
from PIL import Image
import pdfplumber
from pdf2image import convert_from_path
from loguru import logger

class PDFProcessor:
    """PDF处理器"""
    
    @staticmethod
    def analyze_pdf_type(file_path):
        """
        分析PDF类型（文字型 vs 图片型）
        
        Args:
            file_path (str): PDF文件路径
            
        Returns:
            dict: PDF分析结果
        """
        try:
            text_content = ""
            total_pages = 0
            text_pages = 0
            image_pages = 0
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    try:
                        # 提取文本
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content += page_text.strip()
                            text_pages += 1
                        
                        # 检查是否有图片
                        if page.images:
                            image_pages += 1
                            
                    except Exception as e:
                        logger.warning(f"分析第{page_num + 1}页失败: {e}")
                        continue
            
            # 计算文字覆盖率
            text_coverage = text_pages / total_pages if total_pages > 0 else 0
            
            # 文字内容质量评估
            text_quality = PDFProcessor._evaluate_text_quality(text_content)
            
            # 确定PDF类型
            if text_coverage >= 0.7 and text_quality >= 0.6:
                pdf_type = "text"
            elif text_coverage >= 0.3 and text_quality >= 0.4:
                pdf_type = "mixed"
            else:
                pdf_type = "image"
            
            return {
                'success': True,
                'pdf_type': pdf_type,
                'total_pages': total_pages,
                'text_pages': text_pages,
                'image_pages': image_pages,
                'text_coverage': text_coverage,
                'text_quality': text_quality,
                'text_content': text_content if pdf_type == "text" else "",
                'recommendation': PDFProcessor._get_processing_recommendation(pdf_type)
            }
            
        except Exception as e:
            logger.error(f"PDF类型分析失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'pdf_type': 'unknown'
            }
    
    @staticmethod
    def _evaluate_text_quality(text_content):
        """
        评估文本质量
        
        Args:
            text_content (str): 文本内容
            
        Returns:
            float: 质量评分 (0-1)
        """
        if not text_content:
            return 0.0
        
        # 基本指标
        length_score = min(len(text_content) / 500, 1.0)  # 长度评分
        
        # 中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text_content))
        chinese_ratio = chinese_chars / len(text_content) if text_content else 0
        
        # 英文字符比例
        english_chars = len(re.findall(r'[a-zA-Z]', text_content))
        english_ratio = english_chars / len(text_content) if text_content else 0
        
        # 数字比例
        digit_ratio = len(re.findall(r'\d', text_content)) / len(text_content) if text_content else 0
        
        # 常见简历关键词
        resume_keywords = [
            '工作经验', '教育背景', '项目经历', '技能', '联系方式',
            '姓名', '年龄', '性别', '学历', '专业', '公司', '职位',
            'experience', 'education', 'skills', 'project', 'contact'
        ]
        
        keyword_count = sum(1 for keyword in resume_keywords if keyword in text_content.lower())
        keyword_score = min(keyword_count / 5, 1.0)
        
        # 综合评分
        quality_score = (
            length_score * 0.3 +
            min(chinese_ratio + english_ratio, 1.0) * 0.3 +
            keyword_score * 0.4
        )
        
        return quality_score
    
    @staticmethod
    def _get_processing_recommendation(pdf_type):
        """
        获取处理建议
        
        Args:
            pdf_type (str): PDF类型
            
        Returns:
            str: 处理建议
        """
        recommendations = {
            'text': 'recommend_text_extraction',
            'mixed': 'recommend_hybrid_processing',
            'image': 'recommend_ocr_processing',
            'unknown': 'recommend_fallback_processing'
        }
        return recommendations.get(pdf_type, 'recommend_fallback_processing')
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """
        从PDF文件中提取文本
        
        Args:
            file_path (str): PDF文件路径
            
        Returns:
            str: 提取的文本内容
        """
        try:
            text_content = ""
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- 第{page_num + 1}页 ---\n"
                            text_content += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"提取第{page_num + 1}页文本失败: {e}")
                        continue
            
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            raise Exception(f"PDF文本提取失败: {str(e)}")
    
    @staticmethod
    def convert_pdf_to_images(file_path, dpi=200, max_pages=5):
        """
        将PDF转换为图片（用于OCR）
        
        Args:
            file_path (str): PDF文件路径
            dpi (int): 图片分辨率
            max_pages (int): 最大处理页数
            
        Returns:
            list: base64编码的图片列表
        """
        try:
            # 转换PDF为图片
            images = convert_from_path(
                file_path, 
                dpi=dpi,
                first_page=1,
                last_page=min(max_pages, 10)  # 限制最大页数
            )
            
            base64_images = []
            
            for i, image in enumerate(images):
                try:
                    # 压缩图片以减少API调用大小
                    image = image.convert('RGB')
                    
                    # 调整图片大小（如果太大）
                    max_size = 1920
                    if image.width > max_size or image.height > max_size:
                        ratio = min(max_size / image.width, max_size / image.height)
                        new_size = (int(image.width * ratio), int(image.height * ratio))
                        image = image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # 转换为base64
                    buffer = BytesIO()
                    image.save(buffer, format='JPEG', quality=85)
                    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    base64_images.append({
                        'page': i + 1,
                        'image': img_base64,
                        'format': 'jpeg'
                    })
                    
                except Exception as e:
                    logger.warning(f"处理第{i + 1}页图片失败: {e}")
                    continue
            
            return base64_images
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {e}")
            raise Exception(f"PDF转图片失败: {str(e)}")
    
    @staticmethod
    def intelligent_extract_text(file_path):
        """
        智能文本提取（根据PDF类型选择最佳方法）
        
        Args:
            file_path (str): PDF文件路径
            
        Returns:
            dict: 提取结果
        """
        try:
            # 1. 分析PDF类型
            analysis_result = PDFProcessor.analyze_pdf_type(file_path)
            
            if not analysis_result['success']:
                return analysis_result
            
            pdf_type = analysis_result['pdf_type']
            
            # 2. 根据类型选择处理方式
            if pdf_type == 'text':
                # 文字型PDF：直接提取文本
                logger.info(f"检测到文字型PDF，使用直接文本提取")
                text_content = PDFProcessor.extract_text_from_pdf(file_path)
                
                return {
                    'success': True,
                    'method': 'text_extraction',
                    'pdf_type': pdf_type,
                    'text_content': text_content,
                    'confidence': analysis_result['text_quality']
                }
                
            elif pdf_type == 'image':
                # 图片型PDF：使用OCR
                logger.info(f"检测到图片型PDF，准备使用OCR识别")
                images = PDFProcessor.convert_pdf_to_images(file_path)
                
                return {
                    'success': True,
                    'method': 'ocr_required',
                    'pdf_type': pdf_type,
                    'images': images,
                    'confidence': 0.8  # OCR处理的默认置信度
                }
                
            else:  # mixed or unknown
                # 混合型PDF：尝试文本提取，如果质量不好则使用OCR
                logger.info(f"检测到混合型PDF，使用混合处理方式")
                text_content = PDFProcessor.extract_text_from_pdf(file_path)
                
                if analysis_result['text_quality'] >= 0.5:
                    return {
                        'success': True,
                        'method': 'text_extraction',
                        'pdf_type': pdf_type,
                        'text_content': text_content,
                        'confidence': analysis_result['text_quality']
                    }
                else:
                    images = PDFProcessor.convert_pdf_to_images(file_path)
                    return {
                        'success': True,
                        'method': 'ocr_required',
                        'pdf_type': pdf_type,
                        'images': images,
                        'fallback_text': text_content,
                        'confidence': 0.7
                    }
                    
        except Exception as e:
            logger.error(f"智能文本提取失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'failed'
            }
    
    @staticmethod
    def get_pdf_info(file_path):
        """
        获取PDF基本信息
        
        Args:
            file_path (str): PDF文件路径
            
        Returns:
            dict: PDF信息
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                return {
                    'pages': len(pdf.pages),
                    'metadata': pdf.metadata or {},
                    'file_size': os.path.getsize(file_path)
                }
        except Exception as e:
            logger.error(f"获取PDF信息失败: {e}")
            return {
                'pages': 0,
                'metadata': {},
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
    
    @staticmethod
    def validate_pdf_file(file_path):
        """
        验证PDF文件
        
        Args:
            file_path (str): PDF文件路径
            
        Returns:
            dict: 验证结果
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': '文件不存在'}
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {'success': False, 'error': '文件为空'}
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                return {'success': False, 'error': '文件过大'}
            
            # 尝试打开PDF
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    return {'success': False, 'error': 'PDF没有页面'}
                
                if len(pdf.pages) > 20:  # 限制页数
                    return {'success': False, 'error': 'PDF页数过多'}
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"PDF验证失败: {e}")
            return {'success': False, 'error': f'PDF格式错误: {str(e)}'} 