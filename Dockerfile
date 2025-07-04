# 使用 Python 3.10 基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（添加 git）
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 拷贝代码
COPY . .

# 安装依赖
RUN pip install --upgrade pip \
    && pip install setuptools wheel \
    && pip install -r requirements.txt

# Flask 默认端口
EXPOSE 8000

# 启动 Flask 应用
CMD ["python", "app.py"]

