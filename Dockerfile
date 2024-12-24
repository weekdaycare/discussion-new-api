# 使用官方 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录
COPY . .

# 安装所需的 Python 包
RUN pip install requests

# 运行主程序
CMD ["python", "main.py"]
