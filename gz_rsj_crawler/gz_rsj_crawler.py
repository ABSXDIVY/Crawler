#!/usr/bin/env python3
import requests
import json
import os
import time
from datetime import datetime
import logging
from config import CRAWLER_CONFIG, CRAWLER_TYPES

# 配置日志
logging.basicConfig(
    level=getattr(logging, CRAWLER_CONFIG['log']['level']),
    format=CRAWLER_CONFIG['log']['format'],
    handlers=[
        logging.FileHandler(os.path.join(CRAWLER_CONFIG['log']['dir'], 'gz_rsj_crawler.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('gz_rsj_crawler')

class GZRSSCrawler:
    def __init__(self, crawler_type=None):
        # 如果未指定类型，使用配置文件中的默认类型
        self.crawler_type = crawler_type or CRAWLER_CONFIG['current_type']
        # 动态生成基础URL
        self.base_url = CRAWLER_CONFIG['base_url_template'].format(self.crawler_type)
        self.headers = CRAWLER_CONFIG['headers']
        self.cookies = CRAWLER_CONFIG['cookies']
        self.data_dir = os.path.join(CRAWLER_CONFIG['data_dir'], self.crawler_type)
        self.default_page = CRAWLER_CONFIG['crawl']['default_page']
        self.default_start_page = CRAWLER_CONFIG['crawl']['default_start_page']
        self.default_end_page = CRAWLER_CONFIG['crawl']['default_end_page']
        self.auto_crawl_all = CRAWLER_CONFIG['crawl']['auto_crawl_all']
        self.delay = CRAWLER_CONFIG['crawl']['delay']
        self.max_retries = CRAWLER_CONFIG['crawl']['max_retries']
        self.params = CRAWLER_CONFIG['params']

        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)

    def set_crawler_type(self, crawler_type):
        """设置爬虫类型"""
        if crawler_type not in CRAWLER_TYPES:
            logger.error(f'无效的爬虫类型: {crawler_type}，可选类型: {list(CRAWLER_TYPES.keys())}')
            return False

        self.crawler_type = crawler_type
        self.base_url = CRAWLER_CONFIG['base_url_template'].format(self.crawler_type)
        self.data_dir = os.path.join(CRAWLER_CONFIG['data_dir'], self.crawler_type)
        os.makedirs(self.data_dir, exist_ok=True)
        logger.info(f'已切换爬虫类型至: {crawler_type} ({CRAWLER_TYPES[crawler_type]})')
        return True

    def crawl_page(self, page_num=1):
        """爬取指定页码的数据，支持重试机制"""
        params = {
            'page': page_num,
            'sid': self.params['sid']
        }

        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f'开始爬取第 {page_num} 页数据 (类型: {self.crawler_type} - {CRAWLER_TYPES[self.crawler_type]})')
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    cookies=self.cookies,
                    params=params
                )

                if response.status_code == 200:
                    try:
                        data = response.json()
                        # 检查数据是否为空
                        if not data or ('articles' not in data) or (not data['articles']):
                            logger.warning(f'第 {page_num} 页没有数据')
                            return None

                        # 保存数据
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f'gz_rsj_{self.crawler_type}_page_{page_num}_{timestamp}.json'
                        filepath = os.path.join(self.data_dir, filename)

                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)

                        logger.info(f'成功爬取第 {page_num} 页数据，共 {len(data["articles"])} 条记录，已保存至: {filepath}')
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f'第 {page_num} 页数据解析失败: {str(e)}')
                        return None
                elif response.status_code == 404:
                    logger.error(f'爬取第 {page_num} 页失败，状态码: {response.status_code} (页面不存在)')
                    # 对于404错误，直接返回特殊标记表示无数据
                    return {'no_more_data': True}
                else:
                    logger.error(f'爬取第 {page_num} 页失败，状态码: {response.status_code}')
                    retries += 1
                    if retries <= self.max_retries:
                        logger.info(f'第 {retries} 次重试爬取第 {page_num} 页')
                        time.sleep(self.delay * 2)
                    else:
                        logger.error(f'超过最大重试次数，无法爬取第 {page_num} 页')
                        return None
            except Exception as e:
                logger.error(f'爬取第 {page_num} 页时发生错误: {str(e)}')
                retries += 1
                if retries <= self.max_retries:
                    logger.info(f'第 {retries} 次重试爬取第 {page_num} 页')
                    time.sleep(self.delay * 2)
                else:
                    logger.error(f'超过最大重试次数，无法爬取第 {page_num} 页')
                    return None

    def crawl_multiple_pages(self, start_page=None, end_page=None, delay=None):
        """爬取多个页码的数据"""
        # 使用默认参数
        start_page = start_page or self.default_start_page
        end_page = end_page or self.default_end_page
        delay = delay or self.delay

        # 如果启用自动爬取所有页面，则忽略end_page
        if self.auto_crawl_all:
            logger.info(f'开始自动爬取所有页面 (类型: {self.crawler_type} - {CRAWLER_TYPES[self.crawler_type]})')
            page_num = start_page
            while True:
                data = self.crawl_page(page_num)
                if not data:
                    logger.info('没有更多数据，停止爬取')
                    break
                elif 'no_more_data' in data and data['no_more_data']:
                    logger.info(f'检测到404错误，当前类型 {self.crawler_type} 没有更多数据')
                    return False  # 返回False表示遇到404，需要切换类型
                elif ('articles' not in data) or (not data['articles']):
                    logger.info('没有更多数据，停止爬取')
                    break
                page_num += 1
                time.sleep(delay)
            logger.info(f'完成自动爬取所有页面，共爬取 {page_num - start_page} 页')
            return True
        else:
            logger.info(f'开始爬取第 {start_page} 至 {end_page} 页数据 (类型: {self.crawler_type} - {CRAWLER_TYPES[self.crawler_type]})')
            for page_num in range(start_page, end_page + 1):
                data = self.crawl_page(page_num)
                if data and 'no_more_data' in data and data['no_more_data']:
                    logger.info(f'检测到404错误，当前类型 {self.crawler_type} 没有更多数据')
                    return False  # 返回False表示遇到404，需要切换类型
                # 添加延时，避免请求过快
                if page_num < end_page:
                    time.sleep(delay)
            logger.info(f'完成爬取第 {start_page} 至 {end_page} 页数据')
            return True

    def crawl_all_types(self):
        """爬取所有类型的数据"""
        logger.info('开始爬取所有类型的数据')
        current_type_index = list(CRAWLER_TYPES.keys()).index(self.crawler_type)
        types_to_crawl = list(CRAWLER_TYPES.keys())[current_type_index:]
        
        for crawler_type in types_to_crawl:
            self.set_crawler_type(crawler_type)
            result = self.crawl_multiple_pages()
            if not result:
                logger.info(f'当前类型 {crawler_type} 爬取遇到404，自动切换到下一个类型')
                continue
        logger.info('完成爬取所有类型的数据')

if __name__ == '__main__':
    # 创建爬虫实例
    crawler = GZRSSCrawler()

    # 爬取单页数据（使用配置文件中的默认页码）
    # crawler.crawl_page(crawler.default_page)

    # 爬取多页数据（使用配置文件中的设置）
    crawler.crawl_multiple_pages()

    # 如果需要爬取所有类型的数据，可以使用以下方法
    # crawler.crawl_all_types()

    logger.info('爬虫任务执行完毕')