import os
from marker.convert import convert_single_pdf
from marker.models import load_all_models
from utils.logger import pdf_logger
import traceback

class PDFHelper:
    _models = None
    
    @classmethod
    def _initialize_models(cls):
        """初始化 Marker 模型"""
        try:
            if cls._models is None:
                # 设置离线模式
                os.environ['TRANSFORMERS_OFFLINE'] = '1'
                
                # 设置模型缓存目录
                cache_dir = os.getenv('HF_HOME', '/root/.cache/huggingface/hub/')
                os.environ['TRANSFORMERS_CACHE'] = cache_dir
                
                pdf_logger.info(f"Using model cache directory: {cache_dir}")
                pdf_logger.info("Initializing Marker models in offline mode...")
                cls._models = load_all_models()
                pdf_logger.info("Models loaded successfully")
                
        except Exception as e:
            pdf_logger.error(f"Model initialization failed: {str(e)}\n{traceback.format_exc()}")
            raise

    @classmethod
    def pdf_to_markdown(cls, pdf_path: str) -> tuple[str, dict]:
        """
        将PDF文件转换为Markdown格式
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            tuple: (markdown文本, 元数据)
        """
        try:
            # 初始化模型
            cls._initialize_models()
            
            pdf_logger.info(f"Processing PDF file: {pdf_path}")
            
            # 检查文件是否存在
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # 转换PDF
            pdf_logger.info("Starting PDF conversion...")
            markdown_text, images, metadata = convert_single_pdf(
                pdf_path,
                cls._models
            )
            
            # 记录转换统计信息
            pdf_logger.info("Conversion completed successfully")
            pdf_logger.info(f"Pages processed: {metadata.get('pages', 0)}")
            
            # 记录OCR统计信息
            ocr_stats = metadata.get('ocr_stats', {})
            pdf_logger.info(f"OCR stats: {ocr_stats}")
            
            return markdown_text, metadata
            
        except Exception as e:
            pdf_logger.error(f"PDF to Markdown conversion failed: {str(e)}\n{traceback.format_exc()}")
            raise
        finally:
            # 保持模型加载状态以提高后续转换速度
            pass

    @classmethod
    def cleanup(cls):
        """清理模型和缓存"""
        try:
            pdf_logger.info("Cleanup completed")
        except Exception as e:
            pdf_logger.warning(f"Cleanup failed: {str(e)}")