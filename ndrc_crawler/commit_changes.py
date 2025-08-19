#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NDRC政策文件爬虫系统 - Git提交脚本
帮助快速提交所有更改到GitHub仓库
"""

import os
import subprocess
import sys
from datetime import datetime

def run_git_command(command, description):
    """运行Git命令"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            if result.stdout and result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} 失败")
            if result.stderr and result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False

def check_git_config():
    """检查Git配置"""
    # 检查用户名
    result = subprocess.run("git config user.name", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git用户名未配置")
        print("请运行: git config --global user.name \"您的姓名\"")
        return False
    
    # 检查邮箱
    result = subprocess.run("git config user.email", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git邮箱未配置")
        print("请运行: git config --global user.email \"您的邮箱\"")
        return False
    
    print("✅ Git配置检查通过")
    return True

def check_git_status():
    """检查Git状态"""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode == 0 and result.stdout.strip():
        return True
    return False

def generate_commit_message(added_files):
    """生成提交信息"""
    # 根据文件类型生成不同的提交信息
    doc_files = [f for f in added_files if f in ['README.md', '.gitignore', 'LICENSE', 'requirements.txt', 'setup.py']]
    script_files = [f for f in added_files if f.endswith('.py')]
    
    commit_type = "feat"
    if doc_files and not script_files:
        commit_type = "docs"
    elif script_files and not doc_files:
        commit_type = "feat"
    else:
        commit_type = "feat"
    
    # 生成描述
    descriptions = []
    if 'README.md' in added_files:
        descriptions.append("完善项目文档")
    if '.gitignore' in added_files:
        descriptions.append("添加Git忽略文件")
    if 'LICENSE' in added_files:
        descriptions.append("添加开源许可证")
    if 'requirements.txt' in added_files:
        descriptions.append("添加依赖管理")
    if 'setup.py' in added_files:
        descriptions.append("添加安装脚本")
    if 'run.py' in added_files:
        descriptions.append("添加一键启动脚本")
    if 'analyze_attachments.py' in added_files:
        descriptions.append("添加附件分析功能")
    if 'attachment_analysis_report.py' in added_files:
        descriptions.append("添加附件分析报告")
    
    description = "、".join(descriptions) if descriptions else "更新项目文件"
    
    commit_message = f"{commit_type}: {description}\n\n"
    commit_message += f"- 修改文件: {', '.join(added_files)}\n"
    commit_message += f"- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return commit_message

def show_commit_stats():
    """显示提交统计信息"""
    print("\n📊 提交统计:")
    
    try:
        # 获取最近的提交信息
        result = subprocess.run("git log --oneline -1", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0 and result.stdout and result.stdout.strip():
            print(f"最新提交: {result.stdout.strip()}")
        
        # 获取文件统计
        result = subprocess.run("git diff --cached --stat", shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0 and result.stdout and result.stdout.strip():
            print("\n文件变更统计:")
            print(result.stdout.strip())
    except Exception as e:
        print(f"获取统计信息时出错: {e}")

def main():
    """主函数"""
    print("🚀 NDRC政策文件爬虫系统 - Git提交助手")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not os.path.exists('.git'):
        print("❌ 当前目录不是Git仓库")
        print("请先初始化Git仓库或切换到正确的目录")
        return
    
    # 检查Git配置
    print("🔧 检查Git配置...")
    if not check_git_config():
        return
    
    # 检查是否有更改
    if not check_git_status():
        print("📝 没有检测到需要提交的更改")
        return
    
    # 显示当前状态
    print("📋 当前Git状态:")
    run_git_command("git status", "查看Git状态")
    
    # 询问用户是否继续
    print("\n❓ 是否继续提交更改? (y/n): ", end='')
    if input().lower() != 'y':
        print("❌ 用户取消操作")
        return
    
    # 添加所有文件
    print("\n📁 添加文件到暂存区...")
    files_to_add = [
        'README.md',
        '.gitignore', 
        'LICENSE',
        'requirements.txt',
        'setup.py',
        'run.py',
        'analyze_attachments.py',
        'attachment_analysis_report.py',
        'commit_changes.py'
    ]
    
    added_files = []
    for file in files_to_add:
        if os.path.exists(file):
            if run_git_command(f"git add {file}", f"添加 {file}"):
                print(f"   ✅ 已添加: {file}")
                added_files.append(file)
            else:
                print(f"   ❌ 添加失败: {file}")
    
    # 添加其他Python文件
    python_files = [
        'ndrc_crawler.py',
        'data_extractor_full.py',
        'content_splitter.py',
        'attachment_splitter.py',
        'download_attachments.py',
        'config.py'
    ]
    
    for file in python_files:
        if os.path.exists(file):
            if run_git_command(f"git add {file}", f"添加 {file}"):
                print(f"   ✅ 已添加: {file}")
                added_files.append(file)
    
    # 检查是否有文件被添加
    if not added_files:
        print("❌ 没有文件被添加到暂存区")
        return
    
    # 生成提交信息
    commit_message = generate_commit_message(added_files)
    
    print(f"\n💬 提交更改...")
    print(f"提交信息: {commit_message[:100]}...")
    
    # 询问用户是否修改提交信息
    print("\n❓ 是否修改提交信息? (y/n): ", end='')
    if input().lower() == 'y':
        print("请输入新的提交信息: ", end='')
        commit_message = input()
    
    if run_git_command(f'git commit -m "{commit_message}"', "提交更改"):
        print("✅ 提交成功！")
        
        # 推送到远程仓库
        print("\n🚀 推送到GitHub...")
        if run_git_command("git push origin main", "推送到远程仓库"):
            print("✅ 推送成功！")
            print(f"\n🎉 所有更改已成功提交到: https://github.com/ABSXDIVY/ndrc_crawler")
            
            # 显示提交统计
            show_commit_stats()
        else:
            print("❌ 推送失败，请手动执行: git push origin main")
            print("可能的原因:")
            print("1. 网络连接问题")
            print("2. 权限不足")
            print("3. 远程仓库不存在")
    else:
        print("❌ 提交失败")

if __name__ == '__main__':
    main()
