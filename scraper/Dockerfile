# 1. 使用 Playwright 官方提供的、包含所有浏览器和依赖的镜像作为基础
# 我们选择一个基于 Python 的版本以简化操作
FROM mcr.microsoft.com/playwright/python:v1.44.1-jammy

# 2. 设置工作目录
# 之后的所有命令都会在这个目录中执行
WORKDIR /app

# 3. 复制依赖文件
# 将 requirements.txt 文件复制到工作目录中
COPY requirements.txt.

# 4. 安装 Python 依赖
# 在容器内运行 pip 来安装我们脚本所需的库
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制我们的 Python 脚本
# 将抓取脚本复制到工作目录中
COPY scrape.py.

# 6. 设置默认命令
# 当容器启动时，默认执行此命令
# 注意：我们不再需要在构建命令中运行 "playwright install"，因为浏览器已经包含在基础镜像里了
CMD ["python", "scrape.py"]
