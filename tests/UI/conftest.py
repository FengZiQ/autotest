# -*- coding: utf-8 -*-
import logging
import pytest
import datetime
from pytest_html import extras
from airtest.core.api import *
from pywinauto import Application
from utils.path_util import get_path
from config.app_config import config_data
from utils.kill_process import kill_process_by_name as kill_app
from core.windows_app_test import WinAppTest


# 计算器测试相关夹具
@pytest.fixture(scope="session")
def windows_device():
    # 启动应用
    Application().start(config_data.get('app_path'))

    # 更稳定的设备连接
    dev = connect_device("Windows:///")
    auto_setup(__file__, devices=[f"Windows:///"])

    yield WinAppTest(app_device=dev)

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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """处理测试报告"""
    outcome = yield
    report = outcome.get_result()

    # 只在测试函数调用阶段处理
    if report.when == "call":

        report_extras = getattr(report, "extras", [])

        # 失败时截图
        if report.failed and hasattr(item, 'fixturenames') and 'windows_device' in item.fixturenames:
            # 获取测试名称（安全处理特殊字符）
            test_name = report.nodeid.split("::")[-1]
            safe_test_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in test_name)
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            screenshot_name = f"{safe_test_name}_{timestamp}.png"

            # 确保使用绝对路径
            screenshot_dir = get_path('reports', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)

            # 使用airtest截图
            try:
                # 获取windows_device fixture实例
                windows_device_fixture = item.funcargs.get('windows_device')
                if windows_device_fixture:
                    # 使用设备实例进行截图
                    snapshot(screenshot_path)
                    logging.info(f"测试失败截图已保存至: {screenshot_path}")

                    # 添加到报告
                    report_extras.append(extras.png(f'screenshots/{screenshot_name}'))
            except Exception as e:
                logging.error(f"截图失败: {str(e)}")

        report.extras = report_extras