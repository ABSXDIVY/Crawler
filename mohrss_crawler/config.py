#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人力资源和社会保障部网站爬虫配置文件

包含爬虫运行所需的各种参数设置
"""

# 网站配置
WEBSITE_CONFIG = {
    'base_url': 'https://www.mohrss.gov.cn',
    'search_url': '/was5/web/search',
    'channel_id': '203464',
    'order_by': 'date',
    'default': 'isall'
}

# 请求头配置
HEADERS = {
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
}

# Cookies配置
COOKIES = {
    'HttpOnly': 'true',
    'Secure': '',
    'JSESSIONID': '376F1CEDDE3CA4D4153A1008F33BD2E8',
    '__tst_status': '3298241174#',
    'EO_Bot_Ssid': '3838967808',
    'arialoadData': 'false',
    'ariauseGraymode': 'false'
}

# 爬取配置
CRAWL_CONFIG = {
    'start_page': 1,
    'end_page': 5,
    'max_retries': 3,
    'timeout': 30,
    'min_delay': 1,
    'max_delay': 3,
    'page_delay_min': 3,
    'page_delay_max': 6
}

# 文件保存配置
SAVE_CONFIG = {
    'results_dir': 'results',
    'logs_dir': 'logs',
    'analysis_dir': 'analysis_results',
    'extracted_dir': 'extracted_content',
    'save_raw_html': True,
    'save_json': True,
    'save_excel': True
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'encoding': 'utf-8'
}

# 数据解析配置
PARSER_CONFIG = {
    # 可能的搜索结果容器选择器
    'search_result_selectors': [
        'div.search-result-item',
        'li.search-item',
        'div.result-item',
        'div.search-item',
        'li.result-item'
    ],
    
    # 标题选择器
    'title_selectors': [
        'a',
        'h3',
        'div.title',
        'span.title',
        'h4'
    ],
    
    # 链接选择器
    'link_selectors': [
        'a'
    ],
    
    # 日期选择器
    'date_selectors': [
        'span.date',
        'div.date',
        'time',
        'span.time',
        'div.time'
    ],
    
    # 摘要选择器
    'summary_selectors': [
        'div.summary',
        'p.summary',
        'div.content',
        'p.content',
        'div.description'
    ]
}

# 数据分析配置
ANALYSIS_CONFIG = {
    'enable_analysis': True,
    'title_length_analysis': True,
    'date_analysis': True,
    'page_statistics': True,
    'content_summary': True
}

# 错误处理配置
ERROR_CONFIG = {
    'continue_on_error': True,
    'log_errors': True,
    'save_error_pages': True,
    'max_consecutive_errors': 3
}
