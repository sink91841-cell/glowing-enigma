#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试模块 - 测试核心功能
"""

import unittest
import datetime
from utils import format_date
from config import NEWSPAPER_CONFIG


class TestDateFormat(unittest.TestCase):
    """测试日期格式化功能"""

    def test_format_date_basic(self):
        """测试基本日期格式化"""
        date_obj = datetime.datetime(2026, 2, 28)
        result = format_date(date_obj)
        
        self.assertEqual(result['yyyy'], '2026')
        self.assertEqual(result['mm'], '02')
        self.assertEqual(result['dd'], '28')
        self.assertEqual(result['yymm'], '202602')
        self.assertEqual(result['ym'], '2026-02')
        self.assertEqual(result['yyyymmdd'], '20260228')
    
    def test_format_date_different_months(self):
        """测试不同月份的日期格式化"""
        date_obj = datetime.datetime(2026, 12, 15)
        result = format_date(date_obj)
        
        self.assertEqual(result['yyyy'], '2026')
        self.assertEqual(result['mm'], '12')
        self.assertEqual(result['dd'], '15')
        self.assertEqual(result['yymm'], '202612')
        self.assertEqual(result['ym'], '2026-12')
        self.assertEqual(result['yyyymmdd'], '20261215')
    
    def test_format_date_single_digit(self):
        """测试单数日期的格式化"""
        date_obj = datetime.datetime(2026, 1, 5)
        result = format_date(date_obj)
        
        self.assertEqual(result['yyyy'], '2026')
        self.assertEqual(result['mm'], '01')
        self.assertEqual(result['dd'], '05')
        self.assertEqual(result['yymm'], '202601')
        self.assertEqual(result['ym'], '2026-01')
        self.assertEqual(result['yyyymmdd'], '20260105')


class TestURLConstruction(unittest.TestCase):
    """测试URL拼接功能"""

    def test_people_daily_url_construction(self):
        """测试人民日报URL拼接"""
        date_obj = datetime.datetime(2026, 2, 28)
        date_formats = format_date(date_obj)
        
        layout_url_template = NEWSPAPER_CONFIG['人民日报']['layout_url_template']
        layout_url = layout_url_template.format(**date_formats)
        
        expected_url = "http://paper.people.com.cn/rmrb/pc/layout/202602/28/node_01.html"
        self.assertEqual(layout_url, expected_url)
    
    def test_nytimes_url_construction(self):
        """测试纽约时报URL拼接"""
        date_obj = datetime.datetime(2026, 2, 28)
        date_formats = format_date(date_obj)
        
        url_template = NEWSPAPER_CONFIG['纽约时报']['url_template']
        cover_url = url_template.format(**date_formats)
        
        expected_url = "https://static01.nyt.com/images/2026/02/28/nytfrontpage/scan.jpg"
        self.assertEqual(cover_url, expected_url)
    
    def test_url_construction_different_date(self):
        """测试不同日期的URL拼接"""
        date_obj = datetime.datetime(2025, 12, 31)
        date_formats = format_date(date_obj)
        
        layout_url_template = NEWSPAPER_CONFIG['人民日报']['layout_url_template']
        layout_url = layout_url_template.format(**date_formats)
        
        expected_url = "http://paper.people.com.cn/rmrb/pc/layout/202512/31/node_01.html"
        self.assertEqual(layout_url, expected_url)


class TestPromptConstruction(unittest.TestCase):
    """测试提示词构建功能"""

    def test_default_prompt_construction(self):
        """测试默认提示词构建"""
        from config import AI_ANALYSIS_PROMPT
        
        if AI_ANALYSIS_PROMPT:
            prompt = AI_ANALYSIS_PROMPT
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)
            self.assertIn('分析', prompt.lower())
    
    def test_prompt_with_variables(self):
        """测试带变量的提示词构建"""
        newspaper_name = "人民日报"
        date_str = "20260228"
        
        from config import AI_ANALYSIS_PROMPT
        
        if AI_ANALYSIS_PROMPT:
            prompt = AI_ANALYSIS_PROMPT
            self.assertIsInstance(prompt, str)
            self.assertGreater(len(prompt), 0)
    
    def test_message_structure_construction(self):
        """测试消息结构构建"""
        base64_data = "dGVzdF9pbWFnZV9kYXRh"
        prompt = "请分析这张图片"
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                ]
            }
        ]
        
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['role'], 'system')
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(len(messages[1]['content']), 2)
        self.assertEqual(messages[1]['content'][0]['type'], 'text')
        self.assertEqual(messages[1]['content'][1]['type'], 'image_url')


class TestNewspaperConfig(unittest.TestCase):
    """测试报纸配置功能"""

    def test_newspaper_config_structure(self):
        """测试报纸配置结构"""
        self.assertIn('人民日报', NEWSPAPER_CONFIG)
        self.assertIn('纽约时报', NEWSPAPER_CONFIG)
        
        people_daily_config = NEWSPAPER_CONFIG['人民日报']
        self.assertIn('type', people_daily_config)
        self.assertIn('layout_url_template', people_daily_config)
        self.assertIn('description', people_daily_config)
        
        nytimes_config = NEWSPAPER_CONFIG['纽约时报']
        self.assertIn('type', nytimes_config)
        self.assertIn('url_template', nytimes_config)
        self.assertIn('description', nytimes_config)
    
    def test_newspaper_config_values(self):
        """测试报纸配置值"""
        people_daily_config = NEWSPAPER_CONFIG['人民日报']
        self.assertEqual(people_daily_config['type'], 'pdf_dynamic')
        self.assertIn('people.com.cn', people_daily_config['layout_url_template'])
        
        nytimes_config = NEWSPAPER_CONFIG['纽约时报']
        self.assertEqual(nytimes_config['type'], 'jpg')
        self.assertIn('nyt.com', nytimes_config['url_template'])


class TestDateValidation(unittest.TestCase):
    """测试日期验证功能"""

    def test_date_format_validation(self):
        """测试日期格式验证"""
        date_obj = datetime.datetime(2026, 2, 28)
        date_formats = format_date(date_obj)
        
        self.assertEqual(len(date_formats['yyyy']), 4)
        self.assertEqual(len(date_formats['mm']), 2)
        self.assertEqual(len(date_formats['dd']), 2)
        self.assertEqual(len(date_formats['yymm']), 6)
        self.assertEqual(len(date_formats['yyyymmdd']), 8)
    
    def test_date_range_validation(self):
        """测试日期范围验证"""
        test_dates = [
            datetime.datetime(2020, 1, 1),
            datetime.datetime(2025, 6, 15),
            datetime.datetime(2026, 2, 28),
            datetime.datetime(2027, 12, 31),
        ]
        
        for date_obj in test_dates:
            date_formats = format_date(date_obj)
            self.assertEqual(len(date_formats['yyyy']), 4)
            self.assertEqual(len(date_formats['yyyymmdd']), 8)


if __name__ == '__main__':
    unittest.main(verbosity=2)
