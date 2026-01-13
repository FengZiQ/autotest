# -*- coding: utf-8 -*-
import os
from pathlib import Path


class AIConfig:
    """AI相关配置"""
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL = "deepseek-chat"

    # 温度参数，控制生成随机性
    TEMPERATURE = 0.1

    # 最大token数
    MAX_TOKENS = 4000

    # 文件路径配置
    BASE_DIR = Path(__file__).parent.parent
    API_INTERFACE_DIR = BASE_DIR / "resources" / "api_interface"
    TEST_DATA_DIR = BASE_DIR / "tests_data"
    API_DOCS_DIR = BASE_DIR / "docs" / "api_docs"

    # 支持的文档格式
    SUPPORTED_DOC_FORMATS = ['.md', '.txt', '.json', '.yaml', '.yml', '.html']
