import os
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
from PIL import Image
import pdf2image
from utils.logger import ocr_logger
import torch
import tempfile

class OCRHelper:
    _det_model = None
    _det_processor = None
    _rec_model = None
    _rec_processor = None
    
    @classmethod
    def _initialize_models(cls):
        """初始化OCR模型"""
        try:
            if cls._det_model is None:
                ocr_logger.info("Initializing detection model...")
                cls._det_processor = load_det_processor()
                cls._det_model = load_det_model()
                
                # 设置检测器批处理大小
                detector_batch_size = int(os.getenv('DETECTOR_BATCH_SIZE', '6'))
                ocr_logger.info(f"Detection batch size: {detector_batch_size}")

            if cls._rec_model is None:
                ocr_logger.info("Initializing recognition model...")
                cls._rec_model = load_rec_model()
                cls._rec_processor = load_rec_processor()
                
                # 设置识别器批处理大小
                recognition_batch_size = int(os.getenv('RECOGNITION_BATCH_SIZE', '32'))
                ocr_logger.info(f"Recognition batch size: {recognition_batch_size}")
                
        except Exception as e:
            ocr_logger.error(f"Model initialization failed: {str(e)}")
            raise

    @classmethod
    def pdf_to_markdown(cls, pdf_path: str) -> str:
        """
        将PDF文件转换为Markdown格式
        """
        try:
            # 初始化模型
            cls._initialize_models()
            
            ocr_logger.info(f"Processing PDF file: {pdf_path}")
            
            # 将PDF转换为图像
            ocr_logger.info("Converting PDF to images...")
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=300,
                fmt='jpeg'
            )
            ocr_logger.info(f"Converted PDF to {len(images)} images")
            
            # 设置语言（支持中英文）
            langs = [["zh", "en"]] * len(images)
            
            # 运行OCR
            ocr_logger.info("Starting OCR processing...")
            predictions = run_ocr(
                images, 
                langs, 
                cls._det_model, 
                cls._det_processor, 
                cls._rec_model, 
                cls._rec_processor
            )
            
            # 转换为Markdown格式
            markdown_text = ""
            
            # 处理每一页
            for page_num, page_result in enumerate(predictions, 1):
                markdown_text += f"## Page {page_num}\n\n"
                
                # 按照y坐标排序文本行
                text_lines = sorted(page_result.text_lines, 
                                key=lambda x: x.bbox[1])  # 使用bbox的y坐标排序
                
                current_y = None
                line_buffer = []
                
                for line in text_lines:
                    text = line.text.strip()
                    confidence = line.confidence
                    
                    if not text:
                        continue
                        
                    # 获取当前行的y坐标
                    y_coord = line.bbox[1]  # bbox格式: [x1, y1, x2, y2]
                    
                    # 如果是新的y坐标（新的一行），处理缓冲区中的文本
                    if current_y is not None and abs(y_coord - current_y) > 10:
                        markdown_text += " ".join(line_buffer) + "\n\n"
                        line_buffer = []
                    
                    # 如果置信度较高，直接添加文本
                    # 如果置信度较低，添加标记
                    if confidence > 0.9:
                        line_buffer.append(text)
                    else:
                        line_buffer.append(f"{text}[?]")
                    
                    current_y = y_coord
                
                # 处理最后一行
                if line_buffer:
                    markdown_text += " ".join(line_buffer) + "\n\n"
                
                ocr_logger.debug(f"Processed page {page_num} with {len(text_lines)} text lines")
            
            ocr_logger.info("PDF to Markdown conversion completed successfully")
            return markdown_text.strip()
            
        except Exception as e:
            ocr_logger.error(f"PDF to Markdown conversion failed: {str(e)}")
            raise

    @classmethod
    def cleanup(cls):
        """清理模型和缓存"""
        try:
            cls._det_model = None
            cls._det_processor = None
            cls._rec_model = None
            cls._rec_processor = None
            torch.cuda.empty_cache()  # 如果使用GPU，清理显存
            ocr_logger.info("Model cleanup completed")
        except Exception as e:
            ocr_logger.warning(f"Model cleanup failed: {str(e)}")