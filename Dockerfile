# ✅ 使用可用的 CPU 基础镜像
FROM cnstark/pytorch:2.1.2-py3.10.15-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装 git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 拷贝项目代码
COPY . .

# 安装依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 监听端口
EXPOSE 8000

# 使用 gunicorn 启动 Flask（标准做法）
CMD ["python", "app.py"]

