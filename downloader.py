#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载模块 - 负责下载报纸文件（PDF/图片）
"""

import os
import requests
import re
import urllib.parse
import time
from PIL import Image
from config import NEWSPAPER_CONFIG, IMAGE_FOLDER, USER_AGENT, REQUEST_TIMEOUT
from utils import format_date
from logger import logger


def download_newspaper_file(newspaper_name, date_obj, date_str):
    """下载报纸文件（PDF/图片）"""
    logger.info(f"开始下载 {newspaper_name} ({date_obj.strftime('%Y-%m-%d')})")
    print(f"📥 开始下载 {newspaper_name} ({date_obj.strftime('%Y-%m-%d')}) ...")

    config = NEWSPAPER_CONFIG[newspaper_name]
    file_ext = config['type'].split('_')[0]
    filename = f"{newspaper_name}_{date_str}.{file_ext}"
    save_path = os.path.join(IMAGE_FOLDER, filename)

    # 检查文件是否已存在
    if os.path.exists(save_path):
        logger.info(f"文件已存在：{filename}")
        # 自动使用已存在的文件，避免交互式输入
        logger.info(f"使用已存在的文件：{save_path}")
        print("✅ 使用已存在的文件")
        return save_path

    headers = {'User-Agent': USER_AGENT, 'Accept': '*/*'}

    # 创建session，提高连接复用率
    session = requests.Session()
    session.headers.update(headers)

    try:
        if config['type'] == "pdf_dynamic":
            # 动态提取人民日报的PDF链接
            date_formats = format_date(date_obj)
            layout_url = config['layout_url_template'].format(**date_formats)
            logger.debug(f"获取版面页URL：{layout_url}")
            print(f"🌐 正在获取版面页: {layout_url}")

            resp = session.get(layout_url, timeout=(30, REQUEST_TIMEOUT))
            resp.raise_for_status()
            resp.encoding = 'utf-8'

            # 正则提取PDF链接
            match = re.search(r'href="([^"]+\.pdf)"', resp.text)
            if match:
                relative_pdf = match.group(1)
                pdf_url = urllib.parse.urljoin(layout_url, relative_pdf)
                logger.info(f"找到PDF地址：{pdf_url}")
                print(f"✅ 找到PDF地址: {pdf_url}")
            else:
                logger.warning(f"未找到该日期的报纸PDF：{date_str}")
                print("❌ 未找到该日期的报纸PDF，该日期可能停刊或未发布")
                return None

            # 下载PDF
            logger.debug(f"开始下载PDF：{pdf_url}")
            response = session.get(pdf_url, timeout=(30, REQUEST_TIMEOUT), stream=True)
        else:
            # 直接下载纽约时报图片
            date_formats = format_date(date_obj)
            cover_url = config['url_template'].format(**date_formats)
            logger.debug(f"下载图片URL：{cover_url}")
            print(f"🌐 正在下载图片: {cover_url}")
            
            # 添加重试机制，最多重试5次
            max_retries = 5
            retry_count = 0
            response = None
            
            # 增加更详细的超时设置
            connect_timeout = 45  # 连接超时
            read_timeout = 180     # 读取超时
            
            # 配置代理（支持环境变量和系统自动检测）
            proxies = {}
            
            # 1. 首先检查环境变量
            http_proxy = os.getenv('HTTP_PROXY', '') or os.getenv('http_proxy', '')
            https_proxy = os.getenv('HTTPS_PROXY', '') or os.getenv('https_proxy', '')
            
            if http_proxy:
                proxies['http'] = http_proxy
            if https_proxy:
                proxies['https'] = https_proxy
            
            # 2. 如果没有配置代理，尝试从系统获取（Windows）
            if not proxies and os.name == 'nt':
                try:
                    import winreg
                    # 读取Windows系统代理设置
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
                    proxy_enable, _ = winreg.QueryValueEx(key, 'ProxyEnable')
                    if proxy_enable:
                        proxy_server, _ = winreg.QueryValueEx(key, 'ProxyServer')
                        if proxy_server:
                            # 如果代理服务器包含协议，直接使用
                            if '://' in proxy_server:
                                proxies['http'] = proxy_server
                                proxies['https'] = proxy_server
                            else:
                                # 否则添加http://前缀
                                proxies['http'] = f"http://{proxy_server}"
                                proxies['https'] = f"http://{proxy_server}"
                            print(f"🔧 检测到系统代理: {proxy_server}")
                except Exception as e:
                    logger.debug(f"读取系统代理设置失败: {e}")
            
            # 清理空代理
            proxies = {k: v for k, v in proxies.items() if v}
            
            if proxies:
                print(f"🔧 使用代理：{proxies}")
                logger.debug(f"使用代理：{proxies}")
            else:
                print("⚠️  未检测到代理配置，尝试直接连接...")
                print("💡 如果连接失败，请检查VPN是否正确配置系统代理")
                print("💡 或在.env文件中手动配置代理：")
                print("   HTTP_PROXY=http://127.0.0.1:7890")
                print("   HTTPS_PROXY=http://127.0.0.1:7890")
            
            while retry_count < max_retries:
                try:
                    print(f"📥 正在下载... (尝试 {retry_count + 1}/{max_retries})")
                    print(f"   连接超时：{connect_timeout}秒，读取超时：{read_timeout}秒")
                    
                    # 记录开始时间
                    start_time = time.time()
                    
                    # 发送请求
                    response = session.get(
                        cover_url, 
                        timeout=(connect_timeout, read_timeout), 
                        stream=True,
                        allow_redirects=True,
                        proxies=proxies if proxies else None
                    )
                    
                    # 记录响应时间
                    response_time = time.time() - start_time
                    print(f"   响应时间：{response_time:.2f}秒")
                    print(f"   状态码：{response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ 连接成功，开始下载...")
                        # 检查响应头
                        content_length = response.headers.get('Content-Length', '未知')
                        content_type = response.headers.get('Content-Type', '未知')
                        print(f"   文件大小：{content_length} bytes")
                        print(f"   内容类型：{content_type}")
                        break
                    else:
                        print(f"   ❌ 连接失败，状态码：{response.status_code}")
                        # 打印响应头
                        print("   响应头：")
                        for key, value in list(response.headers.items())[:5]:  # 只显示前5个
                            print(f"     {key}: {value}")
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"   正在重试... ({retry_count}/{max_retries})")
                            # 增加超时时间
                            connect_timeout += 15
                            read_timeout += 30
                            # 等待一段时间再重试
                            wait_time = min(5 * (retry_count + 1), 30)
                            print(f"   等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                        else:
                            print("   ❌ 已达到最大重试次数")
                            return None
                except requests.exceptions.ConnectTimeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"连接超时，正在重试... ({retry_count}/{max_retries})")
                        print(f"⚠️  连接超时，正在重试... ({retry_count}/{max_retries})")
                        # 增加超时时间
                        connect_timeout += 15
                        read_timeout += 30
                        # 等待一段时间再重试
                        wait_time = min(5 * (retry_count + 1), 30)
                        print(f"   等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error("纽约时报连接超时，已达到最大重试次数")
                        print("❌ 纽约时报连接超时，已达到最大重试次数")
                        print()
                        print("💡 可能的原因：")
                        print("   - VPN连接不稳定或配置错误")
                        print("   - 纽约时报服务器暂时不可用")
                        print("   - 网络连接不稳定")
                        print()
                        print("💡 建议的解决方案：")
                        print("   1. 检查VPN连接是否正常")
                        print("   2. 尝试更换VPN服务器")
                        print("   3. 稍后再试，可能是临时问题")
                        print("   4. 选择人民日报作为替代")
                        print("   5. 在.env文件中设置代理：HTTPS_PROXY=http://your-proxy:port")
                        print()
                        return None
                except requests.exceptions.ReadTimeout:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"读取超时，正在重试... ({retry_count}/{max_retries})")
                        print(f"⚠️  读取超时，正在重试... ({retry_count}/{max_retries})")
                        # 增加超时时间
                        connect_timeout += 15
                        read_timeout += 30
                        # 等待一段时间再重试
                        wait_time = min(5 * (retry_count + 1), 30)
                        print(f"   等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error("纽约时报读取超时，已达到最大重试次数")
                        print("❌ 纽约时报读取超时，已达到最大重试次数")
                        print()
                        print("💡 可能的原因：")
                        print("   - 网络速度太慢")
                        print("   - VPN连接不稳定")
                        print("   - 纽约时报服务器响应慢")
                        print()
                        print("💡 建议的解决方案：")
                        print("   1. 检查网络速度")
                        print("   2. 尝试更换VPN服务器")
                        print("   3. 稍后再试，可能是临时问题")
                        print("   4. 选择人民日报作为替代")
                        print()
                        return None
                except requests.exceptions.SSLError as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"SSL错误，正在重试... ({retry_count}/{max_retries})")
                        print(f"⚠️  SSL错误：{e}，正在重试... ({retry_count}/{max_retries})")
                        # 等待一段时间再重试
                        wait_time = min(5 * (retry_count + 1), 30)
                        print(f"   等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"纽约时报SSL错误：{e}")
                        print(f"❌ 纽约时报SSL错误：{e}")
                        print()
                        print("💡 可能的原因：")
                        print("   - SSL证书问题")
                        print("   - VPN配置问题")
                        print("   - 网络安全设置")
                        print()
                        print("💡 建议的解决方案：")
                        print("   1. 检查VPN配置")
                        print("   2. 关闭防火墙或安全软件")
                        print("   3. 稍后再试，可能是临时问题")
                        print("   4. 选择人民日报作为替代")
                        print()
                        return None
                except requests.exceptions.ProxyError as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"代理错误，正在重试... ({retry_count}/{max_retries})")
                        print(f"⚠️  代理错误：{e}，正在重试... ({retry_count}/{max_retries})")
                        # 等待一段时间再重试
                        wait_time = min(5 * (retry_count + 1), 30)
                        print(f"   等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"代理错误：{e}")
                        print(f"❌ 代理错误：{e}")
                        print()
                        print("💡 可能的原因：")
                        print("   - 代理配置错误")
                        print("   - 代理服务器不可用")
                        print()
                        print("💡 建议的解决方案：")
                        print("   1. 检查代理配置")
                        print("   2. 尝试其他代理服务器")
                        print("   3. 选择不使用代理")
                        print("   4. 选择人民日报作为替代")
                        print()
                        return None
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        logger.warning(f"下载失败：{str(e)}，正在重试... ({retry_count}/{max_retries})")
                        print(f"⚠️  下载失败：{str(e)}，正在重试... ({retry_count}/{max_retries})")
                        # 等待一段时间再重试
                        wait_time = min(5 * (retry_count + 1), 30)
                        print(f"   等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"纽约时报下载失败：{str(e)}")
                        print(f"❌ 纽约时报下载失败：{str(e)}")
                        print()
                        print("💡 可能的原因：")
                        print("   - VPN连接问题")
                        print("   - 网络连接问题")
                        print("   - 纽约时报服务器问题")
                        print()
                        print("💡 建议的解决方案：")
                        print("   1. 检查VPN连接是否正常")
                        print("   2. 尝试更换VPN服务器")
                        print("   3. 检查网络连接")
                        print("   4. 稍后再试，可能是临时问题")
                        print("   5. 选择人民日报作为替代")
                        print()
                        return None

        # 检查响应状态
        response.raise_for_status()

        # 保存文件
        logger.debug(f"保存文件到：{save_path}")
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # 验证文件
        if file_ext == 'jpg':
            img = Image.open(save_path)
            img.verify()
            logger.info(f"图片下载成功！尺寸：{img.size[0]}x{img.size[1]}")
            print(f"✅ 图片下载成功！尺寸：{img.size[0]}x{img.size[1]}")
        else:
            # 验证PDF文件大小
            file_size = os.path.getsize(save_path) / 1024 / 1024  # MB
            logger.info(f"PDF下载成功！大小：{file_size:.2f} MB")
            print(f"✅ PDF下载成功！大小：{file_size:.2f} MB")
        
        logger.info(f"文件保存路径：{save_path}")
        print(f"📁 保存路径：{save_path}")
        print()
        return save_path

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        logger.error(f"下载失败：HTTP错误 {error_code}")
        print(f"❌ 下载失败：HTTP错误 {error_code}")
        if error_code == 404:
            logger.warning("该日期的报纸可能未发布/停刊")
            print("💡 该日期的报纸可能未发布/停刊，建议选择「昨天」的日期重试")
        elif error_code == 403:
            logger.warning("访问被拒绝，可能是网站反爬限制")
            print("💡 访问被拒绝，可能是网站反爬限制，建议稍后再试")
        return None
    except requests.exceptions.Timeout:
        logger.error("下载超时，网络连接不稳定")
        print("❌ 下载超时，网络连接不稳定")
        return None
    except Exception as e:
        logger.error(f"下载失败：{str(e)}", exc_info=True)
        print(f"❌ 下载失败：{str(e)}")
        return None
