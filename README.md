# 政府政策文件爬虫系统

## 项目简介

这是一个专门用于爬取中国政府网站政策文件的Python爬虫系统。系统包含两个主要模块：

- **人力资源和社会保障部爬虫** (`mohrss_crawler/`) - 爬取人社部政策文件
- **发改委爬虫** (`ndrc_crawler/`) - 爬取发改委政策文件

系统采用模块化设计，具备完整的日志记录、错误处理、数据分析和结果保存功能，为政策研究和数据分析提供可靠的数据源。

## 🚀 主要功能

### 核心爬取功能
- **多网站支持**：支持人社部、发改委和广州市人社局三个重要政府网站
- **智能分页**：自动检测和处理分页内容
- **错误重试**：内置重试机制，确保数据完整性
- **并发控制**：合理的请求间隔，避免对服务器造成压力

### AI智能功能
- **智能体API集成**：支持AI智能体API，提供智能对话和搜索功能
- **智能搜索**：基于AI的语义搜索，更准确地匹配用户需求
- **Web界面**：提供现代化的Web界面，支持AI搜索和结果展示
- **智能链接渲染**：自动识别并渲染可点击的链接，提升用户体验
- **配置管理**：灵活的配置管理，支持多种API配置方式

### 数据处理功能
- **结构化提取**：从HTML页面中提取政策的关键信息
- **智能分段**：将长文本内容按语义智能分段
- **附件处理**：支持下载和处理政策相关附件
- **数据清洗**：自动清理和格式化提取的数据

### 输出格式
- **Excel格式**：多工作表结构，便于数据分析
- **JSON格式**：便于程序化处理
- **原始HTML**：保存完整页面内容
- **统计报告**：自动生成数据统计和分析报告
- **双格式并行**：同时生成Excel和JSON文件，满足不同需求

## 📁 项目结构

```
Crawler/
├── README.md                    # 项目说明文档
├── LICENSE                      # 开源许可证
├── requirements.txt             # 依赖包列表
├── .cursorrules                 # AI配置文件
├── mohrss_crawler/              # 人社部爬虫模块
│   ├── README.md               # 人社部爬虫说明
│   ├── config.py               # 配置文件
│   ├── mohrss_crawler.py       # 基础爬虫程序
│   ├── mohrss_raw_crawler.py   # 原始页面爬虫
│   ├── mohrss_detailed_parser.py # 详细解析器
│   ├── simple_download.py      # 简单下载器
│   ├── results/                # 结果文件目录
│   ├── logs/                   # 日志文件目录
│   ├── downloads/              # 下载文件目录
│   └── parsed_content/         # 解析内容目录
├── ndrc_crawler/               # 发改委爬虫模块
│   ├── README.md               # 发改委爬虫说明
│   ├── config.py               # 配置文件
│   ├── ndrc_crawler.py         # 主爬虫程序
│   ├── data_extractor_full.py  # 数据提取器
│   ├── content_splitter.py     # 内容分段器
│   ├── attachment_splitter.py  # 附件拆解器
│   ├── download_attachments.py # 附件下载器
│   ├── commit_changes.py       # Git提交助手
│   ├── run.py                  # 一键启动脚本
│   ├── setup.py                # 安装脚本
│   ├── results/                # 结果文件目录
│   ├── logs/                   # 日志文件目录
│   └── full_data/              # 完整数据目录
└── gz_rsj_crawler/             # 广州市人社局爬虫模块
    ├── README.md               # 模块说明文档
    ├── config.py               # 配置文件
    ├── url_content_parser.py   # URL内容解析器
    ├── excel_writer.py         # Excel写入模块
    ├── log_config.py           # 日志配置
    ├── requirements.txt        # 依赖包
    ├── results/                # 结果文件目录
    ├── logs/                   # 日志文件目录
    └── input/                  # 输入文件目录
```

## 🛠️ 安装和配置

### 环境要求
- Python 3.7+
- 稳定的网络连接
- 足够的存储空间（建议至少2GB）

### 安装依赖
```bash
# 克隆项目
git clone <repository-url>
cd Crawler

# 安装依赖包
pip install -r requirements.txt
```

## 🖥️ 桌面应用程序

项目还提供了基于Electron的桌面应用程序，将网页功能打包成独立的可执行文件。

### 桌面应用特性
- **跨平台支持**: Windows、macOS、Linux
- **自动服务器管理**: 应用启动时自动启动Python代理服务器
- **原生体验**: 提供桌面应用的原生体验
- **一键启动**: 无需手动配置环境

### 快速开始

#### 方法一：使用启动脚本（推荐）
```bash
# Windows
cd web_interface
start.bat

# Linux/macOS
cd web_interface
chmod +x start.sh
./start.sh
```

#### 方法二：手动构建
```bash
# 进入web_interface目录
cd web_interface

# 安装依赖
npm install
pip install -r requirements.txt

# 开发模式运行
npm start

# 构建应用
npm run build-win    # Windows
npm run build-mac    # macOS
npm run build-linux  # Linux
```

#### 方法三：自动化构建
```bash
# 使用构建脚本
node build.js

# 指定平台构建
node build.js win    # Windows
node build.js mac    # macOS
node build.js linux  # Linux
```

### 桌面应用文件结构
```
web_interface/
├── package.json          # Electron应用配置
├── main.js              # 主进程文件
├── preload.js           # 预加载脚本
├── index.html           # 主界面
├── app.js               # 前端逻辑
├── style.css            # 样式文件
├── start_server.py      # Python代理服务器
├── requirements.txt     # Python依赖
├── build.js             # 构建脚本
├── start.bat            # Windows启动脚本
├── start.sh             # Linux/macOS启动脚本
└── README_APP.md        # 应用详细说明
```

详细说明请参考：[桌面应用说明](web_interface/README_APP.md)

### AI智能体API配置

项目集成了AI智能体API功能，支持智能搜索和对话。配置方法如下：

#### 方法一：使用配置文件（推荐）
1. 编辑 `api_config.env` 文件，设置您的API配置：
```bash
BASE_URL=http://localhost:8080/chat/api
API_KEY=application-ad6838518159e632447b68bfc3cbdf6a
PROFILE_ID=0198ac57-bf0e-7e61-bb66-56f7787966a8
```

2. 运行配置加载器：
```bash
python load_api_config.py
```

#### 方法二：直接设置环境变量
```bash
# Windows PowerShell
$env:BASE_URL="http://localhost:8080/chat/api"
$env:API_KEY="application-ad6838518159e632447b68bfc3cbdf6a"
$env:PROFILE_ID="0198ac57-bf0e-7e61-bb66-56f7787966a8"

# Linux/Mac
export BASE_URL="http://localhost:8080/chat/api"
export API_KEY="application-ad6838518159e632447b68bfc3cbdf6a"
export PROFILE_ID="0198ac57-bf0e-7e61-bb66-56f7787966a8"
```

#### 方法三：命令行参数
```bash
python api_test.py \
  --base-url http://localhost:8080/chat/api \
  --api-key application-ad6838518159e632447b68bfc3cbdf6a \
  --profile-id 0198ac57-bf0e-7e61-bb66-56f7787966a8 \
  --message "你好"
```

### 快速开始

#### 1. 运行人社部爬虫
```bash
cd mohrss_crawler
python mohrss_crawler.py
```

#### 2. 运行发改委爬虫
```bash
cd ndrc_crawler
python run.py
```

#### 3. 运行广州市人社局爬虫
```bash
cd gz_rsj_crawler
python url_content_parser.py
```

#### 4. 启动Web界面（包含AI功能）
```bash
cd web_interface
python start_server.py
```
然后在浏览器中访问 `http://localhost:8000`

**Web界面功能特性：**
- **智能搜索**：支持自然语言搜索和AI对话
- **实时流式响应**：搜索结果实时显示，无需等待
- **可点击链接**：自动识别并渲染HTTP/HTTPS链接为可点击形式
- **复制功能**：一键复制搜索结果到剪贴板
- **响应式设计**：支持桌面和移动设备访问
- **调试日志**：提供详细的调试信息，便于问题排查

**链接功能说明：**
- 系统会自动识别文本中的HTTP和HTTPS链接
- 链接会在新标签页中打开，确保安全性
- 支持带查询参数和路径的复杂链接
- 链接样式与整体界面风格保持一致

#### 4. 测试AI智能体API
```bash
# 使用配置加载器（推荐）
python load_api_config.py

# 或直接运行测试
python api_test.py --message "你好"
```

## 📊 数据输出说明

### 人社部爬虫输出
- **Excel文件**：`mohrss_crawler_results_*.xlsx`
  - 搜索结果工作表：标题、链接、发布时间、摘要等
  - 统计信息工作表：基本统计信息
- **JSON文件**：`mohrss_crawler_results_*.json`
- **分析报告**：`mohrss_data_analysis_*.xlsx`

### 发改委爬虫输出
- **基础数据**：`policy_data.xlsx`
- **完整数据**：`policy_data_full.xlsx`
- **分段内容**：`policy_content_split.xlsx`
- **附件信息**：`policy_attachments_split.xlsx`

### 广州市人社局爬虫输出
- **Excel文件**：`gz_rsj_crawler_results_*.xlsx`
  - 多工作表结构：每个URL类型一个独立工作表
  - 完整内容提取：标题、发布日期、正文内容、附件信息
- **JSON文件**：`gz_rsj_crawler_results_*.json`
  - 结构化数据格式
  - 包含完整的元数据和内容信息

## ⚙️ 配置说明

### 人社部爬虫配置 (`mohrss_crawler/config.py`)
```python
CRAWL_CONFIG = {
    'start_page': 1,        # 开始页码
    'end_page': 5,          # 结束页码
    'max_retries': 3,       # 最大重试次数
    'timeout': 30,          # 请求超时时间
    'min_delay': 1,         # 最小延迟时间
    'max_delay': 3,         # 最大延迟时间
}
```

### 发改委爬虫配置 (`ndrc_crawler/config.py`)
```python
POLICY_CATEGORIES = {
    '发展改革委令': {
        'name': '发展改革委令',
        'base_url': 'https://www.ndrc.gov.cn/xxgk/zcfb/fzggwl',
        'enabled': True
    },
    # ... 其他分类
}

CRAWL_CONFIG = {
    'max_pages_per_category': None,  # 每分类最大页数
    'delay_between_pages': 1,        # 页面间延迟
    'delay_between_extractions': 0.5 # 提取间延迟
}
```

### 广州市人社局爬虫配置 (`gz_rsj_crawler/config.py`)
```python
CRAWL_CONFIG = {
    'max_retries': 3,               # 最大重试次数
    'timeout': 30,                  # 请求超时时间
    'delay_between_requests': 1,    # 请求间延迟
    'user_agent': 'Mozilla/5.0...', # 用户代理
}

EXCEL_CONFIG = {
    'output_dir': 'output',         # 输出目录
    'excel_filename': 'gz_rsj_crawler_results.xlsx', # Excel文件名
    'json_filename': 'gz_rsj_crawler_results.json',  # JSON文件名
}
```

## 🔧 高级用法

### 自定义爬取范围
```python
# 人社部爬虫
from mohrss_crawler.mohrss_crawler import MOHRSSCrawler
crawler = MOHRSSCrawler()
results = crawler.run(start_page=1, end_page=10)

# 发改委爬虫
from ndrc_crawler.ndrc_crawler import NDRCCrawler
crawler = NDRCCrawler()
crawler.crawl_all_categories()

# 广州市人社局爬虫
from gz_rsj_crawler.url_content_parser import URLContentParser
parser = URLContentParser()
results = parser.parse_urls_from_excel('input_urls.xlsx', sheet_name='505_规范性文件')
```

### 数据处理
```python
# 内容分段
from ndrc_crawler.content_splitter import ContentSplitter
splitter = ContentSplitter(max_chars=1000)
splitter.process_excel_file('policy_data_full.xlsx')

# 附件处理
from ndrc_crawler.attachment_splitter import AttachmentSplitter
splitter = AttachmentSplitter()
splitter.process_excel_file('policy_data_full.xlsx')
```

## 📝 日志和监控

### 日志文件位置
- 人社部爬虫：`mohrss_crawler/logs/`
- 发改委爬虫：`ndrc_crawler/logs/`
- 广州市人社局爬虫：`gz_rsj_crawler/logs/`

### 日志级别
- **INFO**：正常运行信息
- **WARNING**：警告信息
- **ERROR**：错误信息

### 监控要点
- 检查日志文件中的错误信息
- 监控爬取进度和成功率
- 关注网络连接状态
- 检查磁盘空间使用情况

## ⚠️ 注意事项

### 使用规范
1. **遵守网站规则**：请合理控制爬取频率，避免对目标网站造成过大压力
2. **数据使用**：爬取的数据仅供学习和研究使用，请遵守相关法律法规
3. **网络环境**：确保网络连接稳定，建议在稳定的网络环境下运行
4. **存储空间**：爬取的数据量较大，请确保有足够的存储空间

### 技术限制
1. **网站结构变化**：目标网站结构可能发生变化，需要定期更新选择器
2. **反爬虫机制**：网站可能升级反爬虫机制，需要相应调整
3. **网络稳定性**：网络环境可能影响爬取稳定性
4. **数据完整性**：建议定期验证数据完整性

## 🐛 故障排除

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

4. **文件保存失败**
   - 检查目录权限
   - 确保磁盘空间充足
   - 验证文件路径

### 调试方法
1. **查看日志文件**：检查详细的错误信息和运行过程
2. **保存原始页面**：查看实际页面内容，分析页面结构
3. **逐步测试**：先爬取单页测试，逐步增加页面数

## 🔄 更新日志

### v2.1.0 (2025-01-XX)
- 新增广州市人社局爬虫模块
- 支持从Excel读取URL批量处理
- 增强错误重试机制（504错误自动重试）
- 优化多工作表Excel输出格式

### v2.0.0 (2025-01-XX)
- 整合两个爬虫项目
- 统一项目结构和文档
- 优化配置管理
- 改进错误处理机制

### v1.1.0 (2025-08-18)
- 人社部爬虫增强版发布
- 发改委爬虫完整功能
- 配置文件支持
- 改进错误处理

### v1.0.0 (2025-08-18)
- 初始版本发布
- 基础爬取功能
- 数据保存功能
- 日志记录功能

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 贡献方式
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 开发规范
- 遵循PEP 8代码风格
- 添加适当的注释和文档
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用MIT许可证，详见[LICENSE](LICENSE)文件。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**免责声明**：本项目仅供学习和研究使用，使用者需自行承担使用风险，并遵守相关法律法规。请合理使用爬取的数据，尊重网站的使用条款和版权。
