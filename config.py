#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家发改委爬虫配置文件
根据具体的URL规则配置爬取参数
"""

# 政策分类配置
POLICY_CATEGORIES = {
    '发展改革委令': {
        'name': '发展改革委令',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl',
        'first_page': 'https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl/index.html',
        'page_pattern': 'https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl/index_{}.html',
        'description': '最高级别的政策文件',
        'enabled': True
    },
    '规范性文件': {
        'name': '规范性文件',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj',
        'first_page': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/index.html',
        'page_pattern': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/index_{}.html',
        'description': '重要规范性政策文件',
        'enabled': True
    },
    '规划文本': {
        'name': '规划文本',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghwb',
        'first_page': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghwb/index.html',
        'page_pattern': 'https://www.ndrc.gov.cn/xxgk/zcfb/ghwb/index_{}.html',
        'description': '发展规划类文件',
        'enabled': True
    },
    '公告': {
        'name': '公告',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/gg',
        'first_page': 'https://www.ndrc.gov.cn/xxgk/zcfb/gg/index.html',
        'page_pattern': 'https://www.ndrc.gov.cn/xxgk/zcfb/gg/index_{}.html',
        'description': '重要公告信息',
        'enabled': True
    },
    '通知': {
        'name': '通知',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/tz',
        'first_page': 'https://www.ndrc.gov.cn/xxgk/zcfb/tz/index.html',
        'page_pattern': 'https://www.ndrc.gov.cn/xxgk/zcfb/tz/index_{}.html',
        'description': '日常通知文件',
        'enabled': True
    }
}

# 爬取配置
CRAWL_CONFIG = {
    # 每个分类最多爬取的页数（设为None表示无限制，直到没有下一页）
    'max_pages_per_category': None,
    
    # 页面访问之间的延迟（秒）
    'delay_between_pages': 1,
    
    # 内容提取之间的延迟（秒）
    'delay_between_extractions': 0.5,
    
    # 分类之间的延迟（秒）
    'delay_between_categories': 2
}

# 网站配置
WEBSITE_CONFIG = {
    # 发改委网站基础URL
    'base_url': 'https://www.ndrc.gov.cn',
    
    # 请求头配置
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    },
    
    # 请求超时设置（秒）
    'timeout': 30,
    
    # 重试次数
    'max_retries': 3,
    
    # 重试延迟（秒）
    'retry_delay': 5
}

# 数据提取配置
EXTRACTION_CONFIG = {
    # 需要提取的字段
    'fields_to_extract': [
        'title',           # 标题
        'publish_date',    # 发布日期
        'document_number', # 文号
        'category',        # 分类
        'url',            # 链接
        'content_summary', # 内容摘要
        'full_content'     # 完整内容
    ],
    
    # 内容提取的最大长度
    'max_content_length': 10000,
    
    # 是否提取完整内容
    'extract_full_content': True,
    
    # 内容清理规则
    'content_cleanup_rules': [
        'remove_extra_whitespace',
        'remove_html_tags',
        'normalize_line_breaks'
    ]
}

# 输出配置
OUTPUT_CONFIG = {
    # 输出文件格式
    'output_format': 'excel',  # 'excel', 'csv', 'json'
    
    # 输出文件名前缀
    'filename_prefix': 'ndrc_policy',
    
    # 是否包含时间戳
    'include_timestamp': True,
    
    # 输出目录
    'output_dir': 'results',
    
    # 日志目录
    'log_dir': 'logs',
    
    # 提取内容保存目录
    'content_dir': 'extracted_content'
}
