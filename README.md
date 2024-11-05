# PDF处理服务

这是一个基于Flask的PDF处理服务，提供PDF文件上传和转换为Markdown格式的功能。

## 功能特性

1. PDF文件上传
   - 支持PDF文件的上传和存储
   - 使用MinIO作为对象存储后端
   - 支持大文件上传

2. PDF转Markdown
   - 使用SuryaOCR进行PDF文本识别
   - 将识别结果转换为Markdown格式
   - 支持中英文文本识别

## API接口说明

### 1. PDF上传接口

- 接口地址：`/api/upload`
- 请求方法：POST
- Content-Type: multipart/form-data
- 请求参数：
  - file: PDF文件（必须） 