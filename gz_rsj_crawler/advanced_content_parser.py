#!/usr/bin/env python3
"""高级URL内容解析器，按照特定格式提取和保存内容"""
import requests
import pandas as pd
import os
import json
import time
import logging
from bs4 import BeautifulSoup
from config import CRAWLER_CONFIG
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# 配置日志
logging.basicConfig(
    level=getattr(logging, CRAWLER_CONFIG['log']['level']),
    format=CRAWLER_CONFIG['log']['format'],
    handlers=[
        logging.FileHandler(os.path.join(CRAWLER_CONFIG['log']['dir'], 'advanced_content_parser.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('advanced_content_parser')


class AdvancedContentParser:
    def __init__(self, excel_path, output_file=None):
        self.excel_path = excel_path
        self.output_file = output_file or os.path.join(os.path.dirname(excel_path), 'parsed_content_formatted.xlsx')
        self.headers = CRAWLER_CONFIG['headers']
        self.cookies = CRAWLER_CONFIG['cookies']
        self.delay = CRAWLER_CONFIG['crawl']['delay']
        self.max_retries = CRAWLER_CONFIG['crawl']['max_retries']
        
        # 创建输出目录
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # 创建工作簿
        self.workbook = Workbook()
        # 移除默认工作表
        default_sheet = self.workbook.active
        self.workbook.remove(default_sheet)
        
    def parse_url_content(self, url):
        """解析单个URL的内容，提取具有特定样式的段落"""
        retries = 0
        while retries <= self.max_retries:
            try:
                logger.info(f'开始解析URL: {url}')
                response = requests.get(url, headers=self.headers, cookies=self.cookies)
                
                if response.status_code == 200:
                    # 使用BeautifulSoup解析HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 查找内容容器
                    content_div = soup.find('div', class_='content', style='margin-top: 30px')
                    
                    if content_div:
                        # 提取标题
                        title_element = content_div.find('h1', class_='title')
                        title = title_element.get_text(strip=True) if title_element else ''
                        
                        # 提取日期行
                        date_row = content_div.find('div', class_='date-row')
                        date_text = date_row.get_text(strip=True) if date_row else ''
                        
                        # 提取具有特定样式的段落
                        paragraphs = []
                        # 查找所有p标签，其style属性包含text-align
                        p_tags = content_div.find_all('p', style=lambda s: s and 'text-align' in s)
                        for p in p_tags:
                            # 提取段落文本
                            p_text = p.get_text(strip=True)
                            if p_text:
                                paragraphs.append(p_text)
                        
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
                            'paragraphs': paragraphs,
                            'attachments': json.dumps(attachments, ensure_ascii=False)
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
        return None
    
    def format_paragraphs(self, paragraphs):
        """将段落每5条合并为一行"""
        formatted = []
        for i in range(0, len(paragraphs), 5):
            chunk = paragraphs[i:i+5]
            # 用换行符连接段落
            formatted_chunk = '\n'.join(chunk)
            formatted.append(formatted_chunk)
        return formatted
    
    def process_worksheet(self, sheet_name, urls):
        """处理单个工作表中的所有URL"""
        logger.info(f'处理工作表: {sheet_name}')
        
        # 创建新工作表
        sheet = self.workbook.create_sheet(title=sheet_name)
        # 设置表头
        sheet.append(['序号', '标题', '日期信息', '内容段落', '链接', '附件'])
        
        # 解析每个URL
        for i, url in enumerate(urls):
            logger.info(f'处理进度: {i+1}/{len(urls)}')
            result = self.parse_url_content(url)
            if result:
                # 格式化段落
                formatted_paragraphs = self.format_paragraphs(result['paragraphs'])
                
                # 如果没有段落，添加一行
                if not formatted_paragraphs:
                    sheet.append([
                        i+1,
                        result['title'],
                        result['date_info'],
                        '',
                        result['url'],
                        result['attachments']
                    ])
                else:
                    # 添加第一行（包含标题、日期等信息）
                    sheet.append([
                        i+1,
                        result['title'],
                        result['date_info'],
                        formatted_paragraphs[0],
                        result['url'],
                        result['attachments']
                    ])
                    
                    # 添加后续行（仅包含段落）
                    for para in formatted_paragraphs[1:]:
                        sheet.append(['', '', '', para, '', ''])
            
            # 添加延时，避免请求过快
            time.sleep(self.delay)
        
    def parse_all_urls_from_excel(self):
        """从Excel文件中读取所有URL并解析其内容"""
        logger.info(f'开始从Excel文件读取URL: {self.excel_path}')
        
        # 读取Excel文件中的所有工作表
        excel_data = pd.read_excel(self.excel_path, sheet_name=None)
        
        # 遍历每个工作表
        for sheet_name, df in excel_data.items():
            # 检查是否存在'链接'列
            if '链接' in df.columns:
                urls = df['链接'].dropna().tolist()
                logger.info(f'工作表 {sheet_name} 中找到 {len(urls)} 个URL')
                
                # 处理当前工作表
                self.process_worksheet(sheet_name, urls)
            else:
                logger.warning(f'工作表 {sheet_name} 中未找到"链接"列')
        
        # 保存工作簿
        self.workbook.save(self.output_file)
        logger.info(f'解析完成，结果已保存至: {self.output_file}')
        return self.output_file


def main():
    # Excel文件路径
    excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gz_rsj_data.xlsx')
    
    # 创建解析器实例
    parser = AdvancedContentParser(excel_path)
    
    # 解析所有URL
    output_file = parser.parse_all_urls_from_excel()
    
    logger.info(f'URL内容解析任务执行完毕，结果已保存至: {output_file}')


if __name__ == '__main__':
    main()