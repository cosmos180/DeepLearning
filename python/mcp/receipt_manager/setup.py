"""
采购收据管理工具 - 安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="receipt-manager",
    version="1.0.0",
    description="智能采购收据管理工具 - 使用AI识别收据并保存到Excel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="bughero",
    author_email="bughero2012@gmail.com",
    url="https://github.com/bughero/DeepLearning",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "openpyxl>=3.1.0",
        "volcenginesdkarkruntime>=0.1.0",
        "loguru>=0.7.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "mypy>=1.5.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
            "Pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "receipt-manager=receipt_manager.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="receipt excel ai ocr purchase management",
)
