# -*- coding: utf-8 -*-
import os


def all_test_plan(root_dir):
    """
    返回指定文件夹下以下级文件夹名作为key，下级文件夹中文件名列表作为value的字典

    Args:
        root_dir: 指定的根目录路径

    Returns:
        dict: 字典，格式为 {下级文件夹名: [文件名1, 文件名2, ...]}
    """
    result_dict = {}

    # 检查根目录是否存在
    if not os.path.exists(root_dir):
        print(f"错误：目录 '{root_dir}' 不存在")
        return result_dict

    # 遍历根目录下的所有项目
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)

        # 只处理子目录，跳过文件
        if os.path.isdir(item_path):
            file_list = []

            # 遍历子目录下的所有项目
            for sub_item in os.listdir(item_path):
                sub_item_path = os.path.join(item_path, sub_item)

                # 只添加文件，跳过子目录
                if os.path.isfile(sub_item_path):
                    file_list.append(sub_item)

            # 将子目录名和对应的文件列表添加到结果字典中
            result_dict[item] = file_list

    return result_dict


# 使用示例
if __name__ == "__main__":
    import json
    from utils.path_util import get_path
    # 测试代码
    target_dir = get_path("tests_data")

    result = all_test_plan(target_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    """
    {
      "smoke": [
        "login_invalid_user.json",
        "login_test_data.json"
      ],
      "order": [
        "login_invalid_user.json",
        "login_test_data.json"
      ],
      "full_functional": [
        "login_invalid_user.json",
        "login_test_data.json"
      ],
      "user_center": [
        "login_invalid_user.json",
        "login_test_data.json"
      ]
    }
    """