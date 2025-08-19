# 人力资源和社会保障部网站爬虫项目

## 项目简介

这是一个专门用于爬取人力资源和社会保障部网站政策文件信息的Python爬虫项目。项目采用模块化设计，包含完整的日志记录、错误处理、数据分析和结果保存功能。

## 功能特性

### 核心功能
- 爬取人力资源和社会保障部网站的政策文件信息
- 支持多页面批量爬取
- 智能数据解析和提取
- 自动错误处理和重试机制
- 详细的数据分析和统计
- 获取原始页面内容（无需解析）

### 数据保存功能
- 保存为Excel格式（包含多个工作表）
- 保存为JSON格式
- 保存原始HTML页面内容
- 自动生成数据统计报告

### 日志记录功能
- 详细的日志记录，包括INFO、WARNING、ERROR级别
- 日志同时输出到控制台和文件
- 日志文件按日期自动分割
- 日志文件保存在`logs`目录下

### 错误处理功能
- 自动捕获和记录所有异常
- 智能重试机制
- 连续错误检测和停止机制
- 详细的错误信息记录

### 数据分析功能
- 基本统计信息（总记录数、爬取页数等）
- 页面统计（每页记录数分布）
- 标题长度分析
- 内容摘要统计
- 发布时间分析

## 项目结构

```
mohrss_crawler/
├── mohrss_crawler.py              # 基础版爬虫程序
├── mohrss_crawler_enhanced.py     # 增强版爬虫程序（推荐使用）
├── mohrss_raw_crawler.py          # 原始页面爬虫程序
├── config.py                      # 配置文件
├── README.md                      # 项目说明文档
├── results/                       # 结果文件目录
│   ├── mohrss_crawler_results_*.xlsx
│   ├── mohrss_crawler_results_*.json
│   └── mohrss_raw_page_*.html
├── logs/                          # 日志文件目录
│   └── mohrss_crawler_*.log
├── analysis_results/              # 分析结果目录
│   └── mohrss_data_analysis_*.xlsx
└── extracted_content/             # 提取内容目录
```

## 安装和配置

### 1. 环境要求
- Python 3.7+
- 网络连接

### 2. 安装依赖
```bash
pip install requests pandas beautifulsoup4 openpyxl
```

### 3. 配置参数
编辑`config.py`文件来调整爬虫参数：

```python
# 爬取配置
CRAWL_CONFIG = {
    'start_page': 1,        # 开始页码
    'end_page': 5,          # 结束页码
    'max_retries': 3,       # 最大重试次数
    'timeout': 30,          # 请求超时时间
    'min_delay': 1,         # 最小延迟时间
    'max_delay': 3,         # 最大延迟时间
    'page_delay_min': 3,    # 页面间最小延迟
    'page_delay_max': 6     # 页面间最大延迟
}
```

## 使用方法

### 运行基础版爬虫
```bash
python mohrss_crawler.py
```

### 运行增强版爬虫（推荐）
```bash
python mohrss_crawler_enhanced.py
```

### 运行原始页面爬虫
```bash
python mohrss_raw_crawler.py
```

### 自定义爬取范围
```python
from mohrss_crawler_enhanced import MOHRSSCrawlerEnhanced

# 创建爬虫实例
crawler = MOHRSSCrawlerEnhanced()

# 爬取指定页面范围
results = crawler.run(start_page=1, end_page=10)
```

## 输出文件说明

### Excel文件结构
- **搜索结果工作表**: 包含所有爬取到的数据
  - title: 标题
  - link: 链接
  - publish_date: 发布时间
  - summary: 摘要
  - page_num: 页码
  - crawl_time: 爬取时间
  - source: 数据来源

- **统计信息工作表**: 包含基本统计信息
  - 总记录数
  - 爬取时间
  - 数据来源
  - 错误次数

### 分析结果文件结构
- **基本统计工作表**: 详细的数据统计
- **页面统计工作表**: 按页面统计记录数
- **标题长度分析工作表**: 标题长度分布
- **内容摘要工作表**: 标题、发布时间、摘要汇总

### JSON文件
包含完整的爬取数据，便于程序化处理。

### 日志文件
记录详细的运行过程，包括：
- 请求成功/失败信息
- 数据解析过程
- 错误信息和堆栈跟踪
- 统计信息

### 原始页面文件
- **HTML文件**: `results/mohrss_raw_page_*.html`
  - 完整的原始页面HTML内容
  - 按页码和时间戳命名
  - 便于后续分析和处理

## 配置说明

### 网站配置
```python
WEBSITE_CONFIG = {
    'base_url': 'https://www.mohrss.gov.cn',
    'search_url': '/was5/web/search',
    'channel_id': '203464',
    'order_by': 'date',
    'default': 'isall'
}
```

### 请求头配置
包含完整的浏览器请求头信息，模拟真实用户访问。

### Cookies配置
包含必要的会话信息，确保请求成功。

### 解析配置
```python
PARSER_CONFIG = {
    'search_result_selectors': [
        'div.search-result-item',
        'li.search-item',
        'div.result-item'
    ],
    'title_selectors': ['a', 'h3', 'div.title'],
    'date_selectors': ['span.date', 'div.date', 'time'],
    'summary_selectors': ['div.summary', 'p.summary', 'div.content']
}
```

## 错误处理

### 自动重试机制
- 网络请求失败时自动重试
- 可配置最大重试次数
- 重试间隔随机化

### 连续错误检测
- 检测连续错误次数
- 达到阈值时自动停止
- 防止无限重试

### 错误日志记录
- 详细记录错误信息
- 包含错误堆栈跟踪
- 便于问题排查

## 性能优化

### 请求优化
- 使用Session保持连接
- 随机延迟避免被封
- 合理的超时设置

### 内存优化
- 及时释放不需要的数据
- 分批处理大量数据
- 避免内存泄漏

### 并发控制
- 单线程设计确保稳定性
- 合理的请求间隔
- 避免对服务器造成压力

## 注意事项

### 使用规范
1. 遵守网站的robots.txt规则
2. 合理设置爬取频率
3. 不要过度频繁地访问
4. 尊重网站的使用条款

### 数据使用
1. 爬取的数据仅供学习和研究使用
2. 不得用于商业用途
3. 遵守相关法律法规
4. 注意数据版权问题

### 技术限制
1. 网站结构可能发生变化
2. 需要定期更新选择器
3. 反爬虫机制可能升级
4. 网络环境可能影响稳定性

## 故障排除

### 常见问题

1. **请求失败**
   - 检查网络连接
   - 验证URL是否正确
   - 检查请求头配置

2. **数据解析失败**
   - 检查页面结构是否变化
   - 更新CSS选择器
   - 查看原始HTML内容

3. **文件保存失败**
   - 检查目录权限
   - 确保磁盘空间充足
   - 验证文件路径

### 调试方法

1. **查看日志文件**
   - 检查详细的错误信息
   - 分析请求过程
   - 定位问题原因

2. **保存原始页面**
   - 查看实际页面内容
   - 分析页面结构
   - 调整解析策略

3. **逐步测试**
   - 先爬取单页测试
   - 逐步增加页面数
   - 验证功能正常

## 更新日志

### v1.0.0 (2025-08-18)
- 初始版本发布
- 基础爬取功能
- 数据保存功能
- 日志记录功能

### v1.1.0 (2025-08-18)
- 增强版发布
- 配置文件支持
- 改进错误处理
- 增强数据分析

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址：GitHub仓库
- 邮箱：your-email@example.com

## 许可证

本项目采用MIT许可证，详见LICENSE文件。
