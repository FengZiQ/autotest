# -*- coding: utf-8 -*-
import time
import logging
import pytest
from config.android_config import test_app_config
from core.android_client import AndroidAutomationTool


# 网易阅读app
@pytest.fixture(scope="session")
def netease_pris():
    # 创建工具实例
    automation_tool = AndroidAutomationTool()
    try:
        # 启动驱动
        automation_tool.setup_driver(test_app_config)
        time.sleep(3)
    except Exception as e:
        logging.warning(f"驱动启动失败，退出测试! 错误信息：{e}")
        pytest.exit('驱动启动失败，退出测试!')

    yield automation_tool

    # 退出驱动
    automation_tool.quit_driver()
