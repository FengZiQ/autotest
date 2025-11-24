# -*- coding: utf-8 -*-
import time
import logging
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.path_util import get_path


logger = logging.getLogger('android_client')


class AndroidAutomationTool:
    def __init__(self, appium_server_url='http://localhost:4723'):
        """
        初始化Android自动化工具类
        :param appium_server_url: Appium服务器地址
        """
        self.driver = None
        self.appium_server_url = appium_server_url
        self.screenshots = get_path('reports', 'screenshots')
        logger.debug(f"Android自动化工具初始化完成，Appium服务器: {appium_server_url}")

    def setup_driver(self, capabilities):
        """
        设置并启动Appium驱动
        :param capabilities: 设备能力配置字典
        :return: driver对象
        """
        try:
            options = UiAutomator2Options().load_capabilities(capabilities)
            self.driver = webdriver.Remote(
                command_executor=self.appium_server_url,
                options=options
            )
            logger.debug("Appium驱动启动成功")
            return self.driver
        except Exception as e:
            logger.warning(f"驱动启动失败: {str(e)}")
            return None

    def quit_driver(self):
        """退出驱动"""
        if self.driver:
            self.driver.quit()
            logger.debug("Appium驱动已退出")

    def find_element(self, locator, timeout=10):
        """
        查找元素
        :param locator: 定位器元组 (By, value)
        :param timeout: 超时时间
        :return: 元素对象或None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.info(f"元素查找成功: {locator}")
            return element
        except TimeoutException:
            logger.warning(f"元素查找超时: {locator}")
            return None

    def click_element(self, locator, timeout=10):
        """
        点击元素
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: 操作是否成功
        """
        element = self.find_element(locator, timeout)
        if element:
            try:
                element.click()
                logger.info(f"元素点击成功: {locator}")
                return True
            except Exception as e:
                logger.warning(f"元素点击失败: {str(e)}")
                return False
        return False

    def send_keys(self, locator, text, timeout=10):
        """
        输入文本
        :param locator: 定位器元组
        :param text: 要输入的文本
        :param timeout: 超时时间
        :return: 操作是否成功
        """
        element = self.find_element(locator, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                logger.info(f"文本输入成功: {text}")
                return True
            except Exception as e:
                logger.warning(f"文本输入失败: {str(e)}")
                return False
        return False

    def get_element_text(self, locator, timeout=10):
        """
        获取元素文本
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: 元素文本或None
        """
        element = self.find_element(locator, timeout)
        if element:
            try:
                text = element.text
                logger.info(f"获取文本成功: {text}")
                return text
            except Exception as e:
                logger.warning(f"获取文本失败: {str(e)}")
                return None
        return None

    def wait_until_visible(self, locator, timeout=10):
        """
        等待元素可见
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: 元素是否可见
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.info(f"元素可见: {locator}")
            return True
        except TimeoutException:
            logger.warning(f"元素不可见: {locator}")
            return False

    # 断言方法 - 所有断言方法只返回True或False
    def assert_element_present(self, locator, timeout=5):
        """
        断言元素存在
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: True或False
        """
        result = self.find_element(locator, timeout) is not None
        logger.info(f"断言元素存在 {locator}: {result}")
        return result

    def assert_element_visible(self, locator, timeout=5):
        """
        断言元素可见
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: True或False
        """
        result = self.wait_until_visible(locator, timeout)
        logger.info(f"断言元素可见 {locator}: {result}")
        return result

    def assert_text_equals(self, locator, expected_text, timeout=5):
        """
        断言元素文本等于预期文本
        :param locator: 定位器元组
        :param expected_text: 预期文本
        :param timeout: 超时时间
        :return: True或False
        """
        actual_text = self.get_element_text(locator, timeout)
        result = actual_text == expected_text
        logger.info(f"断言文本相等: 预期='{expected_text}', 实际='{actual_text}', 结果={result}")
        return result

    def assert_text_contains(self, locator, expected_text, timeout=5):
        """
        断言元素文本包含预期文本
        :param locator: 定位器元组
        :param expected_text: 预期文本
        :param timeout: 超时时间
        :return: True或False
        """
        actual_text = self.get_element_text(locator, timeout)
        result = expected_text in actual_text if actual_text else False
        logger.info(f"断言文本包含: 预期包含='{expected_text}', 实际='{actual_text}', 结果={result}")
        return result

    def take_screenshot(self, filename=None):
        """
        截取屏幕截图
        :param filename: 文件名
        :return: 截图数据或None
        """
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"

            screenshot_data = self.driver.get_screenshot_as_file(get_path(self.screenshots, filename))
            logger.info(f"截图已保存: {filename}")
            return screenshot_data
        except Exception as e:
            logger.warning(f"截图失败: {str(e)}")
            return None

    def back(self):
        """按返回键"""
        try:
            self.driver.back()
            logger.info("执行返回操作")
            return True
        except Exception as e:
            logger.warning(f"返回操作失败: {str(e)}")
            return False

    def get_current_activity(self):
        """获取当前Activity"""
        try:
            activity = self.driver.current_activity
            logger.info(f"当前Activity: {activity}")
            return activity
        except Exception as e:
            logger.warning(f"获取Activity失败: {str(e)}")
            return None


# 使用示例
if __name__ == "__main__":
    # 设备能力配置
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '6.0',
        'deviceName': 'Mumu emulator',
        'appPackage': 'com.netease.pris',
        'appActivity': 'com.netease.pris.activity.PRISActivityFlasScreen',
        'automationName': 'UiAutomator2',
        'noReset': True,
        "udid": "127.0.0.1:5555"
    }

    # 创建工具实例
    automation_tool = AndroidAutomationTool()

    try:
        # 启动驱动
        driver = automation_tool.setup_driver(desired_caps)
        if not driver:
            logger.info("驱动启动失败，退出测试")
            exit(1)
        # 执行操作
        automation_tool.click_element(
            locator=(
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="com.netease.pris:id/title" and @text="我的"]'
            )
        )
    finally:
        # 退出驱动
        automation_tool.quit_driver()


