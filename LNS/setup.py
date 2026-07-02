#!/usr/bin/env python3
"""
LNS — Life Navigation System
setup.py 兼容层（为旧版 pip 提供安装支持）
"""

from setuptools import setup, find_packages

setup(
    name="lns",
    version="1.0.0",
    description="Life Navigation System - 人生决策导航系统",
    packages=find_packages(),
    install_requires=[
        "lunar-python>=1.4,<2.0",
        "pytz",
        "python-dateutil",
        "pydantic>=1.0,<2.0",
    ],
    extras_require={
        "dev": ["pytest", "skyfield>=1.46"],
    },
    python_requires=">=3.6",
)
