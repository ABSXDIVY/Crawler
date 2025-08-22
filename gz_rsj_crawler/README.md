# 广州市人力资源和社会保障局爬虫

这个爬虫用于从广州市人力资源和社会保障局网站爬取政策数据，支持多种类型的数据爬取和自动爬取所有页面功能。

## 项目结构
```
gz_rsj_crawler/
├── gz_rsj_crawler.py  # 爬虫主程序
├── config.py          # 配置文件
├── test_crawler.py    # 测试脚本
├── data/              # 数据保存目录
│   ├── 505/           # 规范性文件数据
│   ├── 506/           # 其他文件数据
│   └── 507/           # 解读文件数据
├── logs/              # 日志目录
└── README.md          # 项目说明
```

## 功能特点
- 支持单页和多页数据爬取
- 支持自动爬取所有页面直到没有数据
- 支持多种类型数据爬取（505: 规范性文件, 506: 其他文件, 507: 解读文件）
- 自动保存爬取的数据为JSON格式，按类型分类存储
- 完善的日志记录系统
- 灵活的配置管理
- 异常处理和重试机制
- 提供测试脚本验证功能

## 环境要求
- Python 3.6+
- requests库

## 安装依赖
```bash
pip install requests
```

## 使用方法

### 直接运行
```bash
cd e:\cursor_workspace\Crawler\gz_rsj_crawler
python gz_rsj_crawler.py
```
默认会使用配置文件中的设置爬取数据。

### 爬取单页数据
修改`gz_rsj_crawler.py`文件中的主函数部分：
```python
# 爬取单页数据（使用配置文件中的默认页码）
crawler.crawl_page(crawler.default_page)
```

### 爬取多页数据
修改`gz_rsj_crawler.py`文件中的主函数部分：
```python
# 爬取多页数据（使用配置文件中的设置）
crawler.crawl_multiple_pages()
```

### 爬取所有类型的数据
修改`gz_rsj_crawler.py`文件中的主函数部分：
```python
# 爬取所有类型的数据
crawler.crawl_all_types()
```

### 运行测试
```bash
python test_crawler.py
```
测试脚本会验证单页爬取、多页爬取和自动爬取所有页面功能。

## 配置说明
配置文件`config.py`中包含以下主要配置项：

- `CRAWLER_TYPES`: 支持的爬虫类型定义
- `base_url_template`: API基础URL模板
- `current_type`: 当前爬取类型
- `params`: 请求参数
- `headers`: HTTP请求头
- `cookies`: HTTP cookies
- `data_dir`: 数据保存根目录
- `log`: 日志配置（目录、级别、格式）
- `crawl`: 爬取配置
  - `default_page`: 默认爬取页码
  - `auto_crawl_all`: 是否自动爬取所有页面
  - `default_start_page`: 默认起始页码
  - `default_end_page`: 默认结束页码（自动爬取时无效）
  - `delay`: 爬取间隔时间(秒)
  - `max_retries`: 最大重试次数

## 注意事项
1. 请遵守网站的爬虫规则，不要过度爬取导致服务器负担过重
2. 爬取间隔时间和最大重试次数可以在配置文件中调整
3. 如遇到cookies过期问题，请更新配置文件中的cookies信息
4. 自动爬取所有页面功能会持续爬取直到没有数据，可能会耗时较长

## 维护者
AI助手

## 日期
"+datetime.now().strftime('%Y-%m-%d')+"}}]}}}