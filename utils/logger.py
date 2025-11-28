# -*- coding: utf-8 -*-
import os
import logging


class ConditionalFormatter(logging.Formatter):
    """根据日志级别动态切换格式的Formatter"""

    def __init__(self, fmt_default, fmt_info_debug, datefmt=None):
        super().__init__(fmt_default, datefmt)
        self.fmt_default = fmt_default
        self.fmt_info_debug = fmt_info_debug
        self.datefmt = datefmt

    def format(self, record):
        # 根据日志级别选择格式
        if record.levelno in (logging.INFO, logging.DEBUG):
            self._style._fmt = self.fmt_info_debug
        else:
            self._style._fmt = self.fmt_default

        # 保持日期格式一致性
        if self.datefmt:
            self.datefmt = self.datefmt
        return super().format(record)


def log_record(timestamp):
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(__file__))
    # 文件日志处理器
    log_dir = root_dir + r"/reports/logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{log_dir}/test_{timestamp}.log"
    with open(log_file, 'a'):
        pass

    def custom_filter(record):
        allowed_names = {
            'root',
            'airtest.services.api',
            'airtest.aircv.multiscale_template_matching',
            'windows_app_test',
            'http_client',
            'api_test_executor',
            'android_client',
            'android_test_executor',
        }
        if record.name not in allowed_names:
            return False

        if record.name == 'airtest.services.api':
            message = record.getMessage()
            return "Try finding" in message or "match result" in message
        return True

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 清除现有处理器避免重复日志
    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(custom_filter)

    # 定义两种日志格式
    fmt_info_debug = '[%(asctime)s][%(levelname)s]<%(name)s> 内容:%(message)s'
    fmt_default = (
        '[%(asctime)s][%(levelname)s]<%(name)s> '
        '【文件名：%(filename)s, 行号：%(lineno)s】 内容:%(message)s'
    )

    # 使用自定义Formatter
    formatter = ConditionalFormatter(
        fmt_default=fmt_default,
        fmt_info_debug=fmt_info_debug,
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
