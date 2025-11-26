# -*- coding: utf-8 -*-
import time
import logging
import pytest
from appium.webdriver.webdriver import AppiumBy
from config.android_config import test_app_config
from core.android_client import AndroidAutomationTool
from core.android_test_executor import AndroidTestExecutor


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
    is_debug = True
    if not is_debug:
        # 启动测试app
        automation_tool.start_app(
            app_package='com.netease.pris',
            app_activity='.activity.PRISActivityFlasScreen'
        )

        # 登录
        automation_tool.click_element(
            locator=(
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="com.netease.pris:id/title" and @text="我的"]'
            )
        )
        login_button = automation_tool.find_element(
            locator=(
                AppiumBy.ID,
                'com.netease.pris:id/button_login'
            ),
            timeout=2
        )
        if login_button:
            automation_tool.click_element(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/button_login'
                )
            )
            automation_tool.send_keys(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_name'
                ),
                text='13717641870'
            )
            automation_tool.send_keys(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_password'
                ),
                text='tester'
            )
            automation_tool.click_element(
                locator=(
                    AppiumBy.ID,
                    'com.netease.pris:id/ui_login_button_login'
                )
            )

    # 创建用例自动化执行器
    executor = AndroidTestExecutor(automation_tool)

    yield executor

    # 退出驱动
    executor.android_tool.quit_driver()
