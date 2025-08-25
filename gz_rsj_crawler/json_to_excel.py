#!/usr/bin/env python3
"""将JSON数据导入到Excel表格的脚本"""
import os
import json
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# 数据目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
# 输出Excel文件路径
OUTPUT_EXCEL = os.path.join(PROJECT_ROOT, 'gz_rsj_data.xlsx')

# 爬虫类型定义
CRAWLER_TYPES = {
    '505': '规范性文件',
    '506': '其他文件',
    '507': '解读文件'
}


def load_json_files(type_id):
    """加载指定类型的所有JSON文件"""
    type_dir = os.path.join(DATA_DIR, type_id)
    if not os.path.exists(type_dir):
        print(f"类型 {type_id} 的目录不存在: {type_dir}")
        return []

    json_files = [f for f in os.listdir(type_dir) if f.endswith('.json')]
    all_data = []

    for file_name in json_files:
        file_path = os.path.join(type_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 提取articles数据
                if 'articles' in data and isinstance(data['articles'], list):
                    all_data.extend(data['articles'])
                    print(f"成功加载文件: {file_name}，读取到 {len(data['articles'])} 条记录")
                else:
                    print(f"文件 {file_name} 格式不正确，缺少articles字段")
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {str(e)}")

    return all_data


def json_to_excel():
    """将所有类型的JSON数据导入到Excel表格"""
    # 创建一个ExcelWriter对象
    writer = pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl')

    for type_id, type_name in CRAWLER_TYPES.items():
        print(f"\n处理类型: {type_id} ({type_name})...")
        # 加载JSON数据
        data = load_json_files(type_id)
        if not data:
            print(f"类型 {type_id} 没有数据")
            continue

        # 转换为DataFrame
        df = pd.DataFrame(data)
        
        # 只保留指定的字段
        specified_columns = ['title', 'document_number', 'publisher', 'classify_main_name', 'url', 'created_at']
        # 检查存在的列
        existing_columns = [col for col in specified_columns if col in df.columns]
        missing_columns = [col for col in specified_columns if col not in df.columns]
        
        if missing_columns:
            print(f"类型 {type_id} 缺少以下字段: {', '.join(missing_columns)}")
        
        # 筛选列
        df = df[existing_columns]
        print(f"类型 {type_id} 共有 {len(df)} 条记录，已筛选保留 {len(existing_columns)} 个字段")
        
        # 将字段名翻译为中文
        column_mapping = {
            'title': '标题',
            'document_number': '文号',
            'publisher': '发布单位',
            'classify_main_name': '分类',
            'url': '链接',
            'created_at': '创建时间'
        }
        # 只映射存在的列
        existing_column_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_column_mapping)
        print(f"已将字段名翻译为中文: {list(existing_column_mapping.values())}")

        # 将DataFrame写入Excel工作表
        sheet_name = f"{type_id}_{type_name[:5]}"  # 工作表名称限制为31个字符
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"已将类型 {type_id} 的数据写入Excel工作表: {sheet_name}")

    # 保存Excel文件
    writer.close()
    print(f"\n所有数据已成功导入到Excel文件: {OUTPUT_EXCEL}")


if __name__ == '__main__':
    print("开始将JSON数据导入到Excel表格...")
    start_time = datetime.now()
    json_to_excel()
    end_time = datetime.now()
    print(f"导入完成，耗时: {end_time - start_time}")