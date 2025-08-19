#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版附件下载脚本
"""

import os
import requests
import pandas as pd
import time

def download_attachments():
    """下载Sheet3中的附件"""
    
    # 找到最新的Excel文件
    parsed_content_dir = 'parsed_content'
    if not os.path.exists(parsed_content_dir):
        print("❌ parsed_content目录不存在")
        return
        
    excel_files = [f for f in os.listdir(parsed_content_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    if not excel_files:
        print("❌ 没有找到Excel文件")
        return
        
    latest_file = max(excel_files, key=lambda x: os.path.getmtime(os.path.join(parsed_content_dir, x)))
    excel_path = os.path.join(parsed_content_dir, latest_file)
    print(f"📁 读取文件: {latest_file}")
    
    # 创建下载目录
    download_dir = 'downloads'
    os.makedirs(download_dir, exist_ok=True)
    
    # 读取Sheet3
    try:
        df = pd.read_excel(excel_path, sheet_name='附件信息')
        print(f"📋 找到 {len(df)} 个附件")
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        success = 0
        failed = 0
        
        for i, row in df.iterrows():
            # 检查数据完整性
            if pd.isna(row['附件链接']) or pd.isna(row['附件名称']) or pd.isna(row['政策标题']):
                print(f"   ⚠️ 跳过第{i+1}行：数据不完整")
                failed += 1
                continue
                
            url = str(row['附件链接']).strip()
            name = str(row['附件名称']).strip()
            title = str(row['政策标题']).strip()
            
            # 检查URL有效性
            if not url.startswith('http'):
                print(f"   ⚠️ 跳过第{i+1}行：无效URL")
                failed += 1
                continue
            
            # 构建文件名 - 更安全的处理
            import re
            safe_title = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', title)[:30]
            safe_name = re.sub(r'[<>:"/\\|?*\n\r\t]', '_', name)
            
            # 确保文件名不为空
            if not safe_title or not safe_name:
                safe_title = "政策文件"
                safe_name = f"附件{i+1}"
                
            # 限制总文件名长度
            max_filename_length = 100
            temp_filename = f"{safe_title}_{safe_name}"
            if len(temp_filename) > max_filename_length:
                # 保留扩展名
                if '.' in safe_name:
                    name_parts = safe_name.rsplit('.', 1)
                    extension = '.' + name_parts[1]
                    name_part = name_parts[0]
                else:
                    extension = ''
                    name_part = safe_name
                
                # 计算可用长度
                available_length = max_filename_length - len(safe_title) - len(extension) - 1  # -1 for underscore
                if available_length > 0:
                    safe_name = name_part[:available_length] + extension
                else:
                    safe_name = f"附件{i+1}{extension}"
                
            filename = f"{safe_title}_{safe_name}"
            
            filepath = os.path.join(download_dir, filename)
            
            print(f"⏳ 下载 {i+1}/{len(df)}: {filename}")
            
            try:
                # 如果文件已存在，跳过
                if os.path.exists(filepath):
                    print(f"   ✅ 已存在，跳过")
                    success += 1
                    continue
                
                # 下载文件
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # 检查响应内容类型
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type and len(response.content) < 1000:
                    print(f"   ⚠️ 可能是错误页面，跳过")
                    failed += 1
                    continue
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                # 检查文件大小
                file_size = os.path.getsize(filepath)
                if file_size == 0:
                    print(f"   ⚠️ 文件大小为0，删除空文件")
                    os.remove(filepath)
                    failed += 1
                else:
                    print(f"   ✅ 下载成功 ({file_size} bytes)")
                    success += 1
                
            except requests.exceptions.Timeout:
                print(f"   ❌ 下载超时")
                failed += 1
            except requests.exceptions.ConnectionError:
                print(f"   ❌ 连接错误")
                failed += 1
            except requests.exceptions.HTTPError as e:
                print(f"   ❌ HTTP错误: {e}")
                failed += 1
            except Exception as e:
                print(f"   ❌ 下载失败: {e}")
                failed += 1
            
            # 延迟1秒
            time.sleep(1)
        
        print(f"\n🎉 下载完成！成功: {success}, 失败: {failed}")
        print(f"📂 文件保存在: {download_dir}")
        
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {e}")

if __name__ == "__main__":
    download_attachments()
