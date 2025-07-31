#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统业务逻辑服务
"""

from typing import Optional, Dict, Any, Tuple, List
from app.dao.system_dao import SystemDAO
from app.dao.user_dao import UserDAO
from loguru import logger


class SystemService:
    """系统业务逻辑服务"""
    
    @staticmethod
    def get_user_system_configs(user_id: int) -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        获取用户系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置列表)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取用户配置
            configs = SystemDAO.get_user_system_configs(user_id)
            
            # 3. 构建响应数据
            config_list = []
            for config in configs:
                config_data = {
                    'id': config.id,
                    'config_type': config.config_type,
                    'config_data': config.config_data,
                    'created_at': config.created_at.isoformat() if config.created_at else None,
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                }
                config_list.append(config_data)
            
            return True, "获取成功", config_list
            
        except Exception as e:
            logger.error(f"获取用户系统配置失败: {e}")
            return False, "获取失败", None
    
    @staticmethod
    def get_system_config_by_type(user_id: int, config_type: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        根据类型获取系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取配置
            config = SystemDAO.get_system_config_by_user_and_type(user_id, config_type)
            if not config:
                return False, "配置不存在", None
            
            # 3. 构建响应数据
            config_data = {
                'id': config.id,
                'config_type': config.config_type,
                'config_data': config.config_data,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            }
            
            return True, "获取成功", config_data
            
        except Exception as e:
            logger.error(f"获取系统配置失败: {e}")
            return False, "获取失败", None
    
    @staticmethod
    def create_or_update_system_config(user_id: int, config_type: str, config_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        创建或更新系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 验证配置数据
            if not config_type:
                return False, "配置类型不能为空", None
            
            if not config_data:
                return False, "配置数据不能为空", None
            
            # 3. 创建或更新配置
            config = SystemDAO.update_or_create_system_config(user_id, config_type, config_data)
            if not config:
                return False, "创建或更新配置失败", None
            
            # 4. 构建响应数据
            response_data = {
                'id': config.id,
                'config_type': config.config_type,
                'config_data': config.config_data,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            }
            
            return True, "配置保存成功", response_data
            
        except Exception as e:
            logger.error(f"创建或更新系统配置失败: {e}")
            return False, "保存失败，请稍后重试", None
    
    @staticmethod
    def delete_system_config(user_id: int, config_id: int) -> Tuple[bool, str]:
        """
        删除系统配置业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在"
            
            # 2. 验证配置
            config = SystemDAO.get_system_config_by_id(config_id)
            if not config:
                return False, "配置不存在"
            
            # 3. 验证权限（只能删除自己的配置）
            if config.user_id != user_id:
                return False, "无权限删除此配置"
            
            # 4. 删除配置
            success = SystemDAO.delete_system_config(config_id)
            if not success:
                return False, "删除配置失败"
            
            return True, "删除成功"
            
        except Exception as e:
            logger.error(f"删除系统配置失败: {e}")
            return False, "删除失败，请稍后重试"
    
    @staticmethod
    def get_global_system_configs() -> Tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """
        获取全局系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置列表)
        """
        try:
            # 1. 获取全局配置
            configs = SystemDAO.get_global_system_configs()
            
            # 2. 构建响应数据
            config_list = []
            for config in configs:
                config_data = {
                    'id': config.id,
                    'config_type': config.config_type,
                    'config_data': config.config_data,
                    'created_at': config.created_at.isoformat() if config.created_at else None,
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                }
                config_list.append(config_data)
            
            return True, "获取成功", config_list
            
        except Exception as e:
            logger.error(f"获取全局系统配置失败: {e}")
            return False, "获取失败", None
    
    @staticmethod
    def get_global_system_config_by_type(config_type: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        根据类型获取全局系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置信息)
        """
        try:
            # 1. 获取配置
            config = SystemDAO.get_global_system_config_by_type(config_type)
            if not config:
                return False, "配置不存在", None
            
            # 2. 构建响应数据
            config_data = {
                'id': config.id,
                'config_type': config.config_type,
                'config_data': config.config_data,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            }
            
            return True, "获取成功", config_data
            
        except Exception as e:
            logger.error(f"获取全局系统配置失败: {e}")
            return False, "获取失败", None
    
    @staticmethod
    def create_global_system_config(config_type: str, config_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        创建全局系统配置业务逻辑
        
        Returns:
            (是否成功, 消息, 配置信息)
        """
        try:
            # 1. 验证配置数据
            if not config_type:
                return False, "配置类型不能为空", None
            
            if not config_data:
                return False, "配置数据不能为空", None
            
            # 2. 创建配置
            config = SystemDAO.create_global_system_config(config_type, config_data)
            if not config:
                return False, "创建全局配置失败", None
            
            # 3. 构建响应数据
            response_data = {
                'id': config.id,
                'config_type': config.config_type,
                'config_data': config.config_data,
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None
            }
            
            return True, "全局配置创建成功", response_data
            
        except Exception as e:
            logger.error(f"创建全局系统配置失败: {e}")
            return False, "创建失败，请稍后重试", None
    
    @staticmethod
    def update_global_system_config(config_type: str, config_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新全局系统配置业务逻辑
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证配置数据
            if not config_type:
                return False, "配置类型不能为空"
            
            if not config_data:
                return False, "配置数据不能为空"
            
            # 2. 更新配置
            success = SystemDAO.update_global_system_config(config_type, config_data)
            if not success:
                return False, "更新全局配置失败"
            
            return True, "全局配置更新成功"
            
        except Exception as e:
            logger.error(f"更新全局系统配置失败: {e}")
            return False, "更新失败，请稍后重试"
    
    @staticmethod
    def get_system_statistics(user_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        获取系统统计信息业务逻辑
        
        Returns:
            (是否成功, 消息, 统计信息)
        """
        try:
            # 1. 验证用户
            user = UserDAO.get_user_by_id(user_id)
            if not user:
                return False, "用户不存在", None
            
            # 2. 获取统计数据
            user_config_count = SystemDAO.get_system_config_count_by_user(user_id)
            global_config_count = len(SystemDAO.get_global_system_configs())
            total_config_count = len(SystemDAO.get_all_system_configs())
            
            statistics = {
                'user_config_count': user_config_count,
                'global_config_count': global_config_count,
                'total_config_count': total_config_count
            }
            
            return True, "获取成功", statistics
            
        except Exception as e:
            logger.error(f"获取系统统计信息失败: {e}")
            return False, "获取失败", None 