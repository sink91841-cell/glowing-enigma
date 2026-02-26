#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI客户端模块 - 负责调用AI接口解析报纸内容
"""

import os
import requests
from config import TONGYI_API_KEY, TONGYI_API_URL, AI_ANALYSIS_PROMPT, AI_TEMPERATURE, AI_MAX_TOKENS, AI_TOP_P, USER_AGENT
from file_processor import image_to_base64, pdf_to_image_base64


def analyze_with_free_ai(file_path, newspaper_name, date_str):
    """调用通义千问免费AI提取图片/PDF精华内容"""
    print(f"🤖 开始AI解析 {newspaper_name} 内容...")
    if not os.path.exists(file_path):
        print(f"❌ 错误：文件 {file_path} 不存在")
        return None

    # 检查API Key是否配置
    if not TONGYI_API_KEY or TONGYI_API_KEY == "your-dashscope-api-key":
        print("❌ 错误：未配置通义千问API Key，请在.env文件中设置TONGYI_API_KEY")
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

    # 从配置文件读取提示词，兜底使用默认模板
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
    prompt_template = AI_ANALYSIS_PROMPT if AI_ANALYSIS_PROMPT else default_prompt
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
            "temperature": AI_TEMPERATURE,  # 从配置文件读取
            "max_tokens": AI_MAX_TOKENS,
            "top_p": AI_TOP_P
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
            print("💡 请检查.env文件中的API Key是否正确，或是否已激活通义千问服务")
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
