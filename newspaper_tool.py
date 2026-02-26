#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自媒体报刊抓取与AI整理工具 - 国内免费AI版
✅ 通义千问免费API驱动，国内网络直接用，完全免费
✅ 已填入API Key，无需额外配置，一键运行
"""

import os
import sys
import requests
import datetime
import re
import base64
from PIL import Image
import urllib.parse
import io

# ===================== 已填入你的API Key =====================
TONGYI_API_KEY = "你的API"

# 报纸配置（已修复所有URL，正常日期可稳定下载）
NEWSPAPER_CONFIG = {
    "人民日报": {
        "type": "pdf_dynamic",
        "layout_url_template": "http://paper.people.com.cn/rmrb/pc/layout/{yymm}/{dd}/node_01.html",
        "description": "人民日报",
    },
    "经济日报": {
        "type": "pdf_dynamic",
        "layout_url_template": "http://paper.ce.cn/jjrb/pc/layout/{yymm}/{dd}/node_01.html",
        "description": "中国经济日报",
    },
    "纽约时报": {
        "type": "jpg",
        "url_template": "https://static01.nyt.com/images/{yyyy}/{mm}/{dd}/nytfrontpage/scan.jpg",
        "description": "The New York Times",
    }
}

# 全局配置
REQUEST_TIMEOUT = 30
IMAGE_FOLDER = "newspaper_images"
COPY_FOLDER = "newspaper_copies"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# 通义千问API地址（国内直连）
TONGYI_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# ========================================================================

def print_banner():
    """打印启动横幅"""
    print("=" * 70)
    print("📰 自媒体报刊抓取工具 - 国内免费AI版")
    print("=" * 70)
    print("✅ 通义千问免费AI驱动，已填入API Key，直接运行")
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

def image_to_base64(image_path):
    """将图片转为base64编码（适配AI接口）"""
    try:
        # 打开并压缩图片（减少传输大小）
        img = Image.open(image_path)
        if img.width > 2048 or img.height > 2048:
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 保存到字节流并转base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr = img_byte_arr.getvalue()
        
        base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"
    except Exception as e:
        print(f"❌ 图片转base64失败：{str(e)}")
        return None

def pdf_to_image_base64(pdf_path):
    """将PDF第一页转为图片并编码为base64"""
    try:
        from pdf2image import convert_from_path
        
        # 提取PDF第一页（dpi=200保证清晰度）
        print("📄 正在提取PDF第一页并转为图片...")
        pages = convert_from_path(
            pdf_path, 
            first_page=1, 
            last_page=1, 
            dpi=200,
            poppler_path=None  # Windows用户需指定poppler路径，如 r'C:\poppler-24.02.0\Library\bin'
        )
        
        # 处理图片
        img = pages[0]
        if img.width > 2048 or img.height > 2048:
            img.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 转为base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85)
        img_byte_arr = img_byte_arr.getvalue()
        
        base64_data = base64.b64encode(img_byte_arr).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"
    
    except ImportError:
        print("❌ 缺少PDF处理库，请先安装：pip install pdf2image")
        print("💡 Windows用户还需下载poppler：https://github.com/oschwartz10612/poppler-windows/releases")
        return None
    except Exception as e:
        print(f"❌ PDF转图片失败：{str(e)}")
        return None

def analyze_with_free_ai(file_path, newspaper_name, date_str):
    """调用通义千问免费AI提取图片/PDF精华内容"""
    print(f"🤖 开始AI解析 {newspaper_name} 内容...")
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件 {file_path} 不存在")
        return None

    # 1. 处理文件，转为base64
    if file_path.endswith(".pdf"):
        base64_data = pdf_to_image_base64(file_path)
    else:
        base64_data = image_to_base64(file_path)
    
    if not base64_data:
        print("❌ 文件转base64失败，无法进行AI解析")
        return None

    # 2. 构建AI请求
    headers = {
        "Authorization": f"Bearer {TONGYI_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }

    # 从环境变量加载提示词
    default_prompt = """
请严格按照以下要求分析《{newspaper_name}》{date_str}的头版内容：
1. 核心头条：提取3-5条最重要的新闻，每条包含【标题原文】+ 50-80字的核心内容摘要（务必准确）
2. 关键数据：提取版面中的量化数据（如经济数据、统计数字、赛事成绩等）
3. 核心主题：用50字以内总结当日报纸的核心主题（高度概括）

输出格式必须严格遵循：
=== 《{newspaper_name}》{date_str} 精华内容 ===
【头条新闻1】标题原文
📝 核心内容：[50-80字摘要]

【头条新闻2】标题原文
📝 核心内容：[50-80字摘要]

【头条新闻3】标题原文
📝 核心内容：[50-80字摘要]

📊 关键数据：
• 数据1（注明数据含义）
• 数据2（注明数据含义）

💡 今日核心主题：
[50字以内的总结]
"""
    prompt_template = os.getenv("AI_ANALYSIS_PROMPT", default_prompt)
    prompt = prompt_template.format(newspaper_name=newspaper_name, date_str=date_str)

    # 构建请求体
    payload = {
        "model": "qwen-vl-plus",  # 通义千问免费多模态模型（支持图文解析）
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": base64_data}
                    ]
                }
            ]
        },
        "parameters": {
            "result_format": "text",
            "temperature": 0.1,  # 低随机性，保证结果准确
            "max_tokens": 2000,
            "top_p": 0.9
        }
    }

    # 3. 调用AI接口
    try:
        print("🚀 正在调用通义千问AI解析...（请稍候）")
        response = requests.post(
            TONGYI_API_URL,
            headers=headers,
            json=payload,
            timeout=60  # 延长超时时间，适配AI处理
        )
        response.raise_for_status()
        result = response.json()

        # 修正：适配通义千问返回的choices结构
        try:
            if "output" in result and "choices" in result["output"] and len(result["output"]["choices"]) > 0:
                message = result["output"]["choices"][0]["message"]
                content = message["content"]
                
                # 如果content是列表，把里面的text拼接起来
                if isinstance(content, list):
                    ai_content = "\n".join([item.get("text", "") for item in content])
                else:
                    ai_content = content.strip()

                if ai_content:
                    print("✅ AI解析完成！")
                    print("-" * 70)
                    print(ai_content)
                    print("-" * 70)
                    return ai_content
                else:
                    print("❌ AI返回空内容，可能是解析失败")
                    return None
            else:
                print(f"❌ AI返回格式异常：{result}")
                return None
        except Exception as e:
            print(f"⚠️  解析AI返回内容时出错：{str(e)}，尝试直接提取内容")
            # 备用提取方案，兼容多种返回格式
            try:
                # 先兼容旧版text格式
                if "output" in result and "text" in result["output"]:
                    ai_content = result["output"]["text"].strip()
                else:
                    # 再尝试嵌套content格式
                    ai_content = result["output"]["choices"][0]["message"]["content"][0]["text"]
                if ai_content:
                    print("✅ AI解析完成！")
                    print("-" * 70)
                    print(ai_content)
                    print("-" * 70)
                    return ai_content
            except:
                print(f"❌ 无法解析AI返回内容：{result}")
                return None

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        print(f"❌ AI调用失败：HTTP错误 {error_code}")
        if error_code == 401:
            print("💡 请检查你的API Key是否正确，或是否已激活通义千问服务")
        elif error_code == 429:
            print("💡 免费调用次数已达上限，请明天再试（每日有免费额度）")
        elif error_code == 500:
            print("💡 AI服务暂时不可用，请稍后重试")
        return None
    except requests.exceptions.Timeout:
        print("❌ AI调用超时，网络或服务器繁忙")
        return None
    except Exception as e:
        print(f"❌ AI解析失败：{str(e)}")
        return None

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

def check_dependencies():
    """检查必要依赖"""
    required = {
        'requests': 'requests',
        'PIL': 'pillow',
        'pdf2image': 'pdf2image'
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
        sys.exit(1)
    else:
        print("✅ 所有依赖库检查通过")
        print()

def main():
    """主函数"""
    # 启动横幅
    print_banner()

    # 检查依赖
    check_dependencies()

    # 检查API Key有效性
    if not TONGYI_API_KEY or TONGYI_API_KEY == "your-dashscope-api-key":
        print("❌ 错误：未配置API Key")
        sys.exit(1)
    else:
        print("✅ API Key 配置完成")
        print()

    # 初始化文件夹
    init_folders()

    # 选择日期
    date_obj, date_str = select_date()

    # 选择报纸
    newspaper_name = select_newspaper()

    # 下载报纸文件
    file_path = download_newspaper_file(newspaper_name, date_obj, date_str)
    if not file_path:
        print("\n❌ 报纸文件下载失败，程序退出")
        sys.exit(1)

    # AI解析
    user_choice = input("\n是否用AI提取精华内容？(y/n): ").strip().lower()
    if user_choice == 'y':
        content = analyze_with_free_ai(file_path, newspaper_name, date_str)
        if content:
            # 保存内容
            user_choice = input("\n是否保存提取的精华内容？(y/n): ").strip().lower()
            if user_choice == 'y':
                save_content_to_file(content, newspaper_name, date_str)

    print("\n👋 操作完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序异常：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)