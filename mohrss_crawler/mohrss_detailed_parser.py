#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人社部政策详细信息解析器
从results目录提取政策链接，访问详情页获取三种信息结构
"""

import os
import re
import time
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List
import logging
try:
	# 优先使用本模块的分段逻辑（章节/段落/句子/标点优先级）
	from mohrss_crawler.content_splitter import ContentSplitter  # type: ignore
except Exception:
	try:
		# 次优先：复用发改委分段器
		from ndrc_crawler.content_splitter import ContentSplitter  # type: ignore
	except Exception:
		# 兜底：简单的分段器（按空行与最大长度切分）
		class ContentSplitter:  # type: ignore
			def __init__(self, max_chars: int = 1000):
				self.max_chars = max_chars
			def split_content(self, content: str):
				if not content:
					return []
				content = re.sub(r'\r\n', '\n', str(content))
				parts = [p.strip() for p in content.split('\n\n') if p.strip()]
				segments = []
				for p in parts:
					if len(p) <= self.max_chars:
						segments.append(p)
					else:
						for i in range(0, len(p), self.max_chars):
							segments.append(p[i:i + self.max_chars])
				return segments

class MOHRSSDetailedParser:
	def __init__(self):
		self.results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
		self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parsed_content')
		os.makedirs(self.output_dir, exist_ok=True)
		self.setup_logging()
		# 正文分段器（仿照 ndrc 的做法）
		self.splitter = ContentSplitter(max_chars=1000)
		
		# 设置请求session
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1'
		})
		
		# 设置cookies
		self.session.cookies.update({
			'JSESSIONID': '376F1CEDDE3CA4D4153A1008F33BD2E8',
			'__tst_status': '3298241174#',
			'EO_Bot_Ssid': '3838967808'
		})
		
	def setup_logging(self):
		timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
		os.makedirs(log_dir, exist_ok=True)
		
		logging.basicConfig(
			level=logging.INFO,
			format='%(asctime)s - %(levelname)s - %(message)s',
			handlers=[
				logging.FileHandler(f'{log_dir}/detailed_parser_{timestamp}.log', encoding='utf-8'),
				logging.StreamHandler()
			]
		)
		self.logger = logging.getLogger(__name__)
		
	def extract_policy_links(self) -> List[Dict]:
		"""从results目录提取政策链接"""
		policy_links = []
		
		try:
			html_files = [f for f in os.listdir(self.results_dir) if f.endswith('.html')]
			
			for html_file in html_files:
				filepath = os.path.join(self.results_dir, html_file)
				self.logger.info(f"解析文件: {html_file}")
				
				with open(filepath, 'r', encoding='utf-8') as f:
					html_content = f.read()
					
				soup = BeautifulSoup(html_content, 'html.parser')
				
				# 查找所有表格
				tables = soup.find_all('table', style='border-collapse:separate;')
				
				for table in tables:
					# 查找所有td元素，按3个一组处理
					td_elements = table.find_all('td')
					
					# 每3个td为一组：日期、标题链接、文号
					for i in range(0, len(td_elements) - 2, 3):
						if i + 2 < len(td_elements):
							date_td = td_elements[i]
							title_td = td_elements[i + 1]
							doc_td = td_elements[i + 2]
							
							# 提取日期
							date_span = date_td.find('span')
							date = date_span.text.strip() if date_span else ''
							
							# 提取标题和链接
							title_link = title_td.find('a')
							if title_link:
								title = title_link.text.strip()
								url = title_link.get('href', '')
								doc_number = doc_td.text.strip()
								
								if url and title:
									policy_info = {
										'title': title,
										'url': url,
										'date': date,
										'doc_number': doc_number
									}
									policy_links.append(policy_info)
									
			self.logger.info(f"提取到 {len(policy_links)} 个政策链接")
			return policy_links
			
		except Exception as e:
			self.logger.error(f"提取政策链接时出错: {e}")
			return []
			
	def fetch_policy_detail(self, policy_info: Dict) -> Dict:
		"""获取政策详情页"""
		try:
			url = policy_info['url']
			title = policy_info['title']
			
			self.logger.info(f"获取详情: {title}")
			
			headers = {
				'Referer': 'https://www.mohrss.gov.cn/was5/web/search?channelid=203464&orderby=date&default=isall&page=1'
			}
			
			response = self.session.get(url, headers=headers, timeout=30)
			response.raise_for_status()
			response.encoding = 'utf-8'
			
			soup = BeautifulSoup(response.text, 'html.parser')
			
			# 提取三种信息结构
			basic_info = self.extract_basic_info(soup)
			content = self.extract_content(soup)
			attachments = self.extract_attachments(soup, url)
			
			return {
				'title': title,
				'url': url,
				'date': policy_info['date'],
				'doc_number': policy_info['doc_number'],
				'basic_info': basic_info,
				'content': content,
				'attachments': attachments
			}
			
		except Exception as e:
			self.logger.error(f"获取详情时出错: {e}")
			return {
				'title': policy_info['title'],
				'url': policy_info['url'],
				'error': str(e)
			}
			
	def extract_basic_info(self, soup: BeautifulSoup) -> Dict:
		"""提取基本信息"""
		basic_info = {}
		
		try:
			info_ul = soup.find('ul', class_='clearfix')
			if info_ul:
				for item in info_ul.find_all('li'):
					label_div = item.find('div', class_='arti_l')
					value_div = item.find('div', class_='arti_r')
					
					if label_div and value_div:
						label_text = label_div.get_text(strip=True)
						label = re.sub(r'[|\s\u00A0]', '', label_text)
						value = value_div.get_text(strip=True)
						
						# 特殊处理"是否有效"字段
						if '是否有效' in label:
							script_tag = value_div.find('script')
							if script_tag and script_tag.string:
								script_content = script_tag.string
								# 查找 isUsed 变量的值
								is_used_match = re.search(r"var\s+isUsed\s*=\s*['\"]([^'\"]+)['\"]", script_content)
								if is_used_match:
									value = is_used_match.group(1)
								else:
									# 如果没有找到isUsed变量，检查document.write的内容
									if 'document.write' in script_content:
										if '有效' in script_content:
											value = '有效'
										elif '已废止' in script_content:
											value = '已废止'
						else:
							# 处理其他字段的JavaScript内容
							if value == '' and value_div.find('script'):
								script_text = value_div.find('script').get_text(" ")
								if '已废止' in script_text:
									value = '已废止'
								elif '有效' in script_text:
									value = '有效'
						
						basic_info[label] = value
						
			return basic_info
			
		except Exception as e:
			self.logger.error(f"提取基本信息时出错: {e}")
			return {}
			
	def extract_content(self, soup: BeautifulSoup) -> str:
		"""提取正文内容"""
		try:
			# 查找正文内容区域 - 支持多种HTML结构
			content_div = None
			
			# 尝试查找 art_p 类的div
			content_div = soup.find('div', class_='art_p')
			
			# 如果没有找到，尝试查找 gz_content 类的div
			if not content_div:
				gz_content = soup.find('div', class_='gz_content')
				if gz_content:
					content_div = gz_content.find('div', class_='gz_content_txt')
			
			if content_div:
				# 提取所有文本内容，包括各种HTML标签
				paragraphs = []
				
				# 处理所有子元素
				for element in content_div.find_all(['p', 'span', 'div', 'font']):
					# 获取元素的文本内容
					text = element.get_text(strip=True)
					if text:
						paragraphs.append(text)
				
				# 如果没有找到子元素，直接获取整个div的文本
				if not paragraphs:
					text = content_div.get_text(strip=True)
					if text:
						paragraphs.append(text)
				
				content = '\n'.join(paragraphs)
				return content
			else:
				return ""
				
		except Exception as e:
			self.logger.error(f"提取正文内容时出错: {e}")
			return ""
			
	def extract_attachments(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
		"""提取附件链接和名称"""
		attachments = []
		
		try:
			# 从页面URL提取基础路径
			base_path = self.extract_base_path_from_url(page_url)
			
			att_div = soup.find('div', class_='cj_xiang_con')
			if att_div:
				for a in att_div.find_all('a'):
					href = a.get('href', '').strip()
					attachment_name = a.get_text(strip=True)  # 提取附件名称
					
					if href:
						# 处理相对URL，转换为完整URL
						if href.startswith('./'):
							href = href[2:]  # 移除 './'
						
						# 如果是相对路径，添加域名前缀
						if href.startswith('/'):
							href = 'https://www.mohrss.gov.cn' + href
						elif not href.startswith('http'):
							# 使用从页面URL提取的基础路径构建附件URL
							href = base_path + href
						
						# 如果附件名称为空，尝试从URL中提取文件名
						if not attachment_name:
							attachment_name = self.extract_filename_from_url(href)
						
						attachments.append({
							'name': attachment_name,
							'url': href
						})
			return attachments
			
		except Exception as e:
			self.logger.error(f"提取附件信息时出错: {e}")
			return []
			
	def extract_filename_from_url(self, url: str) -> str:
		"""从URL中提取文件名"""
		try:
			# 移除查询参数
			url_without_params = url.split('?')[0]
			# 获取URL的最后一部分作为文件名
			filename = url_without_params.split('/')[-1]
			# 如果文件名包含扩展名，直接返回
			if '.' in filename:
				return filename
			else:
				# 如果没有扩展名，尝试添加常见的文档扩展名
				return filename + '.doc'
		except Exception as e:
			self.logger.error(f"从URL提取文件名时出错: {e}")
			return "未知文件"
			
	def extract_base_path_from_url(self, page_url: str) -> str:
		"""从页面URL提取基础路径用于构建附件URL"""
		try:
			# 示例URL格式：
			# http://www.mohrss.gov.cn/xxgk2020/fdzdgknr/zcfg/gfxwj/rcrs/202508/t20250808_552480.html?keywords=
			# http://www.mohrss.gov.cn/xxgk2020/fdzdgknr/zcfg/gfxwj/shbx/202501/t20250115_534693.html?keywords=
			
			# 移除查询参数
			url_without_params = page_url.split('?')[0]
			
			# 查找日期模式（如202508, 202501）
			date_match = re.search(r'/(\d{6})/', url_without_params)
			if date_match:
				date_part = date_match.group(1)
				# 提取日期之前的路径部分
				path_before_date = url_without_params.split(f'/{date_part}/')[0]
				# 构建基础路径
				base_path = f"{path_before_date}/{date_part}/"
				self.logger.info(f"从URL提取基础路径: {base_path}")
				return base_path
			else:
				# 如果无法提取日期，返回默认路径
				self.logger.warning(f"无法从URL提取日期路径: {page_url}")
				return "https://www.mohrss.gov.cn/xxgk2020/fdzdgknr/zcfg/gfxwj/rcrs/"
				
		except Exception as e:
			self.logger.error(f"提取基础路径时出错: {e}")
			return "https://www.mohrss.gov.cn/xxgk2020/fdzdgknr/zcfg/gfxwj/rcrs/"
			
	def rename_basic_info_columns(self, df: pd.DataFrame) -> pd.DataFrame:
		"""重命名基本信息列名为中文"""
		# 由于基本信息字段是动态的，这里只处理常见的字段映射
		# 其他字段保持原样，因为它们可能已经是中文
		column_mapping = {}
		
		# 遍历所有列名，将英文列名映射为中文
		for col in df.columns:
			if col not in ['政策标题', '政策链接', '发布日期', '发文字号']:  # 这些已经是中文了
				# 这里可以根据实际需要添加更多的英文到中文的映射
				# 目前保持原样，因为基本信息字段通常已经是中文
				pass
		
		# 重命名列名
		df = df.rename(columns=column_mapping)
		return df
			
	def save_results(self, results: List[Dict]):
		"""保存三张表到一个Excel文件的三个sheet中"""
		if not results:
			self.logger.warning("没有结果可保存")
			return
			
		timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		excel_file = os.path.join(self.output_dir, f"mohrss_policy_details_{timestamp}.xlsx")
		
		basic_info_list = []
		content_list = []
		attachment_list = []
		
		for result in results:
			if 'error' not in result:
				# 基本信息 - 合并title和doc_number字段
				basic_info = result['basic_info'].copy()
				# 移除可能重复的字段，使用result中的值
				if 'title' in basic_info:
					del basic_info['title']
				if '标题' in basic_info:
					del basic_info['标题']
				if 'doc_number' in basic_info:
					del basic_info['doc_number']
				if '发布日期' in basic_info:
					del basic_info['发布日期']
				
				basic_info.update({
					'政策标题': result['title'],
					'政策链接': result['url'],
					'发文字号': result['doc_number']
				})
				basic_info_list.append(basic_info)
				
				# 正文内容（仿照 ndrc，将正文拆分为多行）
				segments = []
				try:
					segments = self.splitter.split_content(result['content'])
				except Exception as e:
					self.logger.warning(f"正文分段失败，降级为整篇一行: {e}")
					segments = [result['content'] or '']

				if not segments:
					segments = ['']

				for idx, seg in enumerate(segments, 1):
					content_list.append({
						'政策标题': result['title'],
						'政策链接': result['url'],
						'段落序号': idx,
						'段落内容': seg,
						'字符数': len(seg)
					})
				
				# 附件信息
				for attachment in result['attachments']:
					attachment_list.append({
						'政策标题': result['title'],
						'政策链接': result['url'],
						'附件名称': attachment['name'],
						'附件链接': attachment['url']
					})
		
		# 创建Excel文件并保存到三个sheet
		with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
			if basic_info_list:
				# 重命名基本信息列名为中文
				basic_df = pd.DataFrame(basic_info_list)
				basic_df = self.rename_basic_info_columns(basic_df)
				basic_df.to_excel(writer, sheet_name='基本信息', index=False)
				self.logger.info(f"基本信息已保存到sheet: 基本信息")
				
			if content_list:
				pd.DataFrame(content_list).to_excel(writer, sheet_name='正文内容_分段', index=False)
				self.logger.info(f"正文内容已保存到sheet: 正文内容_分段（按段落拆分）")
				
			if attachment_list:
				pd.DataFrame(attachment_list).to_excel(writer, sheet_name='附件信息', index=False)
				self.logger.info(f"附件信息已保存到sheet: 附件信息")
		
		self.logger.info(f"所有信息已保存到: {excel_file}")
			
	def parse_all_details_from_results(self):
		"""主处理函数"""
		try:
			policy_links = self.extract_policy_links()
			
			if not policy_links:
				self.logger.warning("没有找到政策链接")
				return
				
			self.logger.info(f"找到 {len(policy_links)} 个政策链接，开始处理所有链接")
			results = []
			
			for i, policy_info in enumerate(policy_links, 1):
				self.logger.info(f"处理第 {i}/{len(policy_links)} 个政策: {policy_info['title'][:50]}...")
				result = self.fetch_policy_detail(policy_info)
				results.append(result)
				
				# 添加延迟避免请求过快
				if i < len(policy_links):
					time.sleep(1)
					
			self.save_results(results)
			self.logger.info(f"所有 {len(policy_links)} 个政策处理完成")
			
		except Exception as e:
			self.logger.error(f"处理时出错: {e}")


def main():
	parser = MOHRSSDetailedParser()
	parser.parse_all_details_from_results()

if __name__ == "__main__":
	main()
