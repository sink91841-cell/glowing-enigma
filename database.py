#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块 - 负责数据库连接和操作
"""

import os
from config import COPY_FOLDER
from logger import logger

# 尝试导入psycopg2，如果失败则标记为不可用
try:
    import psycopg2
    from psycopg2 import OperationalError
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        if not POSTGRES_AVAILABLE:
            self.available = False
            return
        
        self.available = True
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))  # PostgreSQL默认端口
        self.user = os.getenv("DB_USER", "postgres")  # PostgreSQL默认用户
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "newspaper_db")
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        if not self.available:
            logger.warning("数据库功能不可用，请安装psycopg2")
            print("❌ 数据库功能不可用，请安装psycopg2")
            print("💡 运行命令：pip install psycopg2-binary")
            return False
        
        try:
            # 首先尝试连接到默认的postgres数据库
            logger.debug(f"尝试连接默认数据库...")
            temp_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname="postgres"
            )
            temp_conn.autocommit = True
            temp_cursor = temp_conn.cursor()
            
            # 检查目标数据库是否存在
            temp_cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}'")
            exists = temp_cursor.fetchone()
            
            if not exists:
                # 创建数据库
                logger.info(f"数据库 {self.database} 不存在，正在创建...")
                print(f"📋 数据库 {self.database} 不存在，正在创建...")
                temp_cursor.execute(f"CREATE DATABASE {self.database}")
                logger.info(f"数据库 {self.database} 创建成功")
                print(f"✅ 数据库 {self.database} 创建成功")
            
            # 关闭临时连接
            temp_cursor.close()
            temp_conn.close()
            
            # 连接到目标数据库
            logger.debug(f"尝试连接数据库：{self.host}:{self.port}/{self.database}")
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.database
            )
            logger.info("数据库连接成功")
            print("✅ 数据库连接成功")
            self.cursor = self.connection.cursor()
            self.create_table()
            return True
        except OperationalError as e:
            logger.error(f"数据库连接失败：{e}")
            print(f"❌ 数据库连接失败：{e}")
            print("💡 请检查.env文件中的数据库配置")
            return False
    
    def create_table(self):
        """创建数据表"""
        try:
            logger.debug("检查/创建数据表")
            create_table_query = """
            CREATE TABLE IF NOT EXISTS newspaper_summary (
                id SERIAL PRIMARY KEY,
                newspaper VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                title VARCHAR(255) NOT NULL,
                summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (newspaper, date, title)
            );
            """
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("数据表检查/创建成功")
            print("✅ 数据表检查/创建成功")
        except Exception as e:
            logger.error(f"创建数据表失败：{e}")
            print(f"❌ 创建数据表失败：{e}")
    
    def insert_summary(self, newspaper, date, title, summary):
        """插入摘要数据"""
        if not self.available:
            return False
        
        try:
            logger.debug(f"插入数据：{newspaper} - {title}")
            insert_query = """
            INSERT INTO newspaper_summary (newspaper, date, title, summary)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (newspaper, date, title) DO NOTHING
            """
            self.cursor.execute(insert_query, (newspaper, date, title, summary))
            self.connection.commit()
            if self.cursor.rowcount > 0:
                logger.info(f"已保存到数据库：{newspaper} - {title}")
                print(f"✅ 已保存到数据库：{newspaper} - {title}")
                return True
            else:
                logger.info(f"数据已存在，跳过保存：{newspaper} - {title}")
                print(f"ℹ️ 数据已存在，跳过保存：{newspaper} - {title}")
                return False
        except Exception as e:
            logger.error(f"保存到数据库失败：{e}")
            print(f"❌ 保存到数据库失败：{e}")
            return False
    
    def batch_insert_summaries(self, summaries):
        """批量插入摘要数据"""
        if not self.available:
            return False
        
        try:
            logger.debug(f"批量插入数据：{len(summaries)} 条")
            insert_query = """
            INSERT INTO newspaper_summary (newspaper, date, title, summary)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (newspaper, date, title) DO NOTHING
            """
            self.cursor.executemany(insert_query, summaries)
            self.connection.commit()
            logger.info(f"批量保存成功，处理了 {len(summaries)} 条记录")
            print(f"✅ 批量保存成功，处理了 {len(summaries)} 条记录")
            return True
        except Exception as e:
            logger.error(f"批量保存失败：{e}")
            print(f"❌ 批量保存失败：{e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if not self.available:
            return
        
        if self.cursor:
            self.cursor.close()
        if self.connection:
            try:
                self.connection.close()
                logger.info("数据库连接已关闭")
                print("✅ 数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接失败：{e}")
                print(f"⚠️  关闭数据库连接失败：{e}")
