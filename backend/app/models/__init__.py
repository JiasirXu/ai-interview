#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORM模型模块
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

# 创建db对象
db = SQLAlchemy()
# 创建其他扩展实例
jwt = JWTManager()
migrate = Migrate()
cors = CORS()


from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview
from app.models.system import SystemConfig

__all__ = ['User', 'Resume', 'Interview', 'SystemConfig', 'db', 'jwt', 'migrate', 'cors']