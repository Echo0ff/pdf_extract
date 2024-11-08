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