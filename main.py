#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主入口文件 - 启动自媒体报刊抓取工具
"""

import sys
from utils import print_banner, check_dependencies
from config import TONGYI_API_KEY
from services.newspaper_tool import NewspaperTool
from logger import logger


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("程序启动")
    logger.info("=" * 50)
    
    # 启动横幅
    print_banner()

    # 检查依赖
    print("🔍 正在检查依赖...")
    if not check_dependencies():
        logger.error("依赖检查失败")
        print("❌ 依赖检查失败，请安装必要的依赖包")
        sys.exit(1)

    # 检查API Key有效性
    print("🔑 正在检查API Key...")
    if not TONGYI_API_KEY or TONGYI_API_KEY == "your-dashscope-api-key":
        logger.warning("未配置通义千问API Key")
        print("⚠️  未配置通义千问API Key")
        print("💡 提示：")
        print("  1. 如果你需要使用AI解析功能，请在.env文件中配置API Key")
        print("  2. 你仍然可以使用下载功能，只是无法使用AI解析")
        print()
    else:
        logger.info("API Key 配置完成")
        print("✅ API Key 配置完成")
        print()

    # 初始化并运行工具
    print("🚀 正在初始化报纸工具...")
    tool = NewspaperTool()
    print("✅ 初始化完成，开始运行...")
    print()
    tool.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("程序被用户中断")
        print("\n\n⏹️ 程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常：{str(e)}", exc_info=True)
        print(f"\n\n❌ 程序异常：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
