#!/usr/bin/env python3
"""解析Excel表格中URL内容的爬虫"""
import requests
import pandas as pd
import os
import json
import time
import logging
from bs4 import BeautifulSoup
from config import CRAWLER_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, CRAWLER_CONFIG['log']['level']),
    format=CRAWLER_CONFIG['log']['format'],
    handlers=[
        logging.FileHandler(os.path.join(CRAWLER_CONFIG['log']['dir'], 'url_content_parser.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('url_content_parser')


class URLContentParser:
    def __init__(self, excel_path, output_dir=None):
        self.excel_path = excel_path
        self.output_dir = output_dir or os.path.join(os.path.dirname(excel_path), 'parsed_content')
        self.headers = CRAWLER_CONFIG['headers']
        self.cookies = CRAWLER_CONFIG['cookies']
        self.delay = CRAWLER_CONFIG['crawl']['delay']
        self.max_retries = CRAWLER_CONFIG['crawl']['max_retries']
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def parse_url_content(self, url):
        """解析单个URL的内容，提取特定样式的容器"""
        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f'开始解析URL: {url}')
                response = requests.get(url, headers=self.headers, cookies=self.cookies)
                
                if response.status_code == 200:
                    # 使用BeautifulSoup解析HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找具有特定样式的容器
                    content_div = soup.find('div', class_='content', style='margin-top: 30px')
                    
                    if content_div:
                        # 提取标题
                        title_element = content_div.find('h1', class_='title')
                        title = title_element.get_text(strip=True) if title_element else ''
                        
                        # 提取日期行
                        date_row = content_div.find('div', class_='date-row')
                        date_text = date_row.get_text(strip=True) if date_row else ''
                        
                        # 提取文章内容
                        article_content = content_div.find('div', class_='article-content')
                        content_text = article_content.get_text(strip=True) if article_content else ''
                        
                        # 提取附件链接
                        attachments = []
                        attachment_links = content_div.find_all('a', class_='nfw-cms-attachment')
                        for link in attachment_links:
                            attachment_url = link.get('href', '')
                            attachment_name = link.get_text(strip=True)
                            attachments.append({
                                'name': attachment_name,
                                'url': attachment_url
                            })
                        
                        result = {
                            'url': url,
                            'title': title,
                            'date_info': date_text,
                            'content': content_text,
                            'attachments': json.dumps(attachments, ensure_ascii=False)  # 将附件列表转换为JSON字符串
                        }
                        
                        logger.info(f'成功解析URL: {url}')
                        return result
                    else:
                        logger.warning(f'未找到指定样式的容器: {url}')
                        return None
                else:
                    logger.error(f'请求失败，状态码: {response.status_code}, URL: {url}')
                    retries += 1
                    if retries <= self.max_retries:
                        logger.info(f'第 {retries} 次重试URL: {url}')
                        time.sleep(self.delay * 2)
                    else:
                        logger.error(f'超过最大重试次数，无法解析URL: {url}')
                        return None
            except Exception as e:
                logger.error(f'解析URL时发生错误: {str(e)}, URL: {url}')
                retries += 1
                if retries <= self.max_retries:
                    logger.info(f'第 {retries} 次重试URL: {url}')
                    time.sleep(self.delay * 2)
                else:
                    logger.error(f'超过最大重试次数，无法解析URL: {url}')
                    return None
    
    def parse_all_urls_from_excel(self):
        """从Excel文件中读取所有URL并解析其内容"""
        logger.info(f'开始从Excel文件读取URL: {self.excel_path}')
        
        # 读取Excel文件中的所有工作表
        excel_data = pd.read_excel(self.excel_path, sheet_name=None)
        
        # 存储所有解析结果
        all_results = []
        
        # 遍历每个工作表
        for sheet_name, df in excel_data.items():
            logger.info(f'处理工作表: {sheet_name}')
            
            # 检查是否存在'链接'列
            if '链接' in df.columns:
                urls = df['链接'].dropna().tolist()
                logger.info(f'工作表 {sheet_name} 中找到 {len(urls)} 个URL')
                
                # 解析每个URL
                for i, url in enumerate(urls):
                    logger.info(f'处理进度: {i+1}/{len(urls)}')
                    result = self.parse_url_content(url)
                    if result:
                        result['sheet_name'] = sheet_name
                        all_results.append(result)
                    
                    # 添加延时，避免请求过快
                    time.sleep(self.delay)
            else:
                logger.warning(f'工作表 {sheet_name} 中未找到"链接"列')
        
        # 保存结果到JSON文件
        json_output_file = os.path.join(self.output_dir, 'parsed_content.json')
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 保存结果到Excel文件
        excel_output_file = os.path.join(self.output_dir, 'parsed_content.xlsx')
        if all_results:
            # 转换为DataFrame
            df = pd.DataFrame(all_results)
            # 保存到Excel
            df.to_excel(excel_output_file, index=False)
        
        logger.info(f'解析完成，共处理 {len(all_results)} 个URL，结果已保存至: {json_output_file} 和 {excel_output_file}')
        return all_results


def main():
    # Excel文件路径
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gz_rsj_data.xlsx')
    
    # 创建解析器实例
    parser = URLContentParser(excel_path)
    
    # 解析所有URL
    parser.parse_all_urls_from_excel()
    
    logger.info('URL内容解析任务执行完毕')


if __name__ == '__main__':
    main()