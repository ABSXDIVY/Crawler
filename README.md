# NDRC政策文件爬虫系统

## 项目简介

NDRC政策文件爬虫系统是一个专门用于爬取和处理国家发改委（NDRC）官网政策文件的Python工具。该系统能够自动爬取发改委官网的政策文件，提取结构化数据，并进行智能分段处理，为AI增强的国家政策检索工具提供数据支持。

## 主要功能

### 🔍 数据爬取
- **多分类爬取**：支持爬取发改委官网的5个主要政策分类
  - 发展改革委令（最高级别政策文件）
  - 规范性文件（重要规范性政策文件）
  - 规划文本（发展规划类文件）
  - 公告（重要公告信息）
  - 通知（日常通知文件）
- **智能分页**：自动检测和处理分页内容
- **错误重试**：内置重试机制，确保数据完整性
- **日志记录**：详细的爬取日志，便于监控和调试

### 📊 数据提取
- **结构化提取**：从HTML页面中提取政策的关键信息
  - 政策标题、发布日期、文号
  - 政策分类、正文内容
  - 附件信息和解读信息
- **多工作表输出**：将数据保存到Excel文件的多个工作表中
- **数据清洗**：自动清理和格式化提取的数据

### ✂️ 内容处理
- **智能分段**：将长文本内容按语义智能分段，确保每段不超过1000字符
- **附件拆解**：自动识别和拆解包含多个附件的记录
- **文件类型识别**：根据URL后缀自动识别文件类型

### 📁 文件管理
- **附件下载**：支持下载政策相关的附件文件
- **目录组织**：按分类自动组织文件结构
- **数据备份**：完整的原始数据备份

## 项目结构

```
ndrc_crawler/
├── README.md                    # 项目说明文档
├── LICENSE                      # 开源许可证
├── .gitignore                   # Git忽略文件
├── config.py                    # 配置文件
├── ndrc_crawler.py              # 主爬虫程序
├── data_extractor_full.py       # 数据提取器（完整版）
├── content_splitter.py          # 内容分段器
├── attachment_splitter.py       # 附件拆解器
├── download_attachments.py      # 附件下载器
├── results/                     # 爬取结果目录
│   ├── 发展改革委令/
│   ├── 规范性文件/
│   ├── 规划文本/
│   ├── 公告/
│   └── 通知/
├── logs/                        # 日志文件目录
├── full_data/                   # 完整数据目录（已忽略）
└── *.xlsx                       # 数据输出文件
```

## 安装和使用

### 环境要求

- Python 3.7+
- Windows/Linux/macOS

### 依赖安装

```bash
pip install requests
pip install beautifulsoup4
pip install pandas
pip install openpyxl
pip install urllib3
```

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/ABSXDIVY/ndrc_crawler.git
cd ndrc_crawler
```

2. **配置参数**
编辑 `config.py` 文件，根据需要调整爬取参数：
- 修改爬取页数限制
- 调整请求延迟时间
- 配置测试模式

3. **运行爬虫**
```bash
python ndrc_crawler.py
```

4. **提取数据**
```bash
python data_extractor_full.py
```

5. **处理内容**
```bash
python content_splitter.py
python attachment_splitter.py
```

## 配置说明

### 爬取配置 (config.py)

```python
# 政策分类配置
POLICY_CATEGORIES = {
    '发展改革委令': {
        'name': '发展改革委令',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl',
        'enabled': True
    },
    # ... 其他分类
}

# 爬取控制参数
CRAWL_CONFIG = {
    'max_pages_per_category': None,  # 每分类最大页数
    'delay_between_pages': 1,        # 页面间延迟
    'delay_between_extractions': 0.5 # 提取间延迟
}
```

### 输出文件说明

- `policy_data.xlsx` - 基础政策数据
- `policy_data_full.xlsx` - 完整政策数据（包含正文和附件）
- `policy_content_split.xlsx` - 分段后的政策内容
- `policy_attachments_split.xlsx` - 拆解后的附件信息

## 使用示例

### 基础爬取
```python
from ndrc_crawler import NDRCCrawler

crawler = NDRCCrawler()
crawler.crawl_all_categories()
```

### 数据提取
```python
from data_extractor_full import PolicyDataExtractor

extractor = PolicyDataExtractor(test_mode=True, max_test_items=10)
extractor.process_all_results()
```

### 内容分段
```python
from content_splitter import ContentSplitter

splitter = ContentSplitter(max_chars=1000)
splitter.process_excel_file('policy_data_full.xlsx')
```

## 注意事项

1. **遵守网站规则**：请合理控制爬取频率，避免对目标网站造成过大压力
2. **数据使用**：爬取的数据仅供学习和研究使用，请遵守相关法律法规
3. **网络环境**：确保网络连接稳定，建议在稳定的网络环境下运行
4. **存储空间**：爬取的数据量较大，请确保有足够的存储空间

## 故障排除

### 常见问题

1. **网络连接失败**
   - 检查网络连接
   - 确认目标网站可访问
   - 调整超时设置

2. **数据提取失败**
   - 检查HTML结构是否变化
   - 查看日志文件获取详细错误信息
   - 更新提取规则

3. **内存不足**
   - 减少并发处理数量
   - 分批处理大文件
   - 增加系统内存

### 日志查看

所有操作日志保存在 `logs/` 目录下：
- `ndrc_crawler_YYYYMMDD.log` - 爬虫日志
- `data_extractor.log` - 数据提取日志
- `content_splitter.log` - 内容分段日志
- `attachment_splitter.log` - 附件拆解日志

## 开发计划

- [ ] 支持更多政策来源网站
- [ ] 添加数据可视化功能
- [ ] 实现增量更新机制
- [ ] 优化爬取性能
- [ ] 添加Web界面

## 贡献指南

欢迎提交Issue和Pull Request来改进项目！

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**免责声明**：本项目仅供学习和研究使用，使用者需自行承担使用风险，并遵守相关法律法规。
