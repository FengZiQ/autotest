# -*- coding: utf-8 -*-
import os
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_path(*subpaths):
    return Path(os.path.join(PROJECT_ROOT, *subpaths)).as_posix()


if __name__ == '__main__':
    screenshots_dir = get_path('tests_data', 'user_center', 'login_test_data.json')
    print(screenshots_dir)