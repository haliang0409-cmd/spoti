# 1. 使用 Playwright 官方提供的、包含所有浏览器和依赖的镜像作为基础
# 将镜像标签更新为一个已知的稳定版本，以解决 "not found" 错误。
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 2. 设置工作目录
# 之后的所有命令都会在这个目录中执行
WORKDIR /app

# 3. 更新包列表并安装 Git
# 基础镜像不包含 git，而我们的脚本需要用它来推送更新，所以在此处安装。
RUN apt-get update && apt-get install -y git --no-install-recommends && rm -rf /var/lib/apt/lists/*

# 4. 复制依赖文件
# 将 requirements.txt 文件复制到工作目录中。
COPY requirements.txt .

# 5. 安装 Python 依赖
# 在容器内运行 pip 来安装我们脚本所需的库。
# --no-cache-dir 选项可以减小最终镜像的大小。
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制我们的 Python 脚本
# 将抓取脚本复制到工作目录中。
COPY scrape.py .

# 7. 设置默认命令
# 当容器启动时，默认执行此命令。
CMD ["python", "scrape.py"]
