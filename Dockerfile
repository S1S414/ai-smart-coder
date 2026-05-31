FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有文件
COPY . .

# 确保 static 目录存在
RUN mkdir -p static

# HF Spaces 默认端口 7860
EXPOSE 7860

# gunicorn 生产模式启动
CMD sh -c "gunicorn --bind 0.0.0.0:${PORT:-7860} --workers 1 --timeout 300 app:app"
