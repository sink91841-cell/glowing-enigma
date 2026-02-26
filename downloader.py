#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载模块 - 负责下载报纸文件（PDF/图片）
"""

import os
import requests
import re
import urllib.parse
from config import NEWSPAPER_CONFIG, IMAGE_FOLDER, USER_AGENT, REQUEST_TIMEOUT
from utils import format_date


def download_newspaper_file(newspaper_name, date_obj, date_str):
    """下载报纸文件（PDF/图片）"""
    print(f"📥 开始下载 {newspaper_name} ({date_obj.strftime('%Y-%m-%d')}) ...")

    config = NEWSPAPER_CONFIG[newspaper_name]
    file_ext = config['type'].split('_')[0]
    filename = f"{newspaper_name}_{date_str}.{file_ext}"
    save_path = os.path.join(IMAGE_FOLDER, filename)

    # 检查文件是否已存在
    if os.path.exists(save_path):
        user_choice = input(f"📁 文件 {filename} 已存在，重新下载？(y/n): ").strip().lower()
        if user_choice != 'y':
            print("✅ 使用已存在的文件")
            return save_path

    headers = {'User-Agent': USER_AGENT, 'Accept': '*/*'}

    try:
        if config['type'] == "pdf_dynamic":
            # 动态提取人民日报/经济日报的PDF链接
            date_formats = format_date(date_obj)
            layout_url = config['layout_url_template'].format(**date_formats)
            print(f"🌐 正在获取版面页: {layout_url}")

            resp = requests.get(layout_url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = 'utf-8'

            # 正则提取PDF链接
            match = re.search(r'href="([^"]+\.pdf)"', resp.text)
            if match:
                relative_pdf = match.group(1)
                pdf_url = urllib.parse.urljoin(layout_url, relative_pdf)
                print(f"✅ 找到PDF地址: {pdf_url}")
            else:
                print("❌ 未找到该日期的报纸PDF，该日期可能停刊或未发布")
                return None

            # 下载PDF
            response = requests.get(pdf_url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True)
        else:
            # 直接下载纽约时报图片
            date_formats = format_date(date_obj)
            cover_url = config['url_template'].format(**date_formats)
            print(f"🌐 正在下载图片: {cover_url}")
            response = requests.get(cover_url, headers=headers, timeout=REQUEST_TIMEOUT, stream=True)

        # 检查响应状态
        response.raise_for_status()

        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # 验证文件
        if file_ext == 'jpg':
            from PIL import Image
            img = Image.open(save_path)
            img.verify()
            print(f"✅ 图片下载成功！尺寸：{img.size[0]}x{img.size[1]}")
        else:
            # 验证PDF文件大小
            file_size = os.path.getsize(save_path) / 1024 / 1024  # MB
            print(f"✅ PDF下载成功！大小：{file_size:.2f} MB")
        
        print(f"📁 保存路径：{save_path}")
        print()
        return save_path

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        print(f"❌ 下载失败：HTTP错误 {error_code}")
        if error_code == 404:
            print("💡 该日期的报纸可能未发布/停刊，建议选择「昨天」的日期重试")
        elif error_code == 403:
            print("💡 访问被拒绝，可能是网站反爬限制，建议稍后再试")
        return None
    except requests.exceptions.Timeout:
        print("❌ 下载超时，网络连接不稳定")
        return None
    except Exception as e:
        print(f"❌ 下载失败：{str(e)}")
        return None
