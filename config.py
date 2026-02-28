#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 管理所有环境变量和配置项
"""

import os
from dotenv import load_dotenv

# ===================== 加载配置文件 =====================
# 优先加载用户本地的.env文件（不上传仓库），兜底加载.env.example（示例模板）
load_dotenv()  # 加载 .env（用户本地配置，含真实密钥）
load_dotenv(".env.example", override=False)  # 加载示例配置作为兜底

# -------------------- API配置 --------------------
TONGYI_API_KEY = os.getenv("TONGYI_API_KEY", "")  # 通义千问API Key
TONGYI_API_URL = os.getenv("TONGYI_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")

# -------------------- 百度文心一言API配置 --------------------
ERNIE_API_KEY = os.getenv("ERNIE_API_KEY", "")  # 百度文心一言API Key
ERNIE_API_URL = os.getenv("ERNIE_API_URL", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions")
ERNIE_ACCESS_TOKEN = os.getenv("ERNIE_ACCESS_TOKEN", "")  # 百度文心一言访问令牌

# -------------------- AI提示词配置 --------------------
AI_ANALYSIS_PROMPT = os.getenv("AI_ANALYSIS_PROMPT", "")

# -------------------- 报纸配置 --------------------
NEWSPAPER_CONFIG = {
    "人民日报": {
        "type": os.getenv("PEOPLE_DAILY_TYPE", "pdf_dynamic"),
        "layout_url_template": os.getenv("PEOPLE_DAILY_LAYOUT_URL", "http://paper.people.com.cn/rmrb/pc/layout/{yymm}/{dd}/node_01.html"),
        "description": os.getenv("PEOPLE_DAILY_DESC", "人民日报"),
    },
    "纽约时报": {
        "type": os.getenv("NYTIMES_TYPE", "jpg"),
        "url_template": os.getenv("NYTIMES_URL_TEMPLATE", "https://static01.nyt.com/images/{yyyy}/{mm}/{dd}/nytfrontpage/scan.jpg"),
        "description": os.getenv("NYTIMES_DESC", "The New York Times"),
    }
}

# -------------------- 全局配置 --------------------
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
IMAGE_FOLDER = os.getenv("IMAGE_FOLDER", "newspaper_images")
COPY_FOLDER = os.getenv("COPY_FOLDER", "newspaper_copies")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# -------------------- AI模型参数配置 --------------------
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", 0.1))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 2000))
AI_TOP_P = float(os.getenv("AI_TOP_P", 0.9))

# -------------------- 数据库配置 --------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "newspaper_db")
