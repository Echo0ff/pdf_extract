from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API配置
    DEBUG: bool = False
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "PDF处理服务"
    
    # 服务配置
    PORT: int = 5000
    HOST: str = "0.0.0.0"
    WORKERS: Optional[int] = None
    
    # MinIO配置
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    MINIO_SECURE: bool = False
    
    # SSL配置
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    DOMAIN_NAME: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env.dev"  # 默认使用开发环境配置