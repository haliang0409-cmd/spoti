# 1. 使用 Playwright 官方提供的、包含所有浏览器和依赖的镜像作为基础
# 这个镜像是专门为在无头环境中运行 Playwright 设计的，避免了手动安装浏览器的各种问题。
FROM mcr.microsoft.com/playwright/python:v1.44.1-jammy

# 2. 设置工作目录
# 之后的所有命令都会在这个目录中执行
WORKDIR /app

# 3. 复制依赖文件
# 将 requirements.txt 文件复制到工作目录中。
# 注意：'requirements.txt' 和 '.' 之间有一个空格，这是正确的语法。
COPY requirements.txt .

# 4. 安装 Python 依赖
# 在容器内运行 pip 来安装我们脚本所需的库。
# --no-cache-dir 选项可以减小最终镜像的大小。
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制我们的 Python 脚本
# 将抓取脚本复制到工作目录中。
# 注意：'scrape.py' 和 '.' 之间有一个空格。
COPY scrape.py .

# 6. 设置默认命令
# 当容器启动时，默认执行此命令。
# 因为基础镜像已经包含了浏览器，我们不需要再运行 "playwright install"。
CMD ["python", "scrape.py"]
