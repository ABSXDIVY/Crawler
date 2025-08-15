#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家发改委政策文件爬虫
精简版本 - 直接保存页面源码到results目录
"""

import requests
import time
from datetime import datetime
import logging
import os
import urllib3
from bs4 import BeautifulSoup

# 导入配置
from config import POLICY_CATEGORIES, WEBSITE_CONFIG, CRAWL_CONFIG

# 设置日志
def setup_logging():
    """设置日志配置"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(f"logs/ndrc_crawler_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
        ]
    )
    logger = logging.getLogger(__name__)
    
    logger.info("发改委爬虫启动")
    return logger

logger = setup_logging()

class NDRCCrawler:
    """发改委爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.session.headers.update(WEBSITE_CONFIG['headers'])
        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 创建results目录
        if not os.path.exists('results'):
            os.makedirs('results')
        
    def get_page_content(self, url):
        """获取页面内容"""
        try:
            logger.info(f"访问: {url}")
            response = self.session.get(url, timeout=WEBSITE_CONFIG['timeout'])
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info(f"成功: {response.status_code}")
            return response.text
        except Exception as e:
            logger.error(f"失败: {e}")
            return None
    
    def has_next_page(self, html_content):
        """检查是否有下一页"""
        if not html_content:
            return False
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找下一页链接
        next_indicators = [
            soup.find('a', href=lambda x: x and 'index_' in x),
            soup.find('a', string=lambda x: x and '下一页' in x),
            soup.find('a', string=lambda x: x and '>' in x),
            soup.find('div', class_='pagination'),
            soup.find('div', class_='page')
        ]
        
        return any(next_indicators)
    
    def save_page(self, category_name, page_num, html_content):
        """保存页面到results的子文件夹"""
        try:
            # 创建分类子目录
            category_dir = os.path.join('results', category_name)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"page_{page_num}_{timestamp}.html"
            filepath = os.path.join(category_dir, filename)
            
            # 保存HTML文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已保存: {filepath}")
            
        except Exception as e:
            logger.error(f"保存失败: {e}")
    
    def crawl_category(self, category_name, category_config):
        """爬取单个分类"""
        logger.info(f"开始爬取: {category_name}")
        
        page_num = 1
        max_pages = CRAWL_CONFIG['max_pages_per_category']
        
        while True:
            # 构建页面URL
            if page_num == 1:
                page_url = category_config['first_page']
            else:
                page_url = category_config['page_pattern'].format(page_num - 1)
            
            logger.info(f"第 {page_num} 页: {page_url}")
            
            # 获取页面内容
            html_content = self.get_page_content(page_url)
            if not html_content:
                logger.warning(f"获取失败，停止爬取")
                break
            
            # 保存页面
            self.save_page(category_name, page_num, html_content)
            
            # 检查是否有下一页
            if page_num > 1 and not self.has_next_page(html_content):
                logger.info(f"没有更多页面")
                break
            
            # 检查页数限制
            if max_pages and page_num >= max_pages:
                logger.info(f"达到页数限制 {max_pages}")
                break
            
            page_num += 1
            time.sleep(CRAWL_CONFIG['delay_between_pages'])
        
        logger.info(f"{category_name} 完成，共 {page_num - 1} 页")
    
    def crawl_all(self):
        """爬取所有分类"""
        logger.info("开始爬取所有分类")
        
        for category_key, category_config in POLICY_CATEGORIES.items():
            if not category_config.get('enabled', True):
                continue
            
            try:
                self.crawl_category(category_key, category_config)
                time.sleep(CRAWL_CONFIG['delay_between_categories'])
            except Exception as e:
                logger.error(f"爬取 {category_key} 时出错: {e}")
                continue
        
        logger.info("所有分类爬取完成")

def main():
    """主函数"""
    try:
        logger.info("开始执行爬虫")
        crawler = NDRCCrawler()
        crawler.crawl_all()
        logger.info("爬虫执行完成")
    except Exception as e:
        logger.error(f"执行出错: {e}")

if __name__ == "__main__":
    main()
