# -*- coding: utf-8 -*-
import os
import logging
import time
import subprocess
from airtest.core.cv import Template
from utils.path_util import get_path
from airtest.core.api import touch, text, swipe, snapshot, wait, exists, ST, keyevent, set_clipboard
from airtest.core.api import assert_exists, assert_not_exists, start_app, stop_app, connect_device


logger = logging.getLogger('airtest_client')


class AirtestClient:
    def __init__(self, app_path):
        """
        :param app_path: android应用是传package，windows应用传.exe文件绝对路径
        其他初始化配置：
            app_feature_dir 应用页面特征截图文件夹
            assert_feature_dir 断言应用页面特征截图文件夹
            fail_img 断言失败截图文件夹
            resolution 屏幕分辨率
            fail_img_quality 初始化airtest截图质量
            find_timeout 初始化airtest在屏幕查找特征的超时时间
        """
        self.app_path = app_path
        self.app_feature_dir = None
        self.assert_feature_dir = None
        self.fail_img = get_path('reports', 'screenshots')
        self.resolution = (1920, 1080)
        self.fail_img_quality = 10
        self.find_timeout = 10
        ST.FIND_TIMEOUT = self.find_timeout
        os.makedirs(self.fail_img, exist_ok=True)

    def start_android_app(self, device_info):
        """连接设备，启动测试app"""
        try:
            # 连接设备
            dev = connect_device(uri=device_info)
            if dev:
                # 启动测试app
                start_app(package=self.app_path)
                # 检查测试app是否启动成功
                dev.shell(f'ps | grep {self.app_path}')
                # 等待测试app加载
                time.sleep(3)
                return True
        except Exception as e:
            print(e)
            logger.error(f'app启动失败！错误信息：{e}')
            return False

    def close_android_app(self):
        """关闭测试app"""
        try:
            stop_app(package=self.app_path.get('package'))
        except Exception as e:
            logger.error(f'app关闭失败！错误信息：{e}')

    def start_windows_app(self):
        # 启动测试应用
        try:
            subprocess.Popen(self.app_path)
            logger.info(f'app启动成功^_^')
            return True
        except Exception as e:
            logger.error(f'app启动失败！错误信息：{e}')
            return False

    def connect_windows_app(self, title, timeout=10):
        """连接Windows应用"""
        n = timeout
        dev = None
        while True:
            try:
                dev = connect_device(f"windows:///?title={title}")
                break
            except:
                n -= 1
                time.sleep(1)
                if n == 0:
                    break
        if n > 0:
            logger.info(f'{title} 连接成功^_^')
            return True, dev
        if n == 0:
            logger.warning(f'{title} 连接超时……')
            return False, None

    def close_windows_app(self, title):
        """关闭Windows应用"""
        try:
            dev = self.connect_windows_app(title)[1]
            dev.kill()
            logger.info('app关闭成功^_^')
        except Exception as e:
            logger.error(f'app关闭失败！错误信息：{e}')

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
                filename=feature_name,
                threshold=threshold,
                target_pos=target_pos,
                resolution=self.resolution,
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
        op_id = None
        for attempt in range(retry):
            try:
                op_id = touch(
                    Template(
                        filename=get_path(self.app_feature_dir, feature_name + ".png"),
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
        if op_id:
            return True
        else:
            return False

    def input_text(self, feature_name, threshold=0.7, target_pos=5, input_text='', time_sleep=0.5):
        """
        查找元素
        :param feature_name: 定位特征图片名
        :param threshold: 匹配特征精度值0~1
        :param target_pos: 定位特征图片点击位置
        :param input_text: 输入文本
        :param time_sleep: 输入文本后等待时间
        """
        op_id = self.click(
            feature_name=feature_name,
            threshold=threshold,
            target_pos=target_pos
        )
        text(input_text)
        time.sleep(time_sleep)
        if op_id:
            return True
        else:
            return False

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
        op_id = None
        while True:
            try:
                if wait(
                    Template(
                        filename=get_path(self.app_feature_dir, if_feature + ".png"),
                        threshold=threshold
                    ),
                        timeout=int(timeout/3)
                ):
                    op_id = self.click(
                        feature_name=feature_name,
                        threshold=threshold,
                        target_pos=target_pos,
                        right_click=right_click
                    )
                    break
            except:
                n += 1
                if n == 3:
                    break
        if op_id:
            return True
        else:
            return False

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
        op_id = None
        while True:
            try:
                if wait(
                    Template(
                        filename=get_path(self.app_feature_dir, if_feature + ".png"),
                        threshold=threshold
                    ),
                        timeout=1
                ):
                    n += 1
                    time.sleep(timeout/10)
                    if n == 10:
                        break
            except:
                op_id = self.click(
                    feature_name=feature_name,
                    threshold=threshold,
                    target_pos=target_pos,
                    right_click=right_click
                )
                break
        if op_id:
            return True
        else:
            return False

    def swipe(self, feature_name1, feature_name2, threshold=0.7, target_pos=5):
        op_id = None
        feature1 = self.find_feature(feature_name1, threshold=threshold, target_pos=target_pos)
        feature2 = self.find_feature(feature_name2, threshold=threshold, target_pos=target_pos)
        try:
            if feature1 and feature2:
                op_id = swipe(v1=feature1, v2=feature2)
            else:
                logger.info(f'拖拽操作失败！屏幕中未找到{feature_name1}或{feature_name2}')
        except Exception as e:
            logger.warning(f'拖拽操作失败！错误信息：{e}')
        if op_id:
            return True
        else:
            return False

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
                elif key == 'text':
                    text(value)
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
            feature_name=get_path(self.assert_feature_dir, feature_name + ".png"),
            rgb=rgb
        )
        try:
            if template:
                pos = assert_exists(template)
                logger.info(f'{feature_name}存在，屏幕坐标为：{pos}。#测试通过#')
                return True
        except Exception as e:
            logger.info(f'{feature_name}存在。#测试失败#')
            logger.warning(e)
            return False
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
            feature_name=get_path(self.assert_feature_dir, feature_name + ".png"),
            rgb=rgb
        )
        try:
            if template:
                pos = assert_not_exists(template)
                logger.info(f'{feature_name}存在，屏幕坐标为：{pos}。#测试失败#')
                return False
        except:
            logger.info(f'{feature_name}不存在。#测试通过#')
            return True

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


