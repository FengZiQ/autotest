# -*- coding: utf-8 -*-
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_path(*subpaths):
    return os.path.join(PROJECT_ROOT, *subpaths)


if __name__ == '__main__':
    screenshots_dir = get_path('test_data', 'user_center', 'login_test_data.json')
    print(screenshots_dir)