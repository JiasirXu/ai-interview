import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量文件
load_dotenv()

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:050217xj@localhost:3306/softwarecup'  # 使用MySQL数据库
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # 延长到24小时
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}
    
    # CORS配置
    CORS_ORIGINS = ["http://localhost:8080", "http://127.0.0.1:8080"]
    CORS_ALLOW_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Disposition']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Request-Time']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # 讯飞AI统一配置
    XUNFEI_CONFIG = {
        # 通用认证信息 - 除虚拟人外的所有服务使用 014f8018
        'APPID': os.getenv('XUNFEI_APP_ID', '014f8018'),
        'APISecret': os.getenv('XUNFEI_API_SECRET', 'ODQ4NTRlOGRkOGM2Y2NmMWRkN2FmZWFi'),
        'APIKey': os.getenv('XUNFEI_API_KEY', 'a444fdfbce20c52641ce2b3167957e6d'),
        
        # 1. 讯飞星火认知大模型Spark X1
        'SPARK': {
            'HTTP_URL': 'https://spark-api-open.xf-yun.com/v2/chat/completions',
            'HTTP_PASSWORD': 'VIjIbupkaPneUsEgXtjP:NKnrGmMQPuYraTmzKbPy',
            'WEBSOCKET_URL': 'wss://spark-api.xf-yun.com/v1/x1',
            'SERVICE_NAME': 'Spark X1'
        },
        
        # 2. 通用文档识别WebAPI
        'OCR': {
            'URL': 'https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm',
            'SERVICE_NAME': '通用文档识别'
        },
        
        # 3. 实时语音转写WebSocket
        'AUDIO': {
            'WEBSOCKET_URL': 'wss://rtasr.xfyun.cn/v1/ws',  # 使用wss协议
            'SERVICE_NAME': '实时语音转写',
            'APPID': '014f8018',  # 实时语音转写专用APPID
            'APIKey': '8e15e12cec4d03e8dc7f1a46c6b7b847'  # 实时语音转写专用APIKey
        },
        
        # 4. 人脸检测和属性分析
        'FACE': {
            'DETECTION_URL': 'https://api.xf-yun.com/v1/private/s67c9c78c',
            'EXPRESSION_URL': 'http://tupapi.xfyun.cn/v1/expression',
            'SERVICE_NAME': '人脸检测和表情分析'
        },
        
        # 5. 虚拟人交互接口
        'AVATAR': {
            'APPID': 'e98176f0',  # 虚拟人专用APPID
            'APIKey': '03fd89ab9e928314118bf9724a990762',  # 虚拟人专用APIKey
            'APISecret': 'ZWE0M2M0ZjcwYzQwMDUwNzczOWI3ODEx',  # 虚拟人专用APISecret
            'SERVICE_ID': '198329296530575360',
            'SERVICE_URL': 'https://virtual-man.xfyun.cn/console/api/e98176f0/198329296530575360',
            'SERVICE_NAME': '虚拟人交互'
        }
    }
    
    # 调试模式
    DEBUG = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:050217xj@localhost:3306/softwarecup'  # 可以使用同一个数据库

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 