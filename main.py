#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主入口文件 - 启动自媒体报刊抓取工具
"""

import sys
from utils import print_banner, check_dependencies
from config import TONGYI_API_KEY
from services.newspaper_tool import NewspaperTool


def main():
    """主函数"""
    # 启动横幅
    print_banner()

    # 检查依赖
    check_dependencies()

    # 检查API Key有效性
    if not TONGYI_API_KEY or TONGYI_API_KEY == "your-dashscope-api-key":
        print("❌ 错误：未配置通义千问API Key！")
        print("💡 请复制 .env.example 为 .env，然后在.env文件中填写你的API Key")
        sys.exit(1)
    else:
        print("✅ API Key 配置完成")
        print()

    # 初始化并运行工具
    tool = NewspaperTool()
    tool.run()


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
