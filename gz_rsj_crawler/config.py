#!/usr/bin/env python3
"""配置文件 for 广州市人力资源和社会保障局爬虫"""
import os
from datetime import datetime

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 爬虫类型定义
CRAWLER_TYPES = {
    '505': '规范性文件',
    '506': '其他文件',
    '507': '解读文件'
}

# 爬虫配置
CRAWLER_CONFIG = {
    # 基础URL模板
    'base_url_template': 'https://rsj.gz.gov.cn/gkmlpt/api/all/{}',
    # 当前爬取类型 (505, 506 或 507)
    'current_type': '505',
    # 请求参数
    'params': {
        'sid': '200025'
    },
    # 请求头
    'headers': {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://rsj.gz.gov.cn/gkmlpt/policy',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    },
    # Cookies
    'cookies': {
        'common-secure': '',
        'yfx_c_g_u_id_10004145': '_ck25082209262313159370199755487',
        'yfx_f_l_v_t_10004145': 'f_t_1755825983302__r_t_1755825983302__v_t_1755825983302__r_c_0',
        'front_uc_session': 'eyJpdiI6ImprVGZ2N0puVnFMb3NxYU9LN3N2RVE9PSIsInZhbHVlIjoibkNKa3k4Vkg0K0JrczRYXC9xbXVuNlppcEZZM01UY3ZkajdrZWRvNVwvQXhMU29yM1VcL2tCZjdLVVgya0JxcUJscCIsIm1hYyI6ImVjMDFkYWVlNDAzMDA1MjYwMjI2ZjVkZjE0MDUzZmMwZmFlMmE2MmM1NDVjNDQ4Y2VkNWQ4ODM4MDcwZjMyNzEifQ%3D%3D',
        'laravel_session': 'eyJpdiI6IlNFaVZ6TXZtOSttUXlPVEljXC9kNHZBPT0iLCJ2YWx1ZSI6Ik1sN1lId2xYWVwvWDhtU2JmWm5hMlVuYjA3XC9cLzdnTG55UkV0N2c4R0Q0cktyckRiTm16MWRuMVdUTzBkXC9wVWVQIiwibWFjIjoiNjIwOWExODBjMGRlYzFlMWRkMTVlMWVkNzMzYjExODI3MjYwYTEwZTU1MmMxNTMxNzAzZGIzNTkyYWVlZTMxNiJ9'
    },
    # 数据保存目录
    'data_dir': os.path.join(PROJECT_ROOT, 'data'),
    # 日志配置
    'log': {
        'dir': os.path.join(PROJECT_ROOT, 'logs'),
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    # 爬取配置
    'crawl': {
        # 爬取单页时的默认页码
        'default_page': 1,
        # 是否自动爬取所有页面
        'auto_crawl_all': True,
        # 爬取多页时的默认起始页码
        'default_start_page': 1,
        # 爬取多页时的默认结束页码 (当auto_crawl_all为True时，此参数无效)
        'default_end_page': 5,
        # 爬取间隔时间(秒)
        'delay': 1,
        # 最大重试次数
        'max_retries': 3
    }
}

# 动态生成基础URL
CRAWLER_CONFIG['base_url'] = CRAWLER_CONFIG['base_url_template'].format(CRAWLER_CONFIG['current_type'])

# 确保目录存在
os.makedirs(CRAWLER_CONFIG['data_dir'], exist_ok=True)
os.makedirs(CRAWLER_CONFIG['log']['dir'], exist_ok=True)

if __name__ == '__main__':
    # 打印配置信息
    print("广州市人力资源和社会保障局爬虫配置信息:")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"数据保存目录: {CRAWLER_CONFIG['data_dir']}")
    print(f"日志目录: {CRAWLER_CONFIG['log']['dir']}")
    print(f"默认爬取页码范围: {CRAWLER_CONFIG['crawl']['default_start_page']}-{CRAWLER_CONFIG['crawl']['default_end_page']}")