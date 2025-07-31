#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON结构转换、文本清洗工具
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from loguru import logger
import html
import unicodedata

class JSONParser:
    """JSON数据解析器"""
    
    @staticmethod
    def safe_parse(data: Union[str, bytes]) -> Optional[Dict[str, Any]]:
        """安全解析JSON数据"""
        if not data:
            return None
        
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            if data.startswith('\ufeff'):
                data = data[1:]
            
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"数据解析错误: {e}")
            return None
    
    @staticmethod
    def safe_dumps(data: Any, ensure_ascii: bool = False, indent: int = None) -> str:
        """安全序列化JSON数据"""
        try:
            return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent, default=str)
        except Exception as e:
            logger.error(f"JSON序列化失败: {e}")
            return "{}"

class TextCleaner:
    """文本清洗工具"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """基础文本清洗"""
        if not text:
            return ""
        
        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text)
        text = unicodedata.normalize('NFKC', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def clean_resume_text(text: str) -> str:
        """简历文本清洗"""
        if not text:
            return ""
        
        text = TextCleaner.clean_text(text)
        
        patterns_to_remove = [
            r'第\s*\d+\s*页',
            r'Page\s*\d+',
            r'共\s*\d+\s*页',
            r'简历\s*$',
            r'Resume\s*$',
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """提取联系信息"""
        contact_info = {}
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        phone_patterns = [
            r'1[3-9]\d{9}',
            r'(\d{3})-(\d{4})-(\d{4})',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                if isinstance(phones[0], tuple):
                    contact_info['phone'] = ''.join(phones[0])
                else:
                    contact_info['phone'] = phones[0]
                break
        
        return contact_info 