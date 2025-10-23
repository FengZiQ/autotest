# -*- coding: utf-8 -*-
import logging
import pytest
from airtest.core.api import *
from pywinauto import Application
from config.app_config import config_data
from utils.kill_process import kill_process_by_name as kill_app
from core.calculator_page import CalculatorPage


# 计算器测试相关夹具
@pytest.fixture(scope="session")
def windows_device():
    # 启动应用
    Application().start(config_data.get('app_path'))

    # 更稳定的设备连接
    dev = connect_device("Windows:///")
    auto_setup(__file__, devices=[f"Windows:///"])

    yield CalculatorPage(app_device=dev)

    # 增强的清理逻辑
    try:
        kill_app(process_name='CalculatorApp.exe')
    except Exception as e:
        logging.error(f"应用关闭失败: {str(e)}")


@pytest.fixture(scope="function")
def bz_calculator(windows_device):
    windows_device.click_button(
        button_name='C'
    )
    yield
