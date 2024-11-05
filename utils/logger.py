import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

# 创建logs目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 日志格式
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """设置日志记录器"""
    handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    handler.setFormatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

# 创建应用日志记录器
app_logger = setup_logger('app', 'app.log')
# 创建OCR日志记录器
ocr_logger = setup_logger('ocr', 'ocr.log')
# 创建PDF日志记录器
pdf_logger = setup_logger('pdf', 'pdf.log')
# 创建错误日志记录器
error_logger = setup_logger('error', 'error.log', level=logging.ERROR) 