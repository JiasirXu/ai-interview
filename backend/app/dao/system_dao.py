#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统数据访问对象
"""

from typing import Optional, List, Dict, Any
from app.models import db
from app.models.system import SystemConfig
from loguru import logger


class SystemDAO:
    """系统数据访问对象"""
    
    @staticmethod
    def create_system_config(user_id: int, config_type: str, config_data: Dict[str, Any]) -> Optional[SystemConfig]:
        """创建系统配置"""
        try:
            config = SystemConfig(
                user_id=user_id,
                config_type=config_type,
                config_data=config_data
            )
            db.session.add(config)
            db.session.commit()
            return config
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建系统配置失败: {e}")
            return None
    
    @staticmethod
    def get_system_config_by_id(config_id: int) -> Optional[SystemConfig]:
        """根据ID获取系统配置"""
        return SystemConfig.query.get(config_id)
    
    @staticmethod
    def get_system_config_by_user_and_type(user_id: int, config_type: str) -> Optional[SystemConfig]:
        """根据用户ID和配置类型获取系统配置"""
        return SystemConfig.query.filter_by(user_id=user_id, config_type=config_type).first()
    
    @staticmethod
    def get_user_system_configs(user_id: int) -> List[SystemConfig]:
        """获取用户的所有系统配置"""
        return SystemConfig.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def update_system_config(config_id: int, config_data: Dict[str, Any]) -> bool:
        """更新系统配置"""
        try:
            config = SystemDAO.get_system_config_by_id(config_id)
            if not config:
                return False
            
            config.config_data = config_data
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新系统配置失败: {e}")
            return False
    
    @staticmethod
    def update_or_create_system_config(user_id: int, config_type: str, config_data: Dict[str, Any]) -> Optional[SystemConfig]:
        """更新或创建系统配置"""
        try:
            config = SystemDAO.get_system_config_by_user_and_type(user_id, config_type)
            if config:
                # 更新现有配置
                config.config_data = config_data
                db.session.commit()
                return config
            else:
                # 创建新配置
                return SystemDAO.create_system_config(user_id, config_type, config_data)
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新或创建系统配置失败: {e}")
            return None
    
    @staticmethod
    def delete_system_config(config_id: int) -> bool:
        """删除系统配置"""
        try:
            config = SystemDAO.get_system_config_by_id(config_id)
            if not config:
                return False
            
            db.session.delete(config)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"删除系统配置失败: {e}")
            return False
    
    @staticmethod
    def get_global_system_configs() -> List[SystemConfig]:
        """获取全局系统配置（user_id为None的配置）"""
        return SystemConfig.query.filter_by(user_id=None).all()
    
    @staticmethod
    def get_global_system_config_by_type(config_type: str) -> Optional[SystemConfig]:
        """根据配置类型获取全局系统配置"""
        return SystemConfig.query.filter_by(user_id=None, config_type=config_type).first()
    
    @staticmethod
    def create_global_system_config(config_type: str, config_data: Dict[str, Any]) -> Optional[SystemConfig]:
        """创建全局系统配置"""
        try:
            config = SystemConfig(
                user_id=None,  # 全局配置
                config_type=config_type,
                config_data=config_data
            )
            db.session.add(config)
            db.session.commit()
            return config
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建全局系统配置失败: {e}")
            return None
    
    @staticmethod
    def update_global_system_config(config_type: str, config_data: Dict[str, Any]) -> bool:
        """更新全局系统配置"""
        try:
            config = SystemDAO.get_global_system_config_by_type(config_type)
            if not config:
                return False
            
            config.config_data = config_data
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新全局系统配置失败: {e}")
            return False
    
    @staticmethod
    def get_system_config_count_by_user(user_id: int) -> int:
        """获取用户的系统配置数量"""
        return SystemConfig.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_all_system_configs() -> List[SystemConfig]:
        """获取所有系统配置"""
        return SystemConfig.query.all() 