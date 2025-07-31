#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置ORM模型
"""

from datetime import datetime
from . import db

class SystemConfig(db.Model):
    """系统配置表"""
    
    __tablename__ = 'system_config'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text, nullable=True)
    config_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    description = db.Column(db.Text, nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(config_key=key).first()
        if not config:
            return default
        
        # 根据类型转换值
        if config.config_type == 'integer':
            try:
                return int(config.config_value)
            except (ValueError, TypeError):
                return default
        elif config.config_type == 'float':
            try:
                return float(config.config_value)
            except (ValueError, TypeError):
                return default
        elif config.config_type == 'boolean':
            return config.config_value.lower() in ('true', '1', 'yes', 'on')
        elif config.config_type == 'json':
            try:
                import json
                return json.loads(config.config_value)
            except (ValueError, TypeError):
                return default
        else:
            return config.config_value
    
    @classmethod
    def set_config(cls, key, value, config_type='string', description=None):
        """设置配置值"""
        config = cls.query.filter_by(config_key=key).first()
        
        # 转换值为字符串存储
        if config_type == 'json':
            import json
            str_value = json.dumps(value, ensure_ascii=False)
        else:
            str_value = str(value)
        
        if config:
            config.config_value = str_value
            config.config_type = config_type
            if description:
                config.description = description
            config.updated_at = datetime.utcnow()
        else:
            config = cls(
                config_key=key,
                config_value=str_value,
                config_type=config_type,
                description=description
            )
            db.session.add(config)
        
        db.session.commit()
        return config
    
    @classmethod
    def get_all_configs(cls):
        """获取所有配置"""
        configs = cls.query.all()
        result = {}
        for config in configs:
            result[config.config_key] = cls.get_config(config.config_key)
        return result
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.get_config(self.config_key),
            'config_type': self.config_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'
