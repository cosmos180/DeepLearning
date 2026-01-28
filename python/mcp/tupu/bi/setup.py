from setuptools import setup, find_packages

setup(
    name="tupu-bi-mcp-server",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tupu-bi-mcp-server=tupu_bi.server:main",
        ],
    },
    python_requires=">=3.8",
)
