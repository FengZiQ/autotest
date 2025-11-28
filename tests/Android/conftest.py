# -*- coding: utf-8 -*-
import os
import time
import logging
import pytest
from pytest_html import extras
from appium.webdriver.webdriver import AppiumBy
from config.android_config import test_app_config
from core.android_client import AndroidAutomationTool
from core.android_test_executor import AndroidTestExecutor


# 网易阅读app
@pytest.fixture(scope="session")
def appium_server():
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

    automation_tool.quit_driver()


@pytest.fixture(scope="function")
def netease_pris(appium_server):
    is_debug = True
    if not is_debug:
        # 启动测试app
        appium_server.start_app(
            app_package='com.netease.pris',
            app_activity='.activity.PRISActivityFlasScreen'
        )

        # 登录
        appium_server.click_element(
            locator=(
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="com.netease.pris:id/title" and @text="我的"]'
            )
        )
        login_button = appium_server.find_element(
            locator=(
                AppiumBy.ID,
                'com.netease.pris:id/button_login'
            ),
            timeout=2
        )
        if login_button:
            appium_server.click_element(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/button_login'
                )
            )
            appium_server.send_keys(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_name'
                ),
                text='13717641870'
            )
            appium_server.send_keys(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_password'
                ),
                text='tester'
            )
            appium_server.click_element(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_button_login'
                )
            )

    # 创建用例自动化执行器
    executor = AndroidTestExecutor(appium_server)

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
