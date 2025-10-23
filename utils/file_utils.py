# -*- coding: utf-8 -*-
import os
import time
import json


def writing_json_file(path, text):
    # 如果文件不存在，创建空文件并返回默认值
    if not os.path.exists(path):
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # 如果 text 是字符串，尝试解析为 JSON 以验证其有效性
    if isinstance(text, str):
        try:
            # 尝试解析字符串为 JSON（验证其有效性）
            json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"请检查json格式！错误信息: {e}")
    else:
        # 如果 text 不是字符串，尝试转换为 JSON 字符串（验证其可序列化性）
        try:
            # 尝试序列化为 JSON 字符串（验证其可序列化性）
            json.dumps(text)
        except (TypeError, ValueError) as e:
            raise ValueError(f"请检查json格式！错误信息: {e}")

    # 如果通过验证，写入文件
    with open(path, 'w', encoding='utf-8-sig') as file:
        json.dump(text, file, indent=4, ensure_ascii=False)


def reading_json_file(path, default=None):
    """
    读取JSON文件，如果文件不存在则创建空文件

    参数:
        path (str): JSON文件路径
        default: 文件不存在时返回的默认值（默认为空字典）

    返回:
        dict: 解析后的JSON内容或默认值

    异常:
        ValueError: 当JSON格式无效时抛出
    """
    # 如果文件不存在，创建空文件并返回默认值
    if not os.path.exists(path):
        if default is None:
            default = {}
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # 创建空文件并写入默认值
        with open(path, 'w', encoding='utf-8-sig') as file:
            json.dump(default, file, ensure_ascii=False, indent=4)
        return default

    # 文件存在时正常读取
    with open(path, 'r', encoding='utf-8-sig') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"请检查JSON格式！错误信息: {e}")


def execute_logs(text, file_path):
    with open(file_path, "r+", encoding='UTF-8') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ": " + text + '\n' + content)

        f.close()
    print(text)


def update_testlink(text, file_path):
    # for testLink steps populate
    file = open(file_path, "a", encoding='UTF-8')
    file.write(text + '\n')

    file.close()