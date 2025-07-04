# 使用 Python 3.10 的轻量镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 拷贝代码到容器中
COPY . .

# 安装依赖
RUN pip install --upgrade pip \
    && pip install setuptools wheel \
    && pip install -r requirements.txt

# Flask 默认端口
EXPOSE 8000

# 启动 Flask 应用
CMD ["python", "app.py"]
