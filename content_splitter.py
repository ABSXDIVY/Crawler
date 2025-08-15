#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发改委政策正文内容分段器
对Excel文件Sheet2的正文内容进行智能分段，确保每行不超过1000字并保持语义完整
"""

import pandas as pd
import re
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/content_splitter.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ContentSplitter:
    """正文内容分段器"""
    
    def __init__(self, max_chars=1000):
        """初始化分段器"""
        self.max_chars = max_chars
        logging.info(f"正文分段器初始化完成，最大字符数: {max_chars}")
    
    def split_content(self, content):
        """智能分段正文内容"""
        if not content or len(content.strip()) == 0:
            return []
        
        # 清理内容
        content = self.clean_content(content)
        
        # 如果内容长度小于最大字符数，直接返回
        if len(content) <= self.max_chars:
            return [content]
        
        # 分段策略：按优先级尝试不同的分割点
        segments = []
        remaining_content = content
        
        while len(remaining_content) > self.max_chars:
            # 策略1：查找章节标题（第X章、第X条等）
            split_point = self.find_chapter_split(remaining_content)
            
            # 策略2：查找段落分隔符
            if split_point == -1:
                split_point = self.find_paragraph_split(remaining_content)
            
            # 策略3：查找句子分隔符
            if split_point == -1:
                split_point = self.find_sentence_split(remaining_content)
            
            # 策略4：查找标点符号
            if split_point == -1:
                split_point = self.find_punctuation_split(remaining_content)
            
            # 策略5：强制分割
            if split_point == -1:
                split_point = self.max_chars
            
            # 确保分割点是有效的整数
            try:
                split_point = int(split_point)
                if split_point <= 0 or split_point >= len(remaining_content):
                    split_point = self.max_chars
            except (ValueError, TypeError):
                split_point = self.max_chars
            
            # 分割内容
            try:
                segment = remaining_content[:split_point].strip()
                remaining_content = remaining_content[split_point:].strip()
                
                if segment:
                    segments.append(segment)
            except Exception as e:
                logging.warning(f"分割内容时出错: {e}, 使用强制分割")
                # 强制分割
                segment = remaining_content[:self.max_chars].strip()
                remaining_content = remaining_content[self.max_chars:].strip()
                if segment:
                    segments.append(segment)
        
        # 添加剩余内容
        if remaining_content:
            segments.append(remaining_content)
        
        return segments
    
    def find_chapter_split(self, content):
        """查找章节分割点"""
        try:
            # 查找章节标题模式
            patterns = [
                r'十第[一二三四五六七八九十\d]+章',  # 第X章
                r'第[一二三四五六七八九\d]+条',  # 第X条
                r'第[一二三四五六七八九十\d]+节',  # 第X节
                r'第[一二三四五六七八九十\d]+部分',  # 第X部分
                r'第[一二三四五六七八九十\d]+项',  # 第X项
                r'（[一二三四五六七八九十\d]+）',  # （X）
                r'\([一二三四五六七八九十\d]+\)',  # (X)
                r'[一二三四五六七八九十\d]+、',  # X、
                r'\d+\.',  # 1.
                r'\d+、',  # 1、
            ]
            
            for pattern in patterns:
                try:
                    matches = list(re.finditer(pattern, content))
                    for match in matches:
                        start_pos = match.start()
                        if start_pos > self.max_chars * 0.3 and start_pos <= self.max_chars:
                            return start_pos
                except Exception as e:
                    logging.warning(f"正则表达式匹配出错: {e}")
                    continue
            
            return -1
        except Exception as e:
            logging.warning(f"查找章节分割点时出错: {e}")
            return -1
    
    def find_paragraph_split(self, content):
        """查找段落分割点"""
        try:
            # 查找段落分隔符
            paragraph_markers = ['\n\n', '\r\n\r\n', '\n\r\n\r']
            
            for marker in paragraph_markers:
                try:
                    pos = content.find(marker, int(self.max_chars * 0.5))
                    if pos != -1 and pos <= self.max_chars:
                        return pos + len(marker)
                except Exception as e:
                    logging.warning(f"查找段落分割点时出错: {e}")
                    continue
            
            return -1
        except Exception as e:
            logging.warning(f"查找段落分割点时出错: {e}")
            return -1
    
    def find_sentence_split(self, content):
        """查找句子分割点"""
        try:
            # 查找句子结束标点
            sentence_endings = ['。', '！', '？', '；', '.', '!', '?', ';']
            
            for ending in sentence_endings:
                try:
                    start_pos = int(self.max_chars * 0.7)
                    end_pos = self.max_chars
                    pos = content.rfind(ending, start_pos, end_pos)
                    if pos != -1:
                        return pos + 1
                except Exception as e:
                    logging.warning(f"查找句子分割点时出错: {e}")
                    continue
            
            return -1
        except Exception as e:
            logging.warning(f"查找句子分割点时出错: {e}")
            return -1
    
    def find_punctuation_split(self, content):
        """查找标点符号分割点"""
        try:
            # 查找其他标点符号
            punctuation_marks = ['，', ',', '、', '：', ':', '；', ';']
            
            for mark in punctuation_marks:
                try:
                    start_pos = int(self.max_chars * 0.8)
                    end_pos = self.max_chars
                    pos = content.rfind(mark, start_pos, end_pos)
                    if pos != -1:
                        return pos + 1
                except Exception as e:
                    logging.warning(f"查找标点分割点时出错: {e}")
                    continue
            
            return -1
        except Exception as e:
            logging.warning(f"查找标点分割点时出错: {e}")
            return -1
    
    def clean_content(self, content):
        """清理内容"""
        if not content:
            return ''
        
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content.strip())
        # 移除特殊字符
        content = re.sub(r'[\r\n\t]+', '\n', content)
        # 移除多余的空行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return content
    
    def process_excel_file(self, input_file, output_file):
        """处理Excel文件"""
        try:
            logging.info(f"开始处理Excel文件: {input_file}")
            
            # 读取Sheet2 - 政策正文
            df = pd.read_excel(input_file, sheet_name='政策正文')
            logging.info(f"读取到 {len(df)} 条正文记录")
            
            # 创建新的分段数据
            split_data = []
            
            for index, row in df.iterrows():
                policy_title = row['政策标题']
                content = str(row['正文内容'])
                
                logging.info(f"处理政策: {policy_title}")
                
                # 分段处理正文内容
                segments = self.split_content(content)
                
                if not segments:
                    # 如果没有分段，添加空内容
                    split_data.append({
                        '政策分类': row['政策分类'],
                        '政策标题': policy_title,
                        '文号': row['文号'],
                        '发布日期': row['发布日期'],
                        '政策链接': row['政策链接'],
                        '段落序号': 1,
                        '段落内容': '',
                        '字符数': 0
                    })
                else:
                    # 添加分段后的内容
                    for i, segment in enumerate(segments, 1):
                        split_data.append({
                            '政策分类': row['政策分类'],
                            '政策标题': policy_title,
                            '文号': row['文号'],
                            '发布日期': row['发布日期'],
                            '政策链接': row['政策链接'],
                            '段落序号': i,
                            '段落内容': segment,
                            '字符数': len(segment)
                        })
                
                logging.info(f"政策 '{policy_title}' 分段完成，共 {len(segments)} 段")
            
            # 创建新的DataFrame
            split_df = pd.DataFrame(split_data)
            
            # 保存到新的Excel文件
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                split_df.to_excel(writer, sheet_name='政策正文_分段', index=False)
            
            logging.info(f"分段完成，共生成 {len(split_data)} 条记录")
            logging.info(f"数据已保存到: {output_file}")
            
            # 打印统计信息
            self.print_statistics(split_df)
            
            return split_df
            
        except Exception as e:
            logging.error(f"处理Excel文件时出错: {e}")
            raise
    
    def print_statistics(self, df):
        """打印统计信息"""
        logging.info("\n📊 分段统计信息:")
        logging.info(f"总段落数: {len(df)}")
        logging.info(f"涉及政策数: {df['政策标题'].nunique()}")
        logging.info(f"平均段落长度: {df['字符数'].mean():.1f} 字符")
        logging.info(f"最长段落: {df['字符数'].max()} 字符")
        logging.info(f"最短段落: {df['字符数'].min()} 字符")
        
        # 统计段落长度分布
        short_segments = len(df[df['字符数'] <= 500])
        medium_segments = len(df[(df['字符数'] > 500) & (df['字符数'] <= 1000)])
        long_segments = len(df[df['字符数'] > 1000])
        
        logging.info(f"短段落(≤500字): {short_segments} 段")
        logging.info(f"中段落(500-1000字): {medium_segments} 段")
        logging.info(f"长段落(>1000字): {long_segments} 段")

def main():
    """主函数"""
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 输入和输出文件
    input_file = 'policy_data_full.xlsx'
    output_file = 'policy_content_split.xlsx'
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        logging.error(f"输入文件不存在: {input_file}")
        return
    
    # 创建分段器
    splitter = ContentSplitter(max_chars=1000)
    
    # 处理文件
    try:
        splitter.process_excel_file(input_file, output_file)
        logging.info("🎉 正文分段处理完成！")
    except Exception as e:
        logging.error(f"处理失败: {e}")

if __name__ == "__main__":
    main()
