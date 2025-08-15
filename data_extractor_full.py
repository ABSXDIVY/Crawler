#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发改委政策数据提取模块 - 完整版本
从HTML页面中提取政策列表、正文内容、附件信息和解读信息
保存到Excel文件的四个工作表中
"""

import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
import requests
import time
from urllib.parse import urljoin
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class PolicyDataExtractor:
    """政策数据提取器 - 完整版本"""
    
    def __init__(self, test_mode=False, max_test_items=10):
        """初始化提取器"""
        self.policies_data = []  # 政策列表数据
        self.interpretations_data = []  # 解读数据
        self.content_data = []  # 正文内容数据
        self.attachments_data = []  # 附件数据
        self.base_url = 'https://www.ndrc.gov.cn'  # 基础域名
        
        # 测试模式设置
        self.test_mode = test_mode
        self.max_test_items = max_test_items
        self.processed_count = 0
        
        # 创建requests会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        logging.info("政策数据提取器初始化完成")
    
    def get_page_content(self, url, retries=3):
        """获取页面内容"""
        for attempt in range(retries):
            try:
                logging.info(f"正在获取页面内容: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                response.encoding = 'utf-8'
                logging.info(f"成功获取页面: {response.status_code}")
                return response.text
            except Exception as e:
                logging.warning(f"获取页面失败 (尝试 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    logging.error(f"最终获取失败: {url}")
                    return None
    
    def extract_policy_info(self, html_content, category_name, page_num):
        """从HTML中提取政策信息"""
        if not html_content:
            return
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有政策列表项
        policy_items = soup.find_all('li')
        
        for item in policy_items:
            # 测试模式检查
            if self.test_mode and self.processed_count >= self.max_test_items:
                logging.info(f"测试模式：已达到最大处理数量 {self.max_test_items}")
                return
            
            try:
                # 查找政策链接
                policy_link = item.find('a', href=True)
                if not policy_link:
                    continue
                
                # 检查是否是政策链接（包含日期信息）
                date_span = item.find('span')
                if not date_span:
                    continue
                
                # 提取政策标题
                title = policy_link.get('title', '').strip()
                if not title:
                    title = policy_link.get_text(strip=True)
                
                # 提取链接并转换为完整URL
                href = policy_link.get('href', '')
                if href.startswith('./'):
                    href = href[2:]  # 移除开头的 ./
                
                # 构建完整URL
                full_url = self.build_full_url(href, category_name)
                
                # 提取发布日期
                publish_date = date_span.get_text(strip=True) if date_span else ''
                
                # 提取文号（从标题中提取）
                document_number = self.extract_document_number(title)
                
                # 检查是否有解读
                has_interpretation = self.check_has_interpretation(item)
                
                # 提取解读信息
                interpretations = self.extract_interpretations(item, href)
                
                # 获取政策详情页面的正文内容和附件信息
                content_info = self.extract_policy_detail(full_url, title)
                
                # 添加到政策数据
                policy_data = {
                    '政策分类': category_name,
                    '页码': page_num,
                    '政策标题': title,
                    '文号': document_number,
                    '发布日期': publish_date,
                    '政策链接': full_url,
                    '是否有解读': has_interpretation,
                    '解读数量': len(interpretations)
                }
                
                self.policies_data.append(policy_data)
                
                # 添加正文内容数据
                if content_info.get('content'):
                    content_data = {
                        '政策分类': category_name,
                        '政策标题': title,
                        '文号': document_number,
                        '发布日期': publish_date,
                        '政策链接': full_url,
                        '正文内容': content_info['content']
                    }
                    self.content_data.append(content_data)
                
                # 添加附件数据
                if content_info.get('attachments') or content_info.get('attachment_links'):
                    attachment_data = {
                        '政策分类': category_name,
                        '政策标题': title,
                        '文号': document_number,
                        '发布日期': publish_date,
                        '政策链接': full_url,
                        '附件信息': content_info.get('attachments', ''),
                        '附件链接': content_info.get('attachment_links', '')
                    }
                    self.attachments_data.append(attachment_data)
                
                # 添加解读数据
                for interpretation in interpretations:
                    interpretation_data = {
                        '政策分类': category_name,
                        '政策标题': title,
                        '政策日期': publish_date,
                        '政策链接': full_url,
                        '解读标题': interpretation['title'],
                        '解读链接': interpretation['full_url']
                    }
                    self.interpretations_data.append(interpretation_data)
                
                # 增加处理计数
                self.processed_count += 1
                
                logging.info(f"已处理政策: {title}")
                
                # 添加延迟，避免请求过于频繁
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"提取政策信息时出错: {e}")
                continue
    
    def extract_policy_detail(self, url, title):
        """提取政策详情页面的正文内容和附件信息"""
        try:
            html_content = self.get_page_content(url)
            if not html_content:
                return {'content': '', 'attachments': '', 'attachment_links': ''}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取正文内容
            content = self.extract_content(soup)
            
            # 提取附件信息
            attachments_info = self.extract_attachments(soup, url)
            
            return {
                'content': content,
                'attachments': attachments_info['attachments'],
                'attachment_links': attachments_info['links']
            }
            
        except Exception as e:
            logging.error(f"提取政策详情时出错: {e}")
            return {'content': '', 'attachments': '', 'attachment_links': ''}
    
    def extract_content(self, soup):
        """提取正文内容"""
        try:
            # 优先查找特定的文章内容容器
            content_element = soup.find('div', class_='article_con')
            
            if not content_element:
                # 如果找不到特定容器，尝试其他选择器
                content_selectors = [
                    '.TRS_Editor',  # 发改委网站常用的编辑器容器
                    '.content', '.article-content', '.main-content',
                    '.policy-content', '.document-content', '.text-content',
                    '.article', '.text', '.main'
                ]
                
                for selector in content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        break
            
            if content_element:
                # 清理内容
                content_text = self.clean_content(content_element.get_text())
                # 限制内容长度，避免Excel单元格过大
                return content_text[:15000] if len(content_text) > 15000 else content_text
            
            return ''
            
        except Exception as e:
            logging.error(f"提取正文内容时出错: {e}")
            return ''
    
    def extract_attachments(self, soup, base_url):
        """提取附件信息"""
        try:
            attachments = []
            attachment_links = []
            
            # 查找附件链接 - 支持多种文件格式
            attachment_selectors = [
                'a[href*=".pdf"]',
                'a[href*=".doc"]',
                'a[href*=".docx"]',
                'a[href*=".ofd"]',
                'a[href*=".xls"]',
                'a[href*=".xlsx"]',
                'a[href*=".zip"]',
                'a[href*=".rar"]'
            ]
            
            for selector in attachment_selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    if href:
                        # 构建完整链接
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(base_url, href)
                        
                        attachments.append(text if text else href)
                        attachment_links.append(full_url)
            
            return {
                'attachments': '; '.join(attachments),
                'links': '; '.join(attachment_links)
            }
            
        except Exception as e:
            logging.error(f"提取附件信息时出错: {e}")
            return {'attachments': '', 'links': ''}
    
    def clean_content(self, text):
        """清理文本内容"""
        if not text:
            return ''
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        # 移除特殊字符
        text = re.sub(r'[\r\n\t]+', '\n', text)
        return text
    
    def build_full_url(self, href, category_name):
        """构建完整的URL，包含正确的目录路径"""
        # 根据分类确定基础路径
        category_paths = {
            '发展改革委令': '/xxgk/zcfb/fzggwl',
            '规范性文件': '/xxgk/zcfb/ghxwj',
            '规划文本': '/xxgk/zcfb/ghwb',
            '公告': '/xxgk/zcfb/gg',
            '通知': '/xxgk/zcfb/tz'
        }
        
        base_path = category_paths.get(category_name, '')
        if base_path and not href.startswith('http'):
            # 构建完整URL
            full_url = f"{self.base_url}{base_path}/{href}"
        else:
            # 如果已经是完整URL或无法确定路径，直接拼接
            full_url = urljoin(self.base_url, href)
        
        return full_url
    
    def check_has_interpretation(self, item):
        """检查是否有解读信息"""
        # 多种方式检查解读标识
        indicators = [
            item.find('img', src='/images/jiedu.png'),
            item.find('img', src=lambda x: x and 'jiedu' in x),
            item.find('div', class_='popbox'),
            item.find('strong', recursive=True),  # 解读图标通常被strong标签包围
        ]
        
        return any(indicators)
    
    def extract_document_number(self, title):
        """从标题中提取文号"""
        # 匹配常见的文号格式
        patterns = [
            r'第(\d+)号令',
            r'第(\d+)号',
            r'(\d+)号令',
            r'(\d+)号'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return match.group(0)
        
        return ''
    
    def extract_interpretations(self, item, policy_url):
        """提取解读信息"""
        interpretations = []
        
        try:
            # 查找解读弹窗 - 多种方式查找
            popbox = item.find('div', class_='popbox')
            
            # 如果找不到popbox，尝试其他方式查找解读信息
            if not popbox:
                # 查找解读图标周围的解读链接
                interpretation_indicators = [
                    item.find('img', src='/images/jiedu.png'),
                    item.find('img', src=lambda x: x and 'jiedu' in x),
                    item.find('strong', recursive=True)
                ]
                
                for indicator in interpretation_indicators:
                    if indicator:
                        # 在解读图标附近查找链接
                        nearby_links = indicator.find_next_siblings('a', href=True)
                        if not nearby_links:
                            nearby_links = indicator.parent.find_all('a', href=True)
                        
                        for link in nearby_links:
                            title = link.get('title', '').strip()
                            if not title:
                                title = link.get_text(strip=True)
                            
                            href = link.get('href', '')
                            if href.startswith('../../'):
                                href = href[6:]  # 移除开头的 ../../
                            
                            # 构建完整URL - 解读链接通常指向jd目录
                            if href.startswith('jd/'):
                                full_url = f"{self.base_url}/xxgk/{href}"
                            else:
                                full_url = urljoin(self.base_url, href)
                            
                            interpretations.append({
                                'title': title,
                                'url': href,
                                'full_url': full_url
                            })
                        break
            else:
                # 查找解读列表
                interpretation_links = popbox.find_all('a', href=True)
                
                for link in interpretation_links:
                    title = link.get('title', '').strip()
                    if not title:
                        title = link.get_text(strip=True)
                    
                    href = link.get('href', '')
                    if href.startswith('../../'):
                        href = href[6:]  # 移除开头的 ../../
                    
                    # 构建完整URL - 解读链接通常指向jd目录
                    if href.startswith('jd/'):
                        full_url = f"{self.base_url}/xxgk/{href}"
                    else:
                        full_url = urljoin(self.base_url, href)
                    
                    interpretations.append({
                        'title': title,
                        'url': href,
                        'full_url': full_url
                    })
                
        except Exception as e:
            logging.error(f"提取解读信息时出错: {e}")
        
        return interpretations
    
    def save_to_excel(self, output_file):
        """保存数据到Excel文件 - 四个工作表"""
        try:
            logging.info("开始保存数据到Excel文件")
            
            # 创建Excel写入器
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # 定义目录处理顺序
                category_order = ['发展改革委令', '规范性文件', '规划文本', '公告', '通知']
                
                # ===== Sheet1: 政策列表 =====
                if self.policies_data:
                    policies_df = pd.DataFrame(self.policies_data)
                    
                    # 按照目录和页面顺序排序
                    policies_df['category_order'] = policies_df['政策分类'].map(lambda x: category_order.index(x) if x in category_order else 999)
                    policies_df = policies_df.sort_values(['category_order', '页码', '发布日期'], ascending=[True, True, False])
                    policies_df = policies_df.drop('category_order', axis=1)
                    
                    # 重新排列列顺序
                    column_order = [
                        '政策分类', '页码', '政策标题', '文号', 
                        '发布日期', '政策链接', '是否有解读', '解读数量'
                    ]
                    existing_columns = [col for col in column_order if col in policies_df.columns]
                    policies_df = policies_df[existing_columns]
                    
                    policies_df.to_excel(writer, sheet_name='政策列表', index=False)
                    logging.info(f"✅ Sheet1 - 政策列表: 已保存{len(self.policies_data)}条记录")
                
                # ===== Sheet2: 政策正文 =====
                if self.content_data:
                    content_df = pd.DataFrame(self.content_data)
                    
                    # 按照目录和页面顺序排序
                    content_df['category_order'] = content_df['政策分类'].map(lambda x: category_order.index(x) if x in category_order else 999)
                    content_df = content_df.sort_values(['category_order', '发布日期'], ascending=[True, False])
                    content_df = content_df.drop('category_order', axis=1)
                    
                    # 重新排列列顺序
                    column_order = [
                        '政策分类', '政策标题', '文号', '发布日期', 
                        '政策链接', '正文内容'
                    ]
                    existing_columns = [col for col in column_order if col in content_df.columns]
                    content_df = content_df[existing_columns]
                    
                    content_df.to_excel(writer, sheet_name='政策正文', index=False)
                    logging.info(f"✅ Sheet2 - 政策正文: 已保存{len(self.content_data)}条记录")
                
                # ===== Sheet3: 政策附件 =====
                if self.attachments_data:
                    # 处理附件数据，将不同类型的附件分开
                    processed_attachments = []
                    
                    for attachment_data in self.attachments_data:
                        attachments = attachment_data.get('附件信息', '').split('; ')
                        attachment_links = attachment_data.get('附件链接', '').split('; ')
                        
                        # 按文件类型分类
                        file_types = {
                            'PDF': {'attachments': [], 'links': []},
                            'OFD': {'attachments': [], 'links': []},
                            'Word': {'attachments': [], 'links': []},
                            'Excel': {'attachments': [], 'links': []},
                            '其他': {'attachments': [], 'links': []}
                        }
                        
                        for i, (attachment, link) in enumerate(zip(attachments, attachment_links)):
                            if attachment and link:
                                link_lower = link.lower()
                                if link_lower.endswith('.pdf'):
                                    file_types['PDF']['attachments'].append(attachment)
                                    file_types['PDF']['links'].append(link)
                                elif link_lower.endswith('.ofd'):
                                    file_types['OFD']['attachments'].append(attachment)
                                    file_types['OFD']['links'].append(link)
                                elif link_lower.endswith(('.doc', '.docx')):
                                    file_types['Word']['attachments'].append(attachment)
                                    file_types['Word']['links'].append(link)
                                elif link_lower.endswith(('.xls', '.xlsx')):
                                    file_types['Excel']['attachments'].append(attachment)
                                    file_types['Excel']['links'].append(link)
                                else:
                                    file_types['其他']['attachments'].append(attachment)
                                    file_types['其他']['links'].append(link)
                        
                        # 为每个附件类型创建一行记录
                        for file_type, data in file_types.items():
                            if data['attachments']:
                                processed_attachments.append({
                                    '政策分类': attachment_data['政策分类'],
                                    '政策标题': attachment_data['政策标题'],
                                    '文号': attachment_data['文号'],
                                    '发布日期': attachment_data['发布日期'],
                                    '政策链接': attachment_data['政策链接'],
                                    '附件类型': file_type,
                                    '附件名称': '\n'.join(data['attachments']),
                                    '附件链接': '\n'.join(data['links'])
                                })
                    
                    if processed_attachments:
                        attachments_df = pd.DataFrame(processed_attachments)
                        
                        # 按照目录和页面顺序排序
                        attachments_df['category_order'] = attachments_df['政策分类'].map(lambda x: category_order.index(x) if x in category_order else 999)
                        attachments_df = attachments_df.sort_values(['category_order', '发布日期'], ascending=[True, False])
                        attachments_df = attachments_df.drop('category_order', axis=1)
                        
                        # 重新排列列顺序
                        column_order = [
                            '政策分类', '政策标题', '文号', '发布日期', 
                            '政策链接', '附件类型', '附件名称', '附件链接'
                        ]
                        existing_columns = [col for col in column_order if col in attachments_df.columns]
                        attachments_df = attachments_df[existing_columns]
                        
                        attachments_df.to_excel(writer, sheet_name='政策附件', index=False)
                        logging.info(f"✅ Sheet3 - 政策附件: 已保存{len(processed_attachments)}条记录")
                
                # ===== Sheet4: 政策解读 =====
                if self.interpretations_data:
                    # 直接使用原始解读数据，每个解读单独一行
                    interpretations_df = pd.DataFrame(self.interpretations_data)
                    
                    # 按照目录和页面顺序排序
                    interpretations_df['category_order'] = interpretations_df['政策分类'].map(lambda x: category_order.index(x) if x in category_order else 999)
                    interpretations_df = interpretations_df.sort_values(['category_order', '政策日期'], ascending=[True, False])
                    interpretations_df = interpretations_df.drop('category_order', axis=1)
                    
                    # 重新排列列顺序
                    column_order = [
                        '政策分类', '政策标题', '政策日期', '政策链接',
                        '解读标题', '解读链接'
                    ]
                    existing_columns = [col for col in column_order if col in interpretations_df.columns]
                    interpretations_df = interpretations_df[existing_columns]
                    
                    interpretations_df.to_excel(writer, sheet_name='政策解读', index=False)
                    logging.info(f"✅ Sheet4 - 政策解读: 已保存{len(self.interpretations_data)}条记录")
            
            logging.info(f"🎉 数据已成功保存到: {output_file}")
            
        except Exception as e:
            logging.error(f"保存Excel文件时出错: {e}")
            raise
    
    def get_statistics(self):
        """获取数据统计信息"""
        stats = {
            'total_policies': len(self.policies_data),
            'total_interpretations': len(self.interpretations_data),
            'total_contents': len(self.content_data),
            'total_attachments': len(self.attachments_data),
            'policies_with_interpretations': len([p for p in self.policies_data if p['是否有解读']]),
            'categories': list(set([p['政策分类'] for p in self.policies_data]))
        }
        
        return stats

def process_html_files(html_dir, output_file, test_mode=False, max_test_items=10):
    """处理HTML文件并提取数据"""
    logging.info("开始处理HTML文件")
    
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    extractor = PolicyDataExtractor(test_mode=test_mode, max_test_items=max_test_items)
    
    # 定义目录处理顺序
    category_order = ['发展改革委令', '规范性文件', '规划文本', '公告', '通知']
    
    # 按照指定顺序处理目录
    for category_name in category_order:
        category_path = os.path.join(html_dir, category_name)
        
        if not os.path.exists(category_path):
            logging.warning(f"目录不存在: {category_name}")
            continue
        
        logging.info(f"📁 处理分类: {category_name}")
        
        # 获取该分类下的所有HTML文件
        html_files = []
        for filename in os.listdir(category_path):
            if not filename.endswith('.html'):
                continue
            
            # 从文件名中提取页码 - 支持多种格式
            page_match = re.search(r'page_(\d+)', filename)
            if not page_match:
                continue
            
            page_num = int(page_match.group(1))
            file_path = os.path.join(category_path, filename)
            html_files.append((page_num, file_path, filename))
        
        # 按照页码排序
        html_files.sort(key=lambda x: x[0])
        
        logging.info(f"找到 {len(html_files)} 个HTML文件")
        
        # 处理排序后的文件
        for page_num, file_path, filename in html_files:
            try:
                logging.info(f"处理文件: {filename}")
                
                # 读取HTML文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 提取数据
                extractor.extract_policy_info(html_content, category_name, page_num)
                
                # 测试模式检查
                if test_mode and extractor.processed_count >= max_test_items:
                    logging.info(f"测试模式：已达到最大处理数量 {max_test_items}")
                    break
                
            except Exception as e:
                logging.error(f"处理文件 {filename} 时出错: {e}")
        
        # 测试模式检查
        if test_mode and extractor.processed_count >= max_test_items:
            break
    
    # 保存数据到Excel
    extractor.save_to_excel(output_file)
    
    # 打印统计信息
    stats = extractor.get_statistics()
    logging.info("\n📊 数据提取统计:")
    logging.info(f"总政策数: {stats['total_policies']}")
    logging.info(f"总解读数: {stats['total_interpretations']}")
    logging.info(f"总正文数: {stats['total_contents']}")
    logging.info(f"总附件数: {stats['total_attachments']}")
    logging.info(f"有解读的政策数: {stats['policies_with_interpretations']}")
    logging.info(f"涉及分类: {', '.join(stats['categories'])}")
    
    return extractor

if __name__ == "__main__":
    # 完整模式：处理所有政策
    logging.info("🚀 启动数据提取器 - 完整模式")
    process_html_files('results', 'policy_data_full.xlsx', test_mode=False)
    
    # 测试模式：只处理前10个政策
    # logging.info("🚀 启动数据提取器 - 测试模式")
    # process_html_files('results', 'policy_data_test.xlsx', test_mode=True, max_test_items=10)
