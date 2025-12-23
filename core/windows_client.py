# -*- coding: utf-8 -*-
import logging
import time
from airtest.core.cv import Template
from utils.path_util import get_path
from config.windows_app_config import config_data
from airtest.core.api import exists, touch, text, swipe, ST, assert_exists, assert_not_exists, snapshot, wait, keyevent, set_clipboard


logger = logging.getLogger('windows_client')


class WinAppHandel:
    def __init__(self, app_path):
        self.app_path = app_path
        self.app_feature_dir = get_path('resources', 'image', 'app_feature')
        self.assert_feature_dir = get_path('resources', 'image', 'assert')
        self.fail_img = get_path('reports', 'screenshots')
        self.fail_img_quality = 10
        self.find_timeout = 10
        ST.FIND_TIMEOUT = self.find_timeout

    def start_app(self):
        pass

    def close_app(self):
        pass

    def find_feature(self, feature_name, threshold=0.7, target_pos=5, rgb=False):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param target_pos: 定位特征图片点击位置
        :param rgb: 识别结果是否使用rgb三通道进行校验
        :return: Template或False
        """
        try:
            template = Template(
                filename=f'{self.app_feature_dir}/{feature_name}.png',
                threshold=threshold,
                target_pos=target_pos,
                resolution=config_data.get('resolution'),
                rgb=rgb
            )
            pos = exists(template)
            if pos:
                logger.debug(f'{feature_name}屏幕坐标为：{pos}')
                return template
            else:
                return False
        except Exception as e:
            logger.error(f'未找到{feature_name}！错误信息：{e}')

    def click(self, feature_name, retry=3, interval=2, threshold=0.7, target_pos=5, rgb=False, right_click=False):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param retry: 重试次数
        :param interval: 重试等待时间间隔
        :param threshold: 匹配特征精度值0~1
        :param target_pos: 定位特征图片点击位置
        :param rgb: 识别结果是否使用rgb三通道进行校验
        :param right_click: 是否鼠标右键
        """
        """带重试机制的图像识别点击"""
        for attempt in range(retry):
            try:
                touch(
                    self.find_feature(
                        feature_name=f'{self.app_feature_dir}/{feature_name}.png',
                        target_pos=target_pos,
                        threshold=threshold,
                        rgb=rgb
                    ),
                    right_click=right_click
                )
            except:
                time.sleep(interval)
                if attempt == retry - 1:
                    logger.error(f"{feature_name} 点击失败!")

    def input_text(self, feature_name, threshold=0.7, target_pos=5, input_text='', time_sleep=0.5):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param target_pos: 定位特征图片点击位置
        :param input_text: 输入文本
        :param time_sleep: 输入文本后等待时间
        """
        self.click(
            feature_name=f'{self.app_feature_dir}/{feature_name}.png',
            threshold=threshold,
            target_pos=target_pos
        )
        text(input_text)
        time.sleep(time_sleep)

    def click_if_feature(self, feature_name, if_feature, threshold=0.7, target_pos=5, right_click=False, timeout=15):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param if_feature: 条件定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param timeout: 条件特征等待时长
        :param target_pos: 定位特征图片点击位置
        :param right_click: 是否鼠标右键
        """
        n = 0
        while True:
            try:
                if wait(
                    Template(
                        filename=f'{self.app_feature_dir}/{if_feature}.png',
                        threshold=threshold
                    ),
                        timeout=int(timeout/3)
                ):
                    self.click(
                        feature_name=f'{self.app_feature_dir}/{feature_name}.png',
                        threshold=threshold,
                        target_pos=target_pos,
                        right_click=right_click
                    )
                    break
            except:
                n += 1
                if n == 3:
                    break

    def click_if_not_feature(self, feature_name, if_feature, threshold=0.7, target_pos=5, right_click=False, timeout=10):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param if_feature: 条件定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param timeout: 条件特征消失等待时长
        :param target_pos: 定位特征图片点击位置
        :param right_click: 是否鼠标右键
        """
        n = 0
        while True:
            try:
                if wait(
                    Template(
                        filename=f'{self.app_feature_dir}/{if_feature}.png',
                        threshold=threshold
                    ),
                        timeout=1
                ):
                    n += 1
                    time.sleep(timeout/10)
                    if n == 10:
                        break
            except:
                self.click(
                    feature_name=f'{self.app_feature_dir}/{feature_name}.png',
                    threshold=threshold,
                    target_pos=target_pos,
                    right_click=right_click
                )
                break

    def swipe(self, feature_name1, feature_name2, threshold=0.7, target_pos=5):
        feature1 = self.find_feature(feature_name1, threshold=threshold, target_pos=target_pos)
        feature2 = self.find_feature(feature_name2, threshold=threshold, target_pos=target_pos)
        if feature1 and feature2:
            swipe(v1=feature1, v2=feature2)

    def other_operate(self, operate_info: dict):
        try:
            for key, value in operate_info:
                if key == 'keyevent':
                    if isinstance(value, list):
                        [keyevent(operate) for operate in value]
                    elif isinstance(value, str):
                        keyevent(value)
                elif key == 'set_clipboard':
                    set_clipboard(value)
        except Exception as e:
            logger.warning(f'{operate_info}执行失败！错误信息：{e}')

    def assert_feature_exist(self, feature_name, threshold=0.9, rgb=False, timeout=3):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param rgb: 识别结果是否使用rgb三通道进行校验
        :param timeout: 断言特征匹配时长
        :return: (True, None) 或 (False, '失败截图文件绝对路径')
        """
        ST.FIND_TIMEOUT = timeout
        ST.THRESHOLD_STRICT = threshold
        template = self.find_feature(
            feature_name=f'{self.assert_feature_dir}/{feature_name}.png',
            rgb=rgb
        )
        try:
            if template:
                pos = assert_exists(template)
                logger.info(f'{feature_name}存在，屏幕坐标为：{pos}。断言成功^_^')
                return True, None
        except Exception as e:
            # 截取当前屏幕
            fail_img_path = self.take_screenshot()
            logger.info(f'{feature_name}存在。断言失败-_-| 屏幕截图：{fail_img_path}')
            logger.warning(e)
            return False, fail_img_path
        finally:
            ST.FIND_TIMEOUT = self.find_timeout

    def assert_feature_not_exist(self, feature_name, threshold=0.9, rgb=False, timeout=3):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param rgb: 识别结果是否使用rgb三通道进行校验
        :param timeout: 断言特征匹配时长
        :return: (True, None) 或 (False, '失败截图文件绝对路径')
        """
        ST.FIND_TIMEOUT_TMP = timeout
        ST.THRESHOLD_STRICT = threshold
        template = self.find_feature(
            feature_name=f'{self.assert_feature_dir}/{feature_name}.png',
            rgb=rgb
        )
        try:
            if template:
                pos = assert_not_exists(template)
                # 截取当前屏幕
                fail_img_path = self.take_screenshot()
                logger.warning(f'{feature_name}存在，屏幕坐标为：{pos}。断言失败-_-| 屏幕截图：{fail_img_path}')
                return False, fail_img_path
        except:
            logger.info(f'{feature_name}不存在。断言成功^_^')
            return True, None

    def take_screenshot(self, filename=None):
        """
        截取屏幕截图
        :param filename: 文件名
        :return: 截图文件路径或None
        """
        try:
            if filename is None:
                filename = f"screenshot_{int(time.time())}.png"

            # 截图文件绝对路径
            ST.LOG_DIR = self.fail_img
            snapshot(filename=filename, quality=self.fail_img_quality)

            return get_path(self.fail_img, filename)
        except Exception as e:
            logger.warning(f"截图失败: {str(e)}")
            return None
        finally:
            ST.LOG_DIR = None
