from .base import Settings

class ProdSettings(Settings):
    # 生产环境特定配置
    DEBUG: bool = False
    
    # MinIO生产环境配置
    MINIO_SECURE: bool = True 