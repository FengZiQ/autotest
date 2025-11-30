# -*- coding: utf-8 -*-
import os
import time
import logging
import subprocess
from utils.path_util import get_path
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction


logger = logging.getLogger('android_client')


class AndroidAutomationTool:
    def __init__(self, appium_server_url='http://localhost:4723'):
        """
        初始化Android自动化工具类
        :param appium_server_url: Appium服务器地址
        """
        self.driver = None
        self.appium_server_url = appium_server_url
        self.touch_action = None
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
            self.touch_action = TouchAction(self.driver)
            logger.info("Appium驱动启动成功")
            return self.driver
        except Exception as e:
            logger.warning(f"驱动启动失败: {str(e)}")
            return None

    def quit_driver(self):
        """退出驱动"""
        if self.driver:
            self.driver.quit()
            logger.debug("Appium驱动已退出")

    def start_app(self, app_package, app_activity):
        try:
            if self.driver:
                subprocess.run(
                    ['adb', 'shell', 'am', 'force-stop', app_package]
                )
                time.sleep(3)
                subprocess.run(
                    ['adb', 'shell', 'am', 'start', '-n', f'{app_package}/{app_activity}']
                )
                logger.info(f'{app_package}应用启动')
        except Exception as e:
            logger.warning(f'{app_package}应用启动失败。错误信息：{e}')

    def stop_app(self, app_package):
        try:
            if self.driver:
                subprocess.run(
                    ['adb', 'shell', 'am', 'force-stop', app_package]
                )
                logger.info(f'{app_package}应用停止')
        except Exception as e:
            logger.warning(f'{app_package}应用停止失败。错误信息：{e}')

    def find_element(self, locator, timeout=15):
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
            print(f"元素查找成功: {locator}")
            return element
        except TimeoutException:
            logger.warning(f"元素查找超时: {locator}")
            return None

    def click_element(self, locator, timeout=10, loading_time=1):
        """
        点击元素
        :param locator: 定位器元组
        :param timeout: 超时时间
        :param loading_time: 页面完成加载时间
        :return: 操作是否成功
        """
        element = self.find_element(locator, timeout)
        if element:
            try:
                time.sleep(loading_time)
                element.click()
                print(f"元素点击成功: {locator}")
                return True
            except Exception as e:
                logger.warning(f"元素点击失败: {str(e)}")
                return False
        return False

    def send_keys(self, locator, text, timeout=10, loading_time=0.5):
        """
        输入文本
        :param locator: 定位器元组
        :param text: 要输入的文本
        :param timeout: 超时时间
        :param loading_time: 输入文本后触发UI页面变化加载时间
        :return: 操作是否成功
        """
        element = self.find_element(locator, timeout)
        if element:
            try:
                element.clear()
                element.send_keys(text)
                time.sleep(loading_time)
                print(f"文本输入成功: {text}")
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
                print(f"获取文本成功: {text}")
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
            print(f"元素可见: {locator}")
            return True
        except TimeoutException:
            logger.warning(f"元素不可见: {locator}")
            return False

    # 滑动和手势操作方法
    def swipe(self, start_x, start_y, end_x, end_y, duration=800):
        """
        滑动操作
        :param start_x: 起始x坐标
        :param start_y: 起始y坐标
        :param end_x: 结束x坐标
        :param end_y: 结束y坐标
        :param duration: 滑动持续时间(毫秒)
        :return: 操作是否成功
        """
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            print(f"滑动操作: 从({start_x}, {start_y})到({end_x}, {end_y})")
            return True
        except Exception as e:
            logger.warning(f"滑动操作失败: {str(e)}")
            return False

    def swipe_up(self, duration=800):
        """向上滑动"""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] * 0.5
            start_y = size['height'] * 0.8
            end_x = size['width'] * 0.5
            end_y = size['height'] * 0.2
            return self.swipe(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            logger.warning(f"向上滑动失败: {str(e)}")
            return False

    def swipe_down(self, duration=800):
        """向下滑动"""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] * 0.5
            start_y = size['height'] * 0.2
            end_x = size['width'] * 0.5
            end_y = size['height'] * 0.8
            return self.swipe(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            logger.warning(f"向下滑动失败: {str(e)}")
            return False

    def swipe_left(self, duration=800):
        """向左滑动"""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] * 0.8
            start_y = size['height'] * 0.5
            end_x = size['width'] * 0.2
            end_y = size['height'] * 0.5
            return self.swipe(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            logger.warning(f"向左滑动失败: {str(e)}")
            return False

    def swipe_right(self, duration=800):
        """向右滑动"""
        try:
            size = self.driver.get_window_size()
            start_x = size['width'] * 0.2
            start_y = size['height'] * 0.5
            end_x = size['width'] * 0.8
            end_y = size['height'] * 0.5
            return self.swipe(start_x, start_y, end_x, end_y, duration)
        except Exception as e:
            logger.warning(f"向右滑动失败: {str(e)}")
            return False

    def scroll_to_element(self, start_locator, end_locator):
        """
        从一个元素滚动到另一个元素
        :param start_locator: 起始元素定位器
        :param end_locator: 目标元素定位器
        :return: 操作是否成功
        """
        try:
            start_element = self.find_element(start_locator)
            end_element = self.find_element(end_locator)
            if start_element and end_element:
                self.driver.scroll(start_element, end_element)
                print(f"滚动操作: 从{start_locator}到{end_locator}")
                return True
            return False
        except Exception as e:
            logger.warning(f"滚动操作失败: {str(e)}")
            return False

    def drag_and_drop(self, source_locator, target_locator):
        """
        拖拽元素
        :param source_locator: 源元素定位器
        :param target_locator: 目标元素定位器
        :return: 操作是否成功
        """
        try:
            source_element = self.find_element(source_locator)
            target_element = self.find_element(target_locator)
            if source_element and target_element:
                self.touch_action.long_press(source_element).move_to(target_element).release().perform()
                print(f"拖拽操作: 从{source_locator}到{target_locator}")
                return True
            return False
        except Exception as e:
            logger.warning(f"拖拽操作失败: {str(e)}")
            return False

    def long_press(self, locator, duration=1000):
        """
        长按元素
        :param locator: 元素定位器
        :param duration: 长按持续时间(毫秒)
        :return: 操作是否成功
        """
        try:
            element = self.find_element(locator)
            if element:
                self.touch_action.long_press(element, duration=duration).release().perform()
                print(f"长按操作: {locator}, 持续时间: {duration}ms")
                return True
            return False
        except Exception as e:
            logger.warning(f"长按操作失败: {str(e)}")
            return False

    def tap(self, x, y, duration=500):
        """
        点击坐标点
        :param x: x坐标
        :param y: y坐标
        :param duration: 点击持续时间(毫秒)
        :return: 操作是否成功
        """
        try:
            self.touch_action.tap(x=x, y=y, duration=duration).perform()
            print(f"坐标点击: ({x}, {y})")
            return True
        except Exception as e:
            logger.warning(f"坐标点击失败: {str(e)}")
            return False

    def tap_element(self, locator, duration=500):
        """
        点击元素中心点
        :param locator: 元素定位器
        :param duration: 点击持续时间(毫秒)
        :return: 操作是否成功
        """
        try:
            element = self.find_element(locator)
            if element:
                location = element.location
                size = element.size
                x = location['x'] + size['width'] / 2
                y = location['y'] + size['height'] / 2
                return self.tap(x, y, duration)
            return False
        except Exception as e:
            logger.warning(f"元素点击失败: {str(e)}")
            return False

    def pinch(self, locator=None, percent=200, steps=50):
        """
        捏合手势(缩小)
        :param locator: 元素定位器(可选)
        :param percent: 缩放百分比
        :param steps: 步骤数
        :return: 操作是否成功
        """
        try:
            if locator:
                element = self.find_element(locator)
                self.driver.pinch(element, percent, steps)
                print(f"捏合操作(元素): {locator}")
            else:
                self.driver.pinch(percent=percent, steps=steps)
                print("捏合操作(屏幕)")
            return True
        except Exception as e:
            logger.warning(f"捏合操作失败: {str(e)}")
            return False

    def zoom(self, locator=None, percent=200, steps=50):
        """
        放大手势
        :param locator: 元素定位器(可选)
        :param percent: 缩放百分比
        :param steps: 步骤数
        :return: 操作是否成功
        """
        try:
            if locator:
                element = self.find_element(locator)
                self.driver.zoom(element, percent, steps)
                print(f"放大操作(元素): {locator}")
            else:
                self.driver.zoom(percent=percent, steps=steps)
                print("放大操作(屏幕)")
            return True
        except Exception as e:
            logger.warning(f"放大操作失败: {str(e)}")
            return False

    def multi_touch_zoom(self, element=None):
        """
        多点触控放大(使用MultiAction)
        :param element: 元素(可选)
        :return: 操作是否成功
        """
        try:
            size = self.driver.get_window_size()
            center_x = size['width'] / 2
            center_y = size['height'] / 2

            action1 = TouchAction(self.driver)
            action2 = TouchAction(self.driver)

            if element:
                action1 = action1.long_press(element, center_x - 100, center_y).move_to(element, center_x - 200,
                                                                                        center_y).release()
                action2 = action2.long_press(element, center_x + 100, center_y).move_to(element, center_x + 200,
                                                                                        center_y).release()
            else:
                action1 = action1.long_press(x=center_x - 100, y=center_y).move_to(x=center_x - 200,
                                                                                   y=center_y).release()
                action2 = action2.long_press(x=center_x + 100, y=center_y).move_to(x=center_x + 200,
                                                                                   y=center_y).release()

            multi_action = MultiAction(self.driver)
            multi_action.add(action1, action2)
            multi_action.perform()

            print("多点触控放大操作完成")
            return True
        except Exception as e:
            logger.warning(f"多点触控放大失败: {str(e)}")
            return False

    def multi_touch_pinch(self, element=None):
        """
        多点触控捏合(使用MultiAction)
        :param element: 元素(可选)
        :return: 操作是否成功
        """
        try:
            size = self.driver.get_window_size()
            center_x = size['width'] / 2
            center_y = size['height'] / 2

            action1 = TouchAction(self.driver)
            action2 = TouchAction(self.driver)

            if element:
                action1 = action1.long_press(element, center_x - 200, center_y).move_to(element, center_x - 100,
                                                                                        center_y).release()
                action2 = action2.long_press(element, center_x + 200, center_y).move_to(element, center_x + 100,
                                                                                        center_y).release()
            else:
                action1 = action1.long_press(x=center_x - 200, y=center_y).move_to(x=center_x - 100,
                                                                                   y=center_y).release()
                action2 = action2.long_press(x=center_x + 200, y=center_y).move_to(x=center_x + 100,
                                                                                   y=center_y).release()

            multi_action = MultiAction(self.driver)
            multi_action.add(action1, action2)
            multi_action.perform()

            print("多点触控捏合操作完成")
            return True
        except Exception as e:
            logger.warning(f"多点触控捏合失败: {str(e)}")
            return False

    # 系统操作
    def press_keycode(self, keycode, metastate=None):
        """
        按键操作
        :param keycode: 键码
        :param metastate: 元状态
        :return: 操作是否成功
        """
        try:
            if metastate:
                self.driver.press_keycode(keycode, metastate)
            else:
                self.driver.press_keycode(keycode)
            print(f"按键操作: {keycode}")
            return True
        except Exception as e:
            logger.warning(f"按键操作失败: {str(e)}")
            return False

    def hide_keyboard(self):
        """隐藏键盘"""
        try:
            self.driver.hide_keyboard()
            print("键盘已隐藏")
            return True
        except Exception as e:
            logger.warning(f"隐藏键盘失败: {str(e)}")
            return False

    def get_window_size(self):
        """获取窗口尺寸"""
        try:
            size = self.driver.get_window_size()
            print(f"窗口尺寸: {size}")
            return size
        except Exception as e:
            logger.warning(f"获取窗口尺寸失败: {str(e)}")
            return None

    # 断言方法 - 所有断言方法只返回True或False
    def assert_element_present(self, locator, timeout=5):
        """
        断言元素存在
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: True或False
        """
        result = self.find_element(locator, timeout) is not None
        print(f"断言元素存在 {locator}: {result}")
        return result

    def assert_element_visible(self, locator, timeout=5):
        """
        断言元素可见
        :param locator: 定位器元组
        :param timeout: 超时时间
        :return: True或False
        """
        result = self.wait_until_visible(locator, timeout)
        print(f"断言元素可见 {locator}: {result}")
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
        print(f"断言文本相等: 预期='{expected_text}', 实际='{actual_text}', 结果={result}")
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
        print(f"断言文本包含: 预期包含='{expected_text}', 实际='{actual_text}', 结果={result}")
        return result

    def take_screenshot(self, filename=None):
        """
        截取屏幕截图
        :param filename: 文件名
        :return: 截图文件路径或None
        """
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"

            # 截图
            screenshot_path = get_path('reports', 'screenshots', filename)
            self.driver.get_screenshot_as_file(screenshot_path)

            return screenshot_path
        except Exception as e:
            logger.warning(f"截图失败: {str(e)}")
            return None

    def back(self):
        """按返回键"""
        try:
            self.driver.back()
            return True
        except Exception as e:
            logger.warning(f"返回操作失败: {str(e)}")
            return False

    def get_current_activity(self):
        """获取当前Activity"""
        try:
            activity = self.driver.current_activity
            return activity
        except Exception as e:
            logger.warning(f"获取Activity失败: {str(e)}")
            return None


# 使用示例
if __name__ == "__main__":
    pass



