#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志模块 - 负责日志记录
"""

import os
import logging
from datetime import datetime
from config import COPY_FOLDER


class Logger:
    """日志管理类"""
    
    def __init__(self, name="NewspaperTool", log_level=logging.INFO):
        """初始化日志系统"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """设置日志处理器"""
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(COPY_FOLDER), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 日志文件名（按日期）
        log_filename = os.path.join(log_dir, f"newspaper_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 文件处理器
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """调试信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """普通信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告信息"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """错误信息"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=False):
        """严重错误"""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message):
        """异常信息（包含堆栈）"""
        self.logger.exception(message)


# 创建全局日志实例
logger = Logger()
