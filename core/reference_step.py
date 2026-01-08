# -*- coding: utf-8 -*-
import os
import json
from typing import List, Dict, Any


def handel_references(file_path: str, visited_files: set = None) -> List[Dict[str, Any]]:
    """
    递归加载JSON文件并处理引用
    :param file_path: JSON文件完整路径
    :param visited_files: 已访问文件集合，用于检测循环引用
    :return: 处理后的测试用例步骤列表
    """
    if visited_files is None:
        visited_files = set()

    # 标准化文件路径，避免重复处理同一文件
    normalized_path = os.path.abspath(file_path)

    # 检测循环引用
    if normalized_path in visited_files:
        raise ValueError(f"检测到循环引用: {normalized_path}")

    visited_files.add(normalized_path)

    try:
        # 读取文件内容
        with open(normalized_path, 'r', encoding='utf-8') as file:
            test_case = json.load(file)

        # 如果文件内容不是列表，直接返回
        if not isinstance(test_case, list):
            return test_case

        # 处理引用
        processed_case = []
        for item in test_case:
            # 检查是否是引用
            if isinstance(item, dict) and "_reference" in item:
                # 获取引用的文件名
                ref_file_name = item["_reference"]

                # 构建引用文件的完整路径（与当前文件同级目录）
                current_dir = os.path.dirname(normalized_path)
                ref_file_path = os.path.join(current_dir, ref_file_name)

                # 验证引用文件是否存在
                if not os.path.exists(ref_file_path):
                    raise FileNotFoundError(f"引用文件不存在: {ref_file_path}")

                # 递归加载引用文件内容
                ref_content = handel_references(ref_file_path, visited_files.copy())

                # 确保引用内容是一个列表
                if isinstance(ref_content, list):
                    # 将引用内容添加到处理后的列表中
                    processed_case.extend(ref_content)
                else:
                    # 如果引用内容不是列表，将其作为单个元素添加
                    processed_case.append(ref_content)
            else:
                # 非引用元素，直接添加到列表
                processed_case.append(item)

        # 移除已访问记录，以便其他分支可以重新引用
        visited_files.remove(normalized_path)

        return processed_case

    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        # 移除已访问记录，然后重新抛出异常
        if normalized_path in visited_files:
            visited_files.remove(normalized_path)
        raise
    except Exception as e:
        # 移除已访问记录，然后重新抛出异常
        if normalized_path in visited_files:
            visited_files.remove(normalized_path)
        raise
