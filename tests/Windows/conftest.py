# -*- coding: utf-8 -*-
import os
import pytest
from pytest_html import extras
from core.airtest_client import AirtestClient
from core.airtest_executor import AirtestTestExecutor


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


@pytest.fixture(scope="function")
def app_a_executor(app_a):
    # 创建用例自动化执行器
    executor = AirtestTestExecutor(app_a)

    yield executor

    # 重置一下step_screenshots
    executor.step_screenshots = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """处理测试报告"""
    outcome = yield
    report = outcome.get_result()
    report_extras = getattr(report, "extras", [])

    # 处理测试步骤截图
    if hasattr(item, 'funcargs'):
        # 检查是否有测试执行器的参数
        for arg_name, arg_value in item.funcargs.items():
            if hasattr(arg_value, 'get_step_screenshots'):
                # 获取步骤截图信息
                step_screenshots = arg_value.get_step_screenshots()

                for screenshot_info in step_screenshots:
                    if os.path.exists(screenshot_info):
                        # 添加截图到报告extras
                        # report_extras.append(
                        #     extras.image(screenshot_info, name=screenshot_info)
                        # )

                        # 以URL形式嵌入截图
                        screenshot_name = screenshot_info.split('/')[-1]
                        report_extras.append(
                            extras.url(
                                content=f'http://localhost:63342/autotest/reports/screenshots/{screenshot_name}',
                                name=f'<br>{screenshot_name}<br>'
                            )
                        )

    report.extras = report_extras
