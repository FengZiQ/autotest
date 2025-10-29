# -*- coding: utf-8 -*-
import logging
from airtest.core.api import *
from config.airtest_config import MySettings
from utils.path_util import get_path
from config.app_config import config_data

logger = logging.getLogger('windows_app_test')


class WinAppTest:
    def __init__(self, app_device):
        MySettings()
        self.dev = app_device
        self.img_BZ_path = get_path('resources', 'image', 'calculator_button')
        self.img_BZ_assert_path = get_path('resources', 'image', 'calculator_assert')

    def click_button(self, button_name, retry=3, interval=1, target_pos=5, threshold=0.8, rgb=False):
        """带重试机制的图像识别点击"""
        for attempt in range(retry):
            try:
                pos = exists(Template(
                    f'{self.img_BZ_path}/{button_name}.png',
                    resolution=config_data.get('resolution'),
                    target_pos=target_pos,
                    threshold=threshold,
                    rgb=rgb
                ))
                if pos:
                    touch(pos)
                    return True
            except Exception as e:
                logger.warning(f"点击尝试 {attempt + 1}/{retry} 失败: {str(e)}")
                time.sleep(interval)
        logger.error(f"按钮 {button_name} 点击失败")
        return False

    def feature_exit(self, button_name, threshold=0.8, rgb=False):
        try:
            if wait(
                    Template(
                        filename=f'{self.img_BZ_assert_path}/{button_name}.png',
                        resolution=config_data.get('resolution'),
                        threshold=threshold,
                        rgb=rgb
                    ),
                    timeout=3
            ):
                logger.info(f'断言成功')
                return True
        except Exception as e:
            logger.info(f'断言失败！')
            logger.warning(e)
            return False

