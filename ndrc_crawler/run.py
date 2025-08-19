#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDRC政策文件爬虫系统 - 快速启动脚本
一键运行完整的爬取、提取和处理流程
"""

import os
import sys
import logging
from datetime import datetime
import subprocess
import time

def setup_logging():
    """设置日志配置"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_command(command, description, logger):
    """运行命令并记录日志"""
    logger.info(f"开始执行: {description}")
    logger.info(f"命令: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        end_time = time.time()
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 执行成功 (耗时: {end_time - start_time:.2f}秒)")
            if result.stdout:
                logger.debug(f"输出: {result.stdout}")
        else:
            logger.error(f"❌ {description} 执行失败")
            logger.error(f"错误信息: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {description} 执行异常: {e}")
        return False
    
    return True

def check_dependencies():
    """检查依赖包是否安装"""
    required_packages = [
        'requests',
        'beautifulsoup4', 
        'pandas',
        'openpyxl',
        'urllib3'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 NDRC政策文件爬虫系统 - 快速启动")
    print("=" * 50)
    
    # 设置日志
    logger = setup_logging()
    
    # 检查依赖
    print("📋 检查依赖包...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ 依赖包检查通过")
    
    # 创建必要目录
    print("📁 创建必要目录...")
    for directory in ['results', 'logs', 'full_data']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
    
    # 执行流程
    steps = [
        {
            'command': 'python ndrc_crawler.py',
            'description': '爬取发改委政策文件'
        },
        {
            'command': 'python data_extractor_full.py',
            'description': '提取结构化数据'
        },
        {
            'command': 'python content_splitter.py',
            'description': '处理政策内容分段'
        },
        {
            'command': 'python attachment_splitter.py',
            'description': '处理附件信息拆解'
        }
    ]
    
    print("\n🔄 开始执行爬虫流程...")
    success_count = 0
    
    for i, step in enumerate(steps, 1):
        print(f"\n步骤 {i}/{len(steps)}: {step['description']}")
        if run_command(step['command'], step['description'], logger):
            success_count += 1
        else:
            print(f"⚠️  步骤 {i} 失败，是否继续? (y/n): ", end='')
            if input().lower() != 'y':
                break
    
    # 总结
    print("\n" + "=" * 50)
    print(f"📊 执行完成: {success_count}/{len(steps)} 个步骤成功")
    
    if success_count == len(steps):
        print("🎉 所有步骤执行成功！")
        print("\n📂 生成的文件:")
        for file in os.listdir('.'):
            if file.endswith('.xlsx'):
                print(f"  - {file}")
    else:
        print("⚠️  部分步骤失败，请检查日志文件获取详细信息")
    
    print(f"\n📝 详细日志请查看: logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

if __name__ == '__main__':
    main()
