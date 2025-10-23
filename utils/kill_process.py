# -*- coding: utf-8 -*-
import logging
import psutil


def kill_process_by_name(process_name):
    """根据进程名关闭应用"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            try:
                proc.kill()
                logging.info(f"已关闭进程: {process_name}")
                return True
            except Exception as e:
                logging.error(f"关闭进程失败: {process_name}, 错误: {str(e)}")
    return False