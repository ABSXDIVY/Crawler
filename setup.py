#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDRC政策文件爬虫系统 - 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# 读取requirements文件
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='ndrc-crawler',
    version='1.0.0',
    author='NDRC Crawler Team',
    author_email='contact@example.com',
    description='国家发改委政策文件爬虫系统',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/ABSXDIVY/ndrc_crawler',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=3.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
        ],
        'async': [
            'aiohttp>=3.8.0',
            'asyncio-throttle>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ndrc-crawler=ndrc_crawler:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='crawler, spider, policy, ndrc, government, data-extraction',
    project_urls={
        'Bug Reports': 'https://github.com/ABSXDIVY/ndrc_crawler/issues',
        'Source': 'https://github.com/ABSXDIVY/ndrc_crawler',
        'Documentation': 'https://github.com/ABSXDIVY/ndrc_crawler/blob/main/README.md',
    },
)
