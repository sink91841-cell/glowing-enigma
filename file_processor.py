#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理模块 - 负责文件转换和内容保存
"""

import os
import base64
import io
from PIL import Image
from config import COPY_FOLDER


def image_to_base64(image_path):
    """将图片转为base64编码（适配AI接口）"""
    try:
        # 打开并压缩图片（减少传输大小）
        img = Image.open(image_path)
        
        # 调整图片大小，确保符合API要求
        max_size = 800  # 更小的尺寸，减少内容审核风险
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 确保图片模式为RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 保存到字节流并转base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)  # 适中的质量
        img_byte_arr = img_byte_arr.getvalue()
        
        # 检查数据大小
        if len(img_byte_arr) > 3 * 1024 * 1024:  # 3MB限制
            print("⚠️  图片数据过大，正在进一步压缩...")
            # 进一步压缩
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=60)
            img_byte_arr = img_byte_arr.getvalue()
        
        base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
        print(f"✅ 图片转base64成功，数据大小：{len(base64_data) / 1024:.2f} KB")
        return base64_data
    except Exception as e:
        print(f"❌ 图片转base64失败：{str(e)}")
        return None


def pdf_to_image_base64(pdf_path):
    """将PDF第一页转为图片并编码为base64"""
    try:
        from pdf2image import convert_from_path
        
        # 提取PDF第一页（降低dpi以减少大小）
        print("📄 正在提取PDF第一页并转为图片...")
        pages = convert_from_path(
            pdf_path, 
            first_page=1, 
            last_page=1, 
            dpi=120,  # 更低的dpi，减少内容审核风险
            poppler_path=None  # Windows用户需指定poppler路径，如 r'C:\poppler-24.02.0\Library\bin'
        )
        
        # 处理图片
        img = pages[0]
        
        # 调整图片大小，确保符合API要求
        max_size = 800  # 更小的尺寸，减少内容审核风险
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 确保图片模式为RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 转为base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=75)  # 适中的质量
        img_byte_arr = img_byte_arr.getvalue()
        
        # 检查数据大小
        if len(img_byte_arr) > 3 * 1024 * 1024:  # 3MB限制
            print("⚠️  图片数据过大，正在进一步压缩...")
            # 进一步压缩
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=60)
            img_byte_arr = img_byte_arr.getvalue()
        
        base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
        print(f"✅ PDF转base64成功，数据大小：{len(base64_data) / 1024:.2f} KB")
        return base64_data
    
    except ImportError:
        print("❌ 缺少PDF处理库，请先安装：pip install pdf2image")
        print("💡 Windows用户还需下载poppler：https://github.com/oschwartz10612/poppler-windows/releases")
        return None
    except Exception as e:
        print(f"❌ PDF转图片失败：{str(e)}")
        return None


def parse_ai_content(content, newspaper_name, date_str):
    """解析AI生成的内容，提取新闻标题和摘要"""
    if not content or not content.strip():
        return []
    
    summaries = []
    lines = content.strip().split('\n')
    current_title = None
    current_summary = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('【头条新闻'):
            # 保存上一条新闻
            if current_title and current_summary:
                summaries.append((newspaper_name, date_str, current_title, ' '.join(current_summary)))
            # 提取新标题
            title_match = line.split('】', 1)
            if len(title_match) > 1:
                current_title = title_match[1].strip()
                current_summary = []
        elif line.startswith('📝 核心内容：') and current_title:
            # 提取摘要
            summary = line.replace('📝 核心内容：', '').strip()
            current_summary.append(summary)
    
    # 保存最后一条新闻
    if current_title and current_summary:
        summaries.append((newspaper_name, date_str, current_title, ' '.join(current_summary)))
    
    return summaries

def save_content_to_file(content, newspaper_name, date_str):
    """保存AI解析后的精华内容"""
    if not content or not content.strip():
        print("❌ 内容为空，无法保存")
        return None

    filename = f"{newspaper_name}_{date_str}_精华内容.txt"
    file_path = os.path.join(COPY_FOLDER, filename)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 精华内容已保存到：{file_path}")
        return file_path
    except Exception as e:
        print(f"❌ 保存失败：{str(e)}")
        return None
