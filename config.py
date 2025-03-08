import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    
    # MySQL数据库配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('MYSQL_USER')}:{os.environ.get('MYSQL_PASSWORD')}@{os.environ.get('MYSQL_HOST')}/{os.environ.get('MYSQL_DATABASE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Session配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 静态文件配置
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates' 