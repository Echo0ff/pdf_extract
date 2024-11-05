from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from minio import Minio
import os
import uuid
from utils.ocr_helper import OCRHelper
from utils.pdf_helper import PDFHelper
import tempfile
from typing import Optional
from functools import lru_cache
from config.base import Settings
from config.development import DevSettings
from config.production import ProdSettings
from utils.logger import app_logger, ocr_logger, error_logger

def get_settings():
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProdSettings()
    return DevSettings()

settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME)

# MinIO配置
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

# 确保bucket存在
if not minio_client.bucket_exists(settings.MINIO_BUCKET):
    minio_client.make_bucket(settings.MINIO_BUCKET)
    app_logger.info(f"Created new bucket: {settings.MINIO_BUCKET}")

@app.post(f"{settings.API_V1_STR}/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        app_logger.warning("No file selected")
        raise HTTPException(status_code=400, detail="没有选择文件")
    
    if not file.filename.lower().endswith('.pdf'):
        app_logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="只支持PDF文件")

    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = file.filename
        # 修改：直接使用完整路径作为对象名
        file_path = f"{file_id}.pdf"  # 简化文件路径
        
        app_logger.info(f"Starting upload for file: {filename} with ID: {file_id}")

        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        # 使用BytesIO来处理文件内容
        from io import BytesIO
        file_data = BytesIO(file_content)
        
        # 上传到MinIO
        minio_client.put_object(
            settings.MINIO_BUCKET,
            file_path,
            file_data,
            file_size,
            'application/pdf'
        )
        
        app_logger.info(f"Successfully uploaded file to MinIO: {file_path}")

        return JSONResponse({
            'code': 200,
            'message': '上传成功',
            'data': {
                'file_id': file_id,
                'file_name': filename
            }
        })

    except Exception as e:
        error_msg = f"Upload failed for file {file.filename}: {str(e)}"
        error_logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
    finally:
        await file.close()

@app.get(f"{settings.API_V1_STR}/convert/{{file_id}}")
async def convert_to_markdown(file_id: str):
    try:
        app_logger.info(f"Starting conversion for file_id: {file_id}")
        
        # 修改：直接构造文件路径
        file_path = f"{file_id}.pdf"
        
        # 检查文件是否存在
        try:
            minio_client.stat_object(settings.MINIO_BUCKET, file_path)
        except Exception as e:
            app_logger.error(f"File not found in MinIO: {file_path}")
            raise HTTPException(status_code=404, detail="文件不存在")
        
        app_logger.info(f"Found PDF file in MinIO: {file_path}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            try:
                # 下载文件
                minio_client.fget_object(
                    settings.MINIO_BUCKET, 
                    file_path,
                    temp_file.name
                )
                app_logger.info(f"Downloaded file to temporary location: {temp_file.name}")
                
                # 使用OCRHelper处理PDF
                ocr_logger.info(f"Starting OCR processing for file: {file_path}")
                markdown_text, metadata = PDFHelper.pdf_to_markdown(temp_file.name)
                ocr_logger.info(f"OCR processing completed successfully")
                
                return JSONResponse({
                    'code': 200,
                    'message': '转换成功',
                    'data': {
                        "markdown": markdown_text,
                        "metadata": metadata
                    }
                })
            
            except Exception as e:
                error_msg = f"Processing failed: {str(e)}"
                error_logger.error(error_msg, exc_info=True)
                raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
            finally:
                # 删除临时文件
                try:
                    os.unlink(temp_file.name)
                    app_logger.info(f"Cleaned up temporary file: {temp_file.name}")
                except Exception as e:
                    error_logger.warning(f"Failed to clean up temporary file: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Conversion failed for file_id {file_id}: {str(e)}"
        error_logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

# 添加启动和关闭事件处理
@app.on_event("startup")
async def startup_event():
    app_logger.info("Application starting up...")
    app_logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    app_logger.info(f"MinIO endpoint: {settings.MINIO_ENDPOINT}")

@app.on_event("shutdown")
async def shutdown_event():
    app_logger.info("Application shutting down...") 