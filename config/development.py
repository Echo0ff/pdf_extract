from .base import Settings

class DevSettings(Settings):
    # 开发环境特定配置
    DEBUG: bool = True
    
    # MinIO开发环境配置
    MINIO_ENDPOINT: str = "localhost:9000" 