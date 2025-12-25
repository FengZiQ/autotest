# -*- coding: utf-8 -*-
import os
import logging
import pytest
import datetime
from pytest_html import extras
from core.airtest_client import AirtestClient


@pytest.fixture(scope="session")
def app_8():
    # 启动应用
    client_8 = AirtestClient(os.getenv('8_path'))
    client_8.app_feature_dir = r''
    client_8.assert_feature_dir = r''
    client_8.start_windows_app()
    client_8.connect_windows_app(title=os.getenv('8_title'))

    yield client_8

    client_8.close_windows_app(title=os.getenv('8_title'))


@pytest.fixture(scope="session")
def app_a():
    # 启动应用
    client_a = AirtestClient(os.getenv('a_path'))
    client_a.app_feature_dir = r''
    client_a.assert_feature_dir = r''
    client_a.start_windows_app()
    client_a.connect_windows_app(title=os.getenv('a_title'))

    yield client_a

    client_a.close_windows_app(title=os.getenv('a_title'))


# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """处理测试报告"""
#     outcome = yield
#     report = outcome.get_result()

    # # 只在测试函数调用阶段处理
    # if report.when == "call":
    #
    #     report_extras = getattr(report, "extras", [])
    #
    #     # 失败时截图
    #     if report.failed and hasattr(item, 'fixturenames') and 'windows_device' in item.fixturenames:
    #         # 获取测试名称（安全处理特殊字符）
    #         test_name = report.nodeid.split("::")[-1]
    #         safe_test_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in test_name)
    #         timestamp = datetime.datetime.now().strftime("%H%M%S")
    #         screenshot_name = f"{safe_test_name}_{timestamp}.png"
    #
    #
    #         # 使用airtest截图
    #         try:
    #             # 获取windows_device fixture实例
    #             windows_device_fixture = item.funcargs.get('windows_device')
    #             if windows_device_fixture:
    #                 # 使用设备实例进行截图
    #                 # snapshot(screenshot_path)
    #                 # logging.info(f"测试失败截图已保存至: {screenshot_path}")
    #
    #                 # 添加到报告
    #                 report_extras.append(extras.png(f'screenshots/{screenshot_name}'))
    #         except Exception as e:
    #             logging.error(f"截图失败: {str(e)}")
    #
    #     report.extras = report_extras