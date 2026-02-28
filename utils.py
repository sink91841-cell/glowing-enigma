#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块 - 提供通用功能
"""

import os
import sys
import datetime
from config import NEWSPAPER_CONFIG, IMAGE_FOLDER, COPY_FOLDER


def print_banner():
    """打印启动横幅"""
    print("=" * 70)
    print("📰 自媒体报刊抓取工具 - 国内免费AI版")
    print("=" * 70)
    print("✅ 支持.env配置文件，无硬编码密钥，安全可控")
    print("✅ 支持人民日报/经济日报/PDF、纽约时报图片解析")
    print("=" * 70)
    print()


def init_folders():
    """初始化文件夹"""
    folders = [IMAGE_FOLDER, COPY_FOLDER]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ 已创建文件夹：{folder}/")
        else:
            print(f"📁 文件夹已存在：{folder}/")
    print()


def format_date(date_obj):
    """格式化日期为不同格式"""
    return {
        'yyyy': date_obj.strftime('%Y'),
        'mm': date_obj.strftime('%m'),
        'dd': date_obj.strftime('%d'),
        'yymm': date_obj.strftime('%Y%m'),
        'ym': date_obj.strftime('%Y-%m'),  # 新增格式：2026-02
        'yyyymmdd': date_obj.strftime('%Y%m%d'),
    }


def select_date():
    """选择报纸日期"""
    print("=" * 70)
    print("📅 日期选择")
    print("=" * 70)
    print("1. 今天")
    print("2. 昨天 (推荐，报纸已发布)")
    print("3. 前天")
    print("4. 自定义日期 (YYYY-MM-DD)")
    print()

    while True:
        choice = input("👉 请选择 (1-4): ").strip()
        today = datetime.datetime.now()
        try:
            if choice == '1':
                date_obj = today
            elif choice == '2':
                date_obj = today - datetime.timedelta(days=1)
            elif choice == '3':
                date_obj = today - datetime.timedelta(days=2)
            elif choice == '4':
                date_input = input("👉 请输入日期 (YYYY-MM-DD): ").strip()
                date_obj = datetime.datetime.strptime(date_input, '%Y-%m-%d')
            else:
                print("❌ 无效选择，请输入1-4")
                continue

            # 防止选择未来日期
            if date_obj > today:
                print("⚠️ 未来日期自动调整为昨天")
                date_obj = today - datetime.timedelta(days=1)

            print(f"✅ 已选择：{date_obj.strftime('%Y-%m-%d')}")
            print()
            date_str = date_obj.strftime('%Y%m%d')
            return date_obj, date_str
        except ValueError:
            print("❌ 日期格式错误，请输入如 2026-02-19 这样的格式")
            continue


def list_available_newspapers():
    """列出支持的报纸"""
    print("📋 支持的报纸：")
    print("-" * 50)
    for idx, (name, config) in enumerate(NEWSPAPER_CONFIG.items(), 1):
        print(f"{idx}. {name} ({config['description']})")
    print("-" * 50)
    print()


def select_newspaper():
    """选择要抓取的报纸"""
    list_available_newspapers()
    while True:
        user_input = input("👉 请输入报纸名称或序号: ").strip()
        # 处理序号输入
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(NEWSPAPER_CONFIG):
                newspaper_name = list(NEWSPAPER_CONFIG.keys())[idx]
                break
        # 处理名称输入
        elif user_input in NEWSPAPER_CONFIG:
            newspaper_name = user_input
            break
        print("❌ 未找到该报纸，请输入正确名称或序号（如：1 或 人民日报）")
    
    print(f"✅ 已选择：{newspaper_name}")
    print()
    return newspaper_name


def check_dependencies():
    """检查必要依赖"""
    required = {
        'requests': 'requests',
        'PIL': 'pillow',
        'pdf2image': 'pdf2image',
        'dotenv': 'python-dotenv'  # 新增检查dotenv
    }
    missing = []
    
    for pkg_import, pkg_name in required.items():
        try:
            __import__(pkg_import)
        except ImportError:
            missing.append(pkg_name)
    
    if missing:
        print(f"❌ 缺少必要依赖库：{', '.join(missing)}")
        print(f"👉 请运行安装命令：pip install {' '.join(missing)}")
        print("💡 Windows用户额外安装poppler：https://github.com/oschwartz10612/poppler-windows/releases")
        print("💡 Mac用户：brew install poppler")
        return False
    else:
        print("✅ 所有依赖库检查通过")
        print()
    
    # 检查可选依赖
    try:
        import psycopg2
        print("✅ 数据库依赖检查通过")
    except ImportError:
        print("ℹ️ 数据库功能可选，如需使用请安装：pip install psycopg2-binary")
    print()
    
    return True

# 导入需要的模块
import datetime
