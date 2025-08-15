#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
附件文件下载器 - 从full_data目录读取附件表格
将网页中的附件链接另存为文件，使用附件标题作为文件名
"""

import pandas as pd
import requests
import os
import logging
import time
from urllib.parse import urlparse, unquote
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/download_attachments.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AttachmentDownloader:
    """附件下载器 - 下载网页中的附件文件"""
    
    def __init__(self, excel_file='full_data/附件.xlsx', output_dir='full_data/附件文件'):
        self.excel_file = excel_file
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 下载统计
        self.download_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
    
    def clean_filename(self, filename):
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 限制文件名长度
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename
    
    def get_filename_from_attachment(self, attachment_name, attachment_link):
        """从附件名称和链接生成文件名"""
        try:
            # 优先使用附件名称
            if attachment_name and attachment_name.strip():
                # 确保有文件扩展名
                if '.' not in attachment_name:
                    # 从链接中提取扩展名
                    parsed_url = urlparse(attachment_link)
                    path = unquote(parsed_url.path)
                    if '.' in path:
                        ext = os.path.splitext(path)[1]
                        attachment_name += ext
                    else:
                        # 根据链接特征判断文件类型
                        if 'pdf' in attachment_link.lower():
                            attachment_name += '.pdf'
                        elif 'doc' in attachment_link.lower():
                            attachment_name += '.doc'
                        elif 'xls' in attachment_link.lower():
                            attachment_name += '.xls'
                        else:
                            attachment_name += '.pdf'  # 默认PDF
                
                return self.clean_filename(attachment_name)
            else:
                # 如果没有附件名称，从链接中提取
                parsed_url = urlparse(attachment_link)
                path = unquote(parsed_url.path)
                url_filename = os.path.basename(path)
                
                if url_filename and '.' in url_filename:
                    return self.clean_filename(url_filename)
                else:
                    return f"attachment_{int(time.time())}.pdf"
                    
        except Exception as e:
            logging.warning(f"生成文件名时出错: {e}")
            return f"attachment_{int(time.time())}.pdf"
    
    def download_file(self, url, filename, category_dir):
        """下载单个文件"""
        try:
            # 检查文件是否已存在
            file_path = os.path.join(category_dir, filename)
            if os.path.exists(file_path):
                logging.info(f"文件已存在，跳过: {filename}")
                self.download_stats['skipped'] += 1
                return True
            
            # 下载文件
            logging.info(f"正在下载: {filename}")
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # 检查内容类型，确保是文件而不是网页
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type and len(response.content) < 10000:
                logging.warning(f"可能是网页而不是文件: {filename}")
                # 继续下载，但记录警告
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logging.info(f"下载成功: {filename}")
            self.download_stats['success'] += 1
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"下载失败 {filename}: {e}")
            self.download_stats['failed'] += 1
            return False
        except Exception as e:
            logging.error(f"保存文件失败 {filename}: {e}")
            self.download_stats['failed'] += 1
            return False
    
    def process_attachments(self):
        """处理附件表格"""
        try:
            # 读取Excel文件
            logging.info(f"正在读取附件表格: {self.excel_file}")
            
            # 尝试读取Excel文件，自动检测sheet名称
            excel_data = pd.read_excel(self.excel_file, sheet_name=None)
            
            # 找到包含附件信息的sheet
            target_sheet = None
            for sheet_name, df in excel_data.items():
                # 检查是否包含附件相关列
                columns = df.columns.tolist()
                if any('附件' in col for col in columns) or any('链接' in col for col in columns):
                    target_sheet = sheet_name
                    break
            
            if target_sheet is None:
                # 如果没有找到合适的sheet，使用第一个
                target_sheet = list(excel_data.keys())[0]
            
            df = excel_data[target_sheet]
            logging.info(f"使用sheet: {target_sheet}")
            logging.info(f"找到 {len(df)} 个附件记录")
            logging.info(f"列名: {df.columns.tolist()}")
            
            # 查找附件链接列（应该是附件链接，不是政策链接）
            link_column = None
            for col in df.columns:
                if '附件链接' in col:
                    link_column = col
                    break
            
            if link_column is None:
                # 如果没有找到附件链接列，查找包含链接的列
                for col in df.columns:
                    if '链接' in col and '政策' not in col:
                        link_column = col
                        break
            
            if link_column is None:
                logging.error("找不到附件链接列")
                return
            
            # 查找其他相关列
            title_column = None
            category_column = None
            name_column = None
            
            for col in df.columns:
                if '附件名称' in col:
                    name_column = col
                elif '政策标题' in col:
                    title_column = col
                elif '政策分类' in col:
                    category_column = col
            
            logging.info(f"附件链接列: {link_column}")
            logging.info(f"附件名称列: {name_column}")
            logging.info(f"政策标题列: {title_column}")
            logging.info(f"政策分类列: {category_column}")
            
            # 处理每一行
            for index, row in df.iterrows():
                try:
                    # 获取附件链接
                    attachment_link = row.get(link_column, '')
                    if pd.isna(attachment_link) or not attachment_link:
                        logging.warning(f"跳过无链接的附件 (行 {index})")
                        self.download_stats['skipped'] += 1
                        continue
                    
                    # 获取附件名称（优先使用）
                    attachment_name = row.get(name_column, '') if name_column else ''
                    policy_title = row.get(title_column, f'政策_{index}') if title_column else f'政策_{index}'
                    policy_category = row.get(category_column, '未知分类') if category_column else '未知分类'
                    
                    # 生成文件名（优先使用附件名称）
                    filename = self.get_filename_from_attachment(attachment_name, attachment_link)
                    
                    # 创建政策分类子目录
                    category_dir = os.path.join(self.output_dir, policy_category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    # 下载文件
                    success = self.download_file(attachment_link, filename, category_dir)
                    
                    self.download_stats['total'] += 1
                    
                    # 添加延迟避免请求过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"处理附件记录时出错 (行 {index}): {e}")
                    self.download_stats['failed'] += 1
                    continue
            
            # 输出统计信息
            self.print_stats()
            
        except Exception as e:
            logging.error(f"处理附件表格时出错: {e}")
    
    def print_stats(self):
        """打印下载统计信息"""
        print("\n" + "="*60)
        print("📊 附件下载统计信息:")
        print("="*60)
        print(f"总附件数: {self.download_stats['total']}")
        print(f"下载成功: {self.download_stats['success']}")
        print(f"下载失败: {self.download_stats['failed']}")
        print(f"跳过文件: {self.download_stats['skipped']}")
        
        if self.download_stats['total'] > 0:
            success_rate = (self.download_stats['success'] / self.download_stats['total']) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print(f"文件保存目录: {os.path.abspath(self.output_dir)}")
        print("="*60)
    
    def create_index_file(self):
        """创建索引文件"""
        try:
            index_file = os.path.join(self.output_dir, '附件索引.txt')
            
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write("发改委政策附件索引\n")
                f.write("="*50 + "\n\n")
                
                # 遍历目录结构
                for root, dirs, files in os.walk(self.output_dir):
                    if root == self.output_dir:
                        continue
                    
                    category = os.path.basename(root)
                    f.write(f"\n【{category}】\n")
                    f.write("-" * 30 + "\n")
                    
                    for file in files:
                        if file != '附件索引.txt':
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            f.write(f"{file} ({file_size} bytes)\n")
            
            logging.info(f"索引文件已创建: {index_file}")
            
        except Exception as e:
            logging.error(f"创建索引文件时出错: {e}")

def main():
    """主函数"""
    print("📥 发改委政策附件下载器")
    print("="*60)
    
    # 检查输入文件
    excel_file = 'full_data/附件.xlsx'
    if not os.path.exists(excel_file):
        print(f"❌ 错误：找不到附件表格文件 {excel_file}")
        print("请确保full_data目录下有附件.xlsx文件")
        return
    
    # 创建下载器
    downloader = AttachmentDownloader(
        excel_file=excel_file,
        output_dir='full_data/附件文件'
    )
    
    # 开始下载
    print(f"📁 输入文件: {os.path.abspath(excel_file)}")
    print(f"📁 输出目录: {os.path.abspath(downloader.output_dir)}")
    print(f"📊 开始下载附件...")
    
    start_time = time.time()
    downloader.process_attachments()
    end_time = time.time()
    
    # 创建索引文件
    downloader.create_index_file()
    
    print(f"\n⏱️ 总耗时: {end_time - start_time:.1f} 秒")
    print("🎉 附件下载完成！")

if __name__ == "__main__":
    main()
