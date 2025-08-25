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
    # Cookies - 更新为用户提供的最新cookies
    'cookies': {
        'common-secure': '',
        'yfx_c_g_u_id_10004145': '_ck25082209262313159370199755487',
        'yfx_f_l_v_t_10004145': 'f_t_1755825983302__r_t_1755825983302__v_t_1755825983302__r_c_0',
        'Hm_lvt_1a1ba310b5d048d6cbdc05e1b4a71c7b': '1755830167',
        'Hm_lpvt_1a1ba310b5d048d6cbdc05e1b4a71c7b': '1755830167',
        'XSRF-TOKEN': 'eyJpdiI6IlEyUzgrcjFSa05OSVpjaGsrSCtNTGc9PSIsInZhbHVlIjoiQ1hLNlpMS2JyNE5tRFpFTHlqK3V5aUg0MFhudjVSM3N2cGtadUVvZFYrRnpOUjl4WjZOQ0ErUzVHa0FMN2xMazI3aHRQZXdkbTYwMDYvR0d0cXdWK0loMlJrcWN3ZG8rLzZmenRuMUpKL1B6VDd1TGJvdjBhR0J4WTdmUkM1YUoiLCJtYWMiOiI3YzE1MzE4YmJmNDM0YmIyYjA1NDU5Njc2MTc3YmQ3ZDFlZGY3ODMxMzdmNjAyNmJiMjM2NDg1ZGJmNTU2NDM5In0%3D',
        'laravel_session': 'eyJpdiI6IjhGcnVhc2tJMEpRZ3RRblVxNHRheHc9PSIsInZhbHVlIjoidC9pcXhXNGYwNUJacFk5TlhhMjhkN0FCdm5MMlp6cWZNdXdXZDJpVENLc2VHTXRaUzczQ2VPNU5FbVh2V1BYZnViWkp1eW44QXJOU1JxeDF0a2lPeG4wVmVET3padW9xalJocjFtcjl0YmN5ZitPRU5ycURlSHNiZ1lkcEN5alciLCJtYWMiOiIxMWQwOGRlMzNhZGJmOTZmYzZmYWQ4MDc5NmM5MjViYjE1MTdkYzQzM2NiMWZlZjdiZDExZmE0ZWQ5ZGQ5MjQzIn0%3D',
        'front_uc_session': 'eyJpdiI6InErMTk3RXc0ZUZGdFY2VnVyRVwvaURnPT0iLCJ2YWx1ZSI6IklPaklhV3BXMlRKUGZCYkJlcUo1cGxqcDVmcEpwZzlmVjBFWDJCWG9lU3hzSVpOa0QrN3VYMklqTkJvSktNNnQiLCJtYWMiOiIyNjdhMWIyZWI5MjU3MWE5NGEwODk1NTczZDc3ZjNjZjMwMjFkZDM2YzRmMjFlYzJlZTczM2NlMWE3ZDU5OWRhIn0%3D'
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