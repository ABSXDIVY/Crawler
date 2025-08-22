#!/usr/bin/env python3
"""测试脚本 for 广州市人力资源和社会保障局爬虫"""
import os
import sys
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gz_rsj_crawler import GZRSSCrawler
from config import CRAWLER_CONFIG, CRAWLER_TYPES

def test_single_page_crawl(crawler_type=None):
    """测试单页爬取"""
    print(f"===== 测试单页爬取 {'(' + crawler_type + ' - ' + CRAWLER_TYPES.get(crawler_type, '') + ')' if crawler_type else ''} ======")
    crawler = GZRSSCrawler(crawler_type)
    page_num = CRAWLER_CONFIG['crawl']['default_page']
    print(f"开始爬取第 {page_num} 页数据...")
    start_time = time.time()
    data = crawler.crawl_page(page_num)
    end_time = time.time()
    
    if data:
        print(f"成功爬取第 {page_num} 页数据，耗时: {end_time - start_time:.2f} 秒")
        print(f"数据保存目录: {crawler.data_dir}")
        return True
    else:
        print(f"爬取第 {page_num} 页数据失败")
        return False

def test_multiple_pages_crawl(crawler_type=None, auto_crawl_all=False):
    """测试多页爬取"""
    print(f"===== 测试多页爬取 {'(' + crawler_type + ' - ' + CRAWLER_TYPES.get(crawler_type, '') + ')' if crawler_type else ''} ======")
    crawler = GZRSSCrawler(crawler_type)
    # 保存原始配置
    original_auto_crawl_all = crawler.auto_crawl_all
    
    # 设置自动爬取模式
    crawler.auto_crawl_all = auto_crawl_all
    
    start_page = CRAWLER_CONFIG['crawl']['default_start_page']
    end_page = min(CRAWLER_CONFIG['crawl']['default_end_page'], start_page + 2)  # 限制测试页数，避免耗时过长
    
    if auto_crawl_all:
        print(f"开始自动爬取所有页面 (从第 {start_page} 页开始)...")
    else:
        print(f"开始爬取第 {start_page} 至 {end_page} 页数据...")
    
    start_time = time.time()
    crawler.crawl_multiple_pages(start_page=start_page, end_page=end_page, delay=CRAWLER_CONFIG['crawl']['delay'])
    end_time = time.time()
    
    if auto_crawl_all:
        print(f"自动爬取所有页面完成，耗时: {end_time - start_time:.2f} 秒")
    else:
        print(f"爬取第 {start_page} 至 {end_page} 页数据完成，耗时: {end_time - start_time:.2f} 秒")
    
    print(f"数据保存目录: {crawler.data_dir}")
    
    # 恢复原始配置
    crawler.auto_crawl_all = original_auto_crawl_all
    return True

def test_crawl_all_types():
    """测试爬取所有类型的数据"""
    print("===== 测试爬取所有类型的数据 ======")
    crawler = GZRSSCrawler()
    start_time = time.time()
    crawler.crawl_all_types()
    end_time = time.time()
    print(f"爬取所有类型的数据完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"数据保存目录: {CRAWLER_CONFIG['data_dir']}")
    return True

def test_auto_crawl_all():
    """测试自动爬取所有页面"""
    print("===== 测试自动爬取所有页面 ======")
    # 使用第一个类型进行测试
    crawler_type = next(iter(CRAWLER_TYPES.keys()))
    return test_multiple_pages_crawl(crawler_type=crawler_type, auto_crawl_all=True)

if __name__ == '__main__':
    print("广州市人力资源和社会保障局爬虫测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"支持的爬虫类型: {', '.join([f'{k} ({v})' for k, v in CRAWLER_TYPES.items()])}")
    
    # 测试单页爬取 (默认类型)
    single_page_success = test_single_page_crawl()
    print()
    
    # 如果单页爬取成功，继续其他测试
    if single_page_success:
        time.sleep(2)  # 短暂停顿
        
        # 测试多页爬取 (默认类型)
        test_multiple_pages_crawl()
        print()
        time.sleep(2)
        
        # 测试自动爬取所有页面
        test_auto_crawl_all()
        print()
        time.sleep(2)
        
        # 测试爬取所有类型
        # 注意：这个测试可能会耗时较长，如需跳过请注释下面这行
        # test_crawl_all_types()
    
    print()
    print("测试完成")
    print(f"日志文件位置: {os.path.join(CRAWLER_CONFIG['log']['dir'], 'gz_rsj_crawler.log')}"}}}]})