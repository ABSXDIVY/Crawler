#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人力资源和社会保障部网站原始页面爬虫

功能：
1. 获取人力资源和社会保障部网站的原始页面内容
2. 支持多页面爬取
3. 保存原始HTML页面
4. 详细的日志记录
5. 错误处理和重试机制

作者：AI助手
创建时间：2025-08-18
"""

import requests
import time
import random
import logging
import os
from datetime import datetime
from typing import Optional
import warnings
warnings.filterwarnings('ignore')
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

class MOHRSSRawCrawler:
    """人力资源和社会保障部网站原始页面爬虫类"""
    
    def __init__(self, base_url: str = "https://www.mohrss.gov.cn"):
        """
        初始化爬虫
        
        Args:
            base_url: 网站基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.setup_session()
        self.setup_logging()
        self.error_count = 0
        
    def setup_session(self):
        """设置会话参数"""
        # 设置请求头
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
        
        # 设置cookies
        self.session.cookies.update({
            'HttpOnly': 'true',
            'Secure': '',
            'JSESSIONID': '376F1CEDDE3CA4D4153A1008F33BD2E8',
            '__tst_status': '3298241174#',
            'EO_Bot_Ssid': '3838967808',
            'arialoadData': 'false',
            'ariauseGraymode': 'false'
        })
        
    def setup_logging(self):
        """设置日志记录"""
        # 创建logs目录
        os.makedirs('logs', exist_ok=True)
        
        # 设置日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 创建日志文件名
        timestamp = datetime.now().strftime('%Y%m%d')
        log_filename = f'logs/mohrss_raw_crawler_{timestamp}.log'
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("人力资源和社会保障部网站原始页面爬虫初始化完成")
        
    def get_page(self, url: str, referer: str = None, max_retries: int = 3) -> Optional[requests.Response]:
        """
        获取页面内容
        
        Args:
            url: 目标URL
            referer: 来源页面URL
            max_retries: 最大重试次数
            
        Returns:
            Response对象或None
        """
        for attempt in range(max_retries):
            try:
                # 设置Referer
                if referer:
                    self.session.headers['Referer'] = referer
                
                # 随机延迟
                time.sleep(random.uniform(1, 3))
                
                # 发送请求
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                self.logger.info(f"成功获取页面: {url}")
                return response
                
            except requests.exceptions.RequestException as e:
                self.error_count += 1
                self.logger.warning(f"第{attempt + 1}次请求失败: {url}, 错误: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    self.logger.error(f"请求失败，已达到最大重试次数: {url}")
                    return None
                    
    def save_raw_page(self, html_content: str, page_num: int):
        """保存原始页面内容"""
        try:
            # 创建results目录（相对脚本目录）
            results_dir = os.path.join(MODULE_DIR, 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(results_dir, f"mohrss_raw_page_{page_num}_{timestamp}.html")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            self.logger.info(f"原始页面内容已保存: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"保存原始页面内容失败: {e}")
            return None
            
    def crawl_page(self, page_num: int) -> bool:
        """
        爬取指定页面
        
        Args:
            page_num: 页码
            
        Returns:
            是否成功
        """
        # 构建URL
        url = f"{self.base_url}/was5/web/search?channelid=203464&orderby=date&default=isall&page={page_num}"
        
        # 设置Referer
        if page_num > 1:
            referer = f"{self.base_url}/was5/web/search?channelid=203464&orderby=date&default=isall&page={page_num-1}"
        else:
            referer = None
            
        self.logger.info(f"开始爬取第{page_num}页: {url}")
        
        # 获取页面内容
        response = self.get_page(url, referer)
        if not response:
            return False
            
        # 保存原始页面内容
        saved_file = self.save_raw_page(response.text, page_num)
        
        if saved_file:
            self.logger.info(f"第{page_num}页爬取完成，文件已保存: {saved_file}")
            return True
        else:
            self.logger.error(f"第{page_num}页保存失败")
            return False
        
    def crawl_multiple_pages(self, start_page: int = 1, end_page: int = 30):
        """
        爬取多个页面
        
        Args:
            start_page: 开始页码
            end_page: 结束页码
        """
        success_count = 0
        total_pages = end_page - start_page + 1
        
        self.logger.info(f"开始爬取第{start_page}页到第{end_page}页")
        
        for page_num in range(start_page, end_page + 1):
            try:
                if self.crawl_page(page_num):
                    success_count += 1
                
                # 页面间延迟
                if page_num < end_page:
                    delay = random.uniform(3, 6)
                    self.logger.info(f"等待{delay:.1f}秒后继续...")
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"爬取第{page_num}页时出错: {e}")
                continue
                
        self.logger.info(f"所有页面爬取完成")
        self.logger.info(f"成功爬取: {success_count}/{total_pages} 页")
        self.logger.info(f"错误次数: {self.error_count}")
        
        return success_count
        
    def run(self, start_page: int = 1, end_page: int = 30):
        """
        运行爬虫
        
        Args:
            start_page: 开始页码
            end_page: 结束页码
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("人力资源和社会保障部网站原始页面爬虫开始运行")
            self.logger.info("=" * 50)
            
            # 爬取数据
            success_count = self.crawl_multiple_pages(start_page, end_page)
            
            self.logger.info("=" * 50)
            self.logger.info("爬虫运行完成")
            self.logger.info(f"成功爬取: {success_count} 页")
            self.logger.info(f"错误次数: {self.error_count}")
            self.logger.info("=" * 50)
            
            return success_count
            
        except Exception as e:
            self.logger.error(f"爬虫运行出错: {e}")
            return 0

def main():
    """主函数"""
    try:
        # 创建爬虫实例
        crawler = MOHRSSRawCrawler()
        
        # 运行爬虫（爬取前5页）
        success_count = crawler.run(start_page=1, end_page=30)
        
        print(f"\n爬取完成！成功爬取 {success_count} 页")
        print("原始页面文件保存在 results/ 目录下")
        print("日志文件保存在 logs/ 目录下")
        
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
