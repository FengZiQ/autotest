# -*- coding: utf-8 -*-
from airtest.core.api import ST


class MySettings(object):
    # 元素查找超时时间
    ST.FIND_TIMEOUT = 15
    # 断言时严格模式置信度阈值
    ST.THRESHOLD_STRICT = 0.92
    # 截图质量
    ST.SNAPSHOT_QUALITY = 20

    # ST.LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r'/logs'



