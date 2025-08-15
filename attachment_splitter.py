#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发改委政策附件信息拆解器
对Excel文件Sheet3的附件信息进行拆解，将包含多个附件的行拆分成多行，并根据链接后缀自动填入文件类型
"""

import pandas as pd
import re
import os
import logging
from datetime import datetime
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/attachment_splitter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AttachmentSplitter:
    """附件信息拆解器"""
    
    def __init__(self):
        """初始化拆解器"""
        # 文件类型映射
        self.file_type_mapping = {
            '.pdf': 'PDF',
            '.ofd': 'OFD',
            '.doc': 'Word',
            '.docx': 'Word',
            '.xls': 'Excel',
            '.xlsx': 'Excel',
            '.ppt': 'PowerPoint',
            '.pptx': 'PowerPoint',
            '.txt': '文本文件',
            '.zip': '压缩文件',
            '.rar': '压缩文件',
            '.7z': '压缩文件',
            '.jpg': '图片文件',
            '.jpeg': '图片文件',
            '.png': '图片文件',
            '.gif': '图片文件',
            '.bmp': '图片文件',
            '.tiff': '图片文件',
            '.mp4': '视频文件',
            '.avi': '视频文件',
            '.mov': '视频文件',
            '.wmv': '视频文件',
            '.mp3': '音频文件',
            '.wav': '音频文件',
            '.flv': '音频文件',
            '.html': '网页文件',
            '.htm': '网页文件',
            '.xml': 'XML文件',
            '.json': 'JSON文件',
            '.csv': 'CSV文件',
            '.rtf': 'RTF文件',
            '.odt': 'OpenDocument',
            '.ods': 'OpenDocument',
            '.odp': 'OpenDocument'
        }
        
        logging.info("附件拆解器初始化完成")
    
    def detect_file_type(self, url):
        """根据URL后缀检测文件类型"""
        if not url or pd.isna(url):
            return '未知类型'
        
        try:
            # 解析URL
            parsed_url = urlparse(str(url))
            path = parsed_url.path.lower()
            
            # 查找文件扩展名
            for ext, file_type in self.file_type_mapping.items():
                if path.endswith(ext):
                    return file_type
            
            # 如果没有找到匹配的扩展名，尝试从URL中提取
            if '.' in path:
                ext = '.' + path.split('.')[-1]
                # 检查是否是已知的扩展名
                if ext in self.file_type_mapping:
                    return self.file_type_mapping[ext]
                else:
                    return f'其他文件({ext})'
            
            # 尝试从查询参数中提取文件类型
            if parsed_url.query:
                query_lower = parsed_url.query.lower()
                for ext, file_type in self.file_type_mapping.items():
                    if ext in query_lower:
                        return file_type
            
            return '未知类型'
        except Exception as e:
            logging.warning(f"检测文件类型时出错: {e}, URL: {url}")
            return '未知类型'
    
    def split_attachments(self, attachment_names, attachment_links):
        """拆解附件名称和链接"""
        if pd.isna(attachment_names) or pd.isna(attachment_links):
            return []
        
        names_str = str(attachment_names).strip()
        links_str = str(attachment_links).strip()
        
        if not names_str or not links_str:
            return []
        
        # 首先提取所有链接
        links = self.extract_all_links(links_str)
        
        if not links:
            # 如果没有找到链接，返回单个附件
            return [{
                '附件名称': names_str,
                '附件链接': links_str,
                '文件类型': self.detect_file_type(links_str)
            }]
        
        # 根据链接数量决定拆分策略
        if len(links) == 1:
            # 只有一个链接，返回单个附件
            return [{
                '附件名称': names_str,
                '附件链接': links_str,
                '文件类型': self.detect_file_type(links_str)
            }]
        
        # 多个链接，需要拆分名称
        name_parts = self.split_names_by_links(names_str, links_str, links)
        
        # 构建附件列表
        attachments = []
        for i, (name, link) in enumerate(zip(name_parts, links)):
            if name and link:
                attachments.append({
                    '附件名称': name,
                    '附件链接': link,
                    '文件类型': self.detect_file_type(link)
                })
        
        return attachments
    
    def extract_all_links(self, links_str):
        """提取所有http链接"""
        links = []
        
        # 只匹配http/https链接
        link_patterns = [
            r'https?://[^\s\n,;，；、|]+',  # HTTP/HTTPS链接
        ]
        
        for pattern in link_patterns:
            found_links = re.findall(pattern, links_str)
            links.extend(found_links)
        
        # 去重并保持顺序
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        logging.info(f"提取到 {len(unique_links)} 个http链接")
        return unique_links
    
    def split_names_by_links(self, names_str, links_str, links):
        """根据链接拆分名称 - 仅根据http字段分解，名称按序号或明显符号分解"""
        if len(links) == 1:
            return [names_str]
        
        logging.info(f"链接数量: {len(links)}")
        
        # 策略1: 尝试根据明显的序号或符号拆分名称
        name_parts = self.split_by_clear_markers(names_str, len(links))
        if len(name_parts) == len(links):
            logging.info(f"根据明显标记拆分成功，共 {len(name_parts)} 个")
            return name_parts
        
        # 策略2: 尝试不同的分隔符来拆分名称
        separators = [
            '\n',           # 换行符
            '；',           # 中文分号
            ';',            # 英文分号
            '，',           # 中文逗号
            ',',            # 英文逗号
            '、',           # 中文顿号
            '|',            # 竖线
            '||',           # 双竖线
        ]
        
        # 尝试找到合适的分隔符
        for sep in separators:
            if sep in names_str:
                name_parts = [part.strip() for part in names_str.split(sep) if part.strip()]
                if len(name_parts) == len(links):
                    logging.info(f"使用分隔符 '{sep}' 拆解附件名称，共 {len(name_parts)} 个")
                    return name_parts
        
        # 策略3: 如果无法拆分，使用默认的序号分配
        name_parts = self.split_by_default_sequence(names_str, len(links))
        logging.info(f"使用默认序号分配，共 {len(name_parts)} 个")
        
        return name_parts
    
    def split_by_clear_markers(self, names_str, link_count):
        """根据明显的序号或符号拆分名称"""
        name_parts = []
        
        # 查找明显的序号模式
        patterns = [
            r'(\d+)[\.、\)）]',  # 数字+点/顿号/括号
            r'[（\(](\d+)[）\)]',  # 括号中的数字
            r'第(\d+)',          # 第X
            r'附件(\d+)',        # 附件X
        ]
        
        # 尝试找到序号位置
        marker_positions = []
        for pattern in patterns:
            matches = list(re.finditer(pattern, names_str))
            if len(matches) == link_count:
                marker_positions = [(m.start(), m.group()) for m in matches]
                break
        
        if marker_positions:
            # 按序号位置拆分
            marker_positions.sort(key=lambda x: x[0])
            
            for i, (pos, marker) in enumerate(marker_positions):
                if i == 0:
                    # 第一个序号，取从开始到下一个序号之前的内容
                    if i + 1 < len(marker_positions):
                        end_pos = marker_positions[i + 1][0]
                        name_part = names_str[:end_pos].strip()
                    else:
                        name_part = names_str.strip()
                else:
                    # 其他序号，取从当前序号到下一个序号之前的内容
                    if i + 1 < len(marker_positions):
                        end_pos = marker_positions[i + 1][0]
                        name_part = names_str[pos:end_pos].strip()
                    else:
                        name_part = names_str[pos:].strip()
                
                if name_part:
                    name_parts.append(name_part)
        
        return name_parts
    
    def split_by_default_sequence(self, names_str, link_count):
        """使用默认的序号分配"""
        name_parts = []
        
        # 如果只有一个链接，返回原名称
        if link_count == 1:
            return [names_str]
        
        # 对于多个链接，尝试智能分配
        # 查找可能的自然分割点
        split_points = []
        
        # 查找常见的分割点
        split_patterns = [
            r'[。！？；]',  # 句号、感叹号、问号、分号
            r'[，,]',      # 逗号
            r'[、]',       # 顿号
            r'\s+',        # 多个空格
        ]
        
        for pattern in split_patterns:
            matches = list(re.finditer(pattern, names_str))
            if len(matches) >= link_count - 1:
                split_points = [m.end() for m in matches[:link_count-1]]
                break
        
        if split_points:
            # 根据分割点拆分
            last_pos = 0
            for pos in split_points:
                name_part = names_str[last_pos:pos].strip()
                if name_part:
                    name_parts.append(name_part)
                last_pos = pos
            
            # 添加最后一部分
            if last_pos < len(names_str):
                name_part = names_str[last_pos:].strip()
                if name_part:
                    name_parts.append(name_part)
        else:
            # 如果没有找到自然分割点，按长度平均分配
            part_length = len(names_str) // link_count
            for i in range(link_count):
                if i == 0:
                    name_part = names_str[:part_length].strip()
                elif i == link_count - 1:
                    name_part = names_str[part_length:].strip()
                else:
                    start = i * part_length
                    end = (i + 1) * part_length
                    name_part = names_str[start:end].strip()
                
                if name_part:
                    name_parts.append(name_part)
        
        # 确保数量匹配
        while len(name_parts) < link_count:
            name_parts.append(f"附件{len(name_parts)+1}")
        
        return name_parts[:link_count]
    
    def get_file_extension(self, url):
        """获取文件扩展名"""
        try:
            parsed_url = urlparse(str(url))
            path = parsed_url.path.lower()
            if '.' in path:
                return '.' + path.split('.')[-1]
            return ''
        except:
            return ''
    
    def split_by_extensions(self, names_str, links, extensions):
        """根据文件后缀拆分名称"""
        name_parts = []
        
        # 查找名称中是否包含对应的后缀
        for i, (link, ext) in enumerate(zip(links, extensions)):
            if ext:
                # 在名称中查找包含该后缀的部分
                ext_pattern = re.escape(ext)
                matches = re.findall(f'[^\\s\\n,;，；、|]*{ext_pattern}[^\\s\\n,;，；、|]*', names_str)
                
                if matches:
                    # 找到匹配的后缀，使用对应的名称部分
                    name_part = matches[0]
                    name_parts.append(name_part)
                    # 从原名称中移除已匹配的部分
                    names_str = names_str.replace(name_part, '', 1)
                else:
                    # 没找到匹配的后缀，使用默认拆分
                    name_part = self.split_name_by_position(names_str, i, len(links))
                    name_parts.append(name_part)
            else:
                # 没有后缀，使用默认拆分
                name_part = self.split_name_by_position(names_str, i, len(links))
                name_parts.append(name_part)
        
        return name_parts
    
    def split_by_link_positions(self, names_str, links_str, links):
        """根据链接在文本中的位置来拆分名称"""
        name_parts = []
        
        # 查找每个链接在文本中的位置
        link_positions = []
        for link in links:
            pos = links_str.find(link)
            if pos != -1:
                link_positions.append((pos, link))
        
        # 按位置排序
        link_positions.sort(key=lambda x: x[0])
        
        # 根据链接位置拆分名称
        for i, (pos, link) in enumerate(link_positions):
            name_part = self.split_name_by_position(names_str, i, len(links))
            name_parts.append(name_part)
        
        return name_parts
    
    def split_name_by_position(self, names_str, index, total_count):
        """根据位置拆分名称"""
        if total_count == 1:
            return names_str
        
        # 计算每个部分的长度
        part_length = len(names_str) // total_count
        
        if index == 0:
            # 第一个部分
            name_part = names_str[:part_length].strip()
        elif index == total_count - 1:
            # 最后一个部分
            name_part = names_str[part_length:].strip()
        else:
            # 中间部分
            start = index * part_length
            end = (index + 1) * part_length
            name_part = names_str[start:end].strip()
        
        # 清理名称
        name_part = self.clean_attachment_name(name_part)
        if not name_part:
            name_part = f"附件{index+1}"
        
        return name_part
    
    def clean_attachment_name(self, name):
        """清理附件名称"""
        if not name:
            return ""
        
        # 移除多余的空白字符
        name = re.sub(r'\s+', ' ', name.strip())
        
        # 移除特殊字符，但保留中文、英文、数字和常用标点
        name = re.sub(r'[^\w\s\u4e00-\u9fff\-_\.\(\)（）]+', '', name)
        
        return name.strip()
    

    
    def process_excel_file(self, input_file, output_file):
        """处理Excel文件"""
        try:
            logging.info(f"开始处理Excel文件: {input_file}")
            
            # 读取Sheet3 - 政策附件
            df = pd.read_excel(input_file, sheet_name='政策附件')
            logging.info(f"读取到 {len(df)} 条附件记录")
            
            # 创建新的拆解数据
            split_data = []
            
            for index, row in df.iterrows():
                policy_title = row['政策标题']
                attachment_names = row['附件名称']
                attachment_links = row['附件链接']
                
                logging.info(f"处理政策附件: {policy_title}")
                
                # 拆解附件信息
                attachments = self.split_attachments(attachment_names, attachment_links)
                
                if not attachments:
                    # 如果没有附件，添加空记录
                    split_data.append({
                        '政策分类': row['政策分类'],
                        '政策标题': policy_title,
                        '文号': row['文号'],
                        '发布日期': row['发布日期'],
                        '政策链接': row['政策链接'],
                        '附件序号': 1,
                        '附件名称': '',
                        '附件链接': '',
                        '文件类型': '无附件'
                    })
                else:
                    # 添加拆解后的附件
                    for i, attachment in enumerate(attachments, 1):
                        split_data.append({
                            '政策分类': row['政策分类'],
                            '政策标题': policy_title,
                            '文号': row['文号'],
                            '发布日期': row['发布日期'],
                            '政策链接': row['政策链接'],
                            '附件序号': i,
                            '附件名称': attachment['附件名称'],
                            '附件链接': attachment['附件链接'],
                            '文件类型': attachment['文件类型']
                        })
                
                logging.info(f"政策 '{policy_title}' 附件拆解完成，共 {len(attachments)} 个附件")
            
            # 创建新的DataFrame
            split_df = pd.DataFrame(split_data)
            
            # 保存到新的Excel文件
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                split_df.to_excel(writer, sheet_name='政策附件_拆解', index=False)
            
            logging.info(f"附件拆解完成，共生成 {len(split_data)} 条记录")
            logging.info(f"数据已保存到: {output_file}")
            
            # 打印统计信息
            self.print_statistics(split_df)
            
            return split_df
            
        except Exception as e:
            logging.error(f"处理Excel文件时出错: {e}")
            raise
    
    def print_statistics(self, df):
        """打印统计信息"""
        logging.info("\n📊 附件拆解统计信息:")
        logging.info(f"总附件数: {len(df)}")
        logging.info(f"涉及政策数: {df['政策标题'].nunique()}")
        
        # 文件类型统计
        file_type_counts = df['文件类型'].value_counts()
        logging.info(f"文件类型分布:")
        for file_type, count in file_type_counts.head(10).items():
            logging.info(f"  {file_type}: {count} 个")
        
        # 有附件的政策统计
        policies_with_attachments = df[df['文件类型'] != '无附件']['政策标题'].nunique()
        policies_without_attachments = df[df['文件类型'] == '无附件']['政策标题'].nunique()
        
        logging.info(f"有附件的政策数: {policies_with_attachments}")
        logging.info(f"无附件的政策数: {policies_without_attachments}")
        
        # 附件数量分布
        attachment_counts = df.groupby('政策标题')['附件序号'].max()
        logging.info(f"平均每个政策附件数: {attachment_counts.mean():.1f}")
        logging.info(f"最多附件数: {attachment_counts.max()}")
        logging.info(f"最少附件数: {attachment_counts.min()}")

def main():
    """主函数"""
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 输入和输出文件
    input_file = 'policy_data_full.xlsx'
    output_file = 'policy_attachments_split.xlsx'
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        logging.error(f"输入文件不存在: {input_file}")
        return
    
    # 创建拆解器
    splitter = AttachmentSplitter()
    
    # 处理文件
    try:
        splitter.process_excel_file(input_file, output_file)
        logging.info("🎉 附件拆解处理完成！")
    except Exception as e:
        logging.error(f"处理失败: {e}")

if __name__ == "__main__":
    main() 
