# 使用Python 3.7官方镜像
FROM python:3.7-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p reports/logs reports/screenshots

# 设置环境变量
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# 创建启动脚本
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1024x768x16 &\n\
sleep 2\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 设置入口点
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认命令（运行API测试）
CMD ["python", "-m", "pytest", "tests/API/test_entrance.py", "-v"]