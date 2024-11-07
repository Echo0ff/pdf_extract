# FROM python:3.10-slim

# WORKDIR /app

# # 安装系统依赖
# RUN apt-get update && apt-get install -y \
#     poppler-utils \
#     build-essential \
#     libgl1-mesa-glx \
#     libglib2.0-0 \
#     libsm6 \
#     libxext6 \
#     libxrender-dev \
#     && rm -rf /var/lib/apt/lists/*

# # 配置pip使用清华源，并升级pip
# RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U && \
#     pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# # 分层安装依赖
# COPY requirements.txt .

# # 先安装torch和其他基础依赖
# RUN pip install --no-cache-dir \
#     torch>=2.1.2 \
#     transformers>=4.36.2 \
#     pillow>=10.2.0 \
#     opencv-python>=4.9.0.80 \
#     tabulate>=0.9.0

# # 然后安装surya-ocr和其他应用依赖
# RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# COPY . .

# # 使用环境变量来控制运行环境
# ENV ENV=development
# ENV RECOGNITION_STATIC_CACHE=true
# ENV RECOGNITION_BATCH_SIZE=32
# ENV DETECTOR_BATCH_SIZE=6

# # 预创建模型缓存目录
# RUN mkdir -p /root/.cache/huggingface/hub

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

# 使用Python 3.10基础镜像
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 预创建模型缓存目录
RUN mkdir -p /root/.cache/huggingface/hub

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]