# -*- coding: utf-8 -*-
import os
import sys
import json
import glob
import pytest
import threading
from datetime import datetime


class TestPlatform:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tests_data_dir = os.path.join(self.base_dir, 'tests_data')
        self.reports_dir = os.path.join(self.base_dir, 'reports')
        self.test_completed = False
        self.test_exit_code = None
        self.current_timestamp = None

    def get_test_plans(self):
        """获取所有测试计划"""
        test_plans = {}
        if os.path.exists(self.tests_data_dir):
            for item in os.listdir(self.tests_data_dir):
                item_path = os.path.join(self.tests_data_dir, item)
                if os.path.isdir(item_path):
                    # 获取该测试计划下的所有JSON文件
                    test_cases = []
                    for file in os.listdir(item_path):
                        if file.endswith('.json'):
                            test_cases.append(file)
                    test_plans[item] = sorted(test_cases)
        return test_plans

    def save_test_case(self, test_project, case_name, case_data):
        """保存测试用例到指定测试计划"""
        try:
            # 验证JSON格式
            json.loads(case_data)

            # 确保测试计划目录存在
            plan_dir = os.path.join(self.tests_data_dir, test_project)
            os.makedirs(plan_dir, exist_ok=True)

            # 保存文件
            file_path = os.path.join(plan_dir, f"{case_name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(case_data)
            return True, "保存成功"
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"保存失败: {str(e)}"

    def cleanup_module_cache(self):
        """清理模块缓存，避免模块导入冲突"""
        modules_to_remove = []
        for module_name in list(sys.modules.keys()):
            if module_name and (
                    'test_entrance' in module_name or 'tests.API' in module_name or 'tests.Android' in module_name
            ):
                modules_to_remove.append(module_name)

        for module_name in modules_to_remove:
            del sys.modules[module_name]

        # 清理 pycache
        for root, dirs, files in os.walk(os.path.join(self.base_dir, 'tests')):
            if '__pycache__' in dirs:
                import shutil
                pycache_path = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_path, ignore_errors=True)

    def execute_test_plan(self, test_project, test_plan):
        """执行指定的测试计划，并返回日志和报告信息"""
        try:
            # 清理模块缓存
            self.cleanup_module_cache()

            # 生成时间戳
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            project_name = None
            execute_test = None
            if test_project == 'API' and test_plan == 'smoke':
                project_name = 'API'
                execute_test = 'test_execute_smoke_cases'
            elif test_project == 'API' and test_plan == 'all_fun':
                project_name = 'API'
                execute_test = 'test_execute_all_fun'
            elif test_project == 'API' and test_plan == 'user_service':
                project_name = 'API'
                execute_test = 'test_user_service'
            elif test_project == 'API' and test_plan == 'order_service':
                project_name = 'API'
                execute_test = 'test_order_service'
            elif test_project == 'android_app' and test_plan == 'smoke':
                project_name = 'Android'
                execute_test = 'test_execute_smoke_cases'
            elif test_project == 'android_app' and test_plan == 'bookstore':
                project_name = 'Android'
                execute_test = 'test_bookstore'
            elif test_project == 'android_app' and test_plan == 'bookshelf':
                project_name = 'Android'
                execute_test = 'test_bookshelf'
            elif test_project == 'android_app' and test_plan == 'user_center':
                project_name = 'Android'
                execute_test = 'test_user_center'
            elif test_project == 'Windows' and test_plan == '':
                project_name = 'Windows'
                execute_test = ''

            # 构建文件路径
            file_path = os.path.join(self.base_dir, 'tests', project_name, 'test_entrance.py')
            # 组合成 pytest 可识别的格式
            test_command = f"pytest {file_path}::TestExecute::{execute_test}"

            # test_target = f"{file_path}::TestExecute::{execute_test}"
            # pytest_args = [test_target, '-v']

            # 在后台线程中执行测试
            def run_tests():
                # exit_code = pytest.main(pytest_args)
                exit_code = os.system(test_command)
                self.test_completed = True
                self.test_exit_code = exit_code

            thread = threading.Thread(target=run_tests)
            thread.daemon = True
            thread.start()

            # 返回时间戳用于查找日志和报告
            return True, "测试已开始执行", timestamp
        except Exception as e:
            return False, f"执行失败: {str(e)}", None

    def get_log_content(self, timestamp):
        """根据时间戳获取最新的日志内容"""
        try:
            logs_dir = os.path.join(self.reports_dir, 'logs')
            if not os.path.exists(logs_dir):
                return "日志目录不存在"

            # 查找匹配时间戳的日志文件
            log_pattern = os.path.join(logs_dir, f'test_{timestamp}*.log')
            log_files = glob.glob(log_pattern)

            if not log_files:
                # 如果没有找到精确匹配，尝试获取最新的日志文件
                all_logs = glob.glob(os.path.join(logs_dir, 'test_*.log'))
                if all_logs:
                    latest_log = max(all_logs, key=os.path.getctime)
                    with open(latest_log, 'r', encoding='utf-8') as f:
                        return f.read()
                return "未找到日志文件"

            # 读取最新的匹配日志文件
            latest_log = max(log_files, key=os.path.getctime)
            with open(latest_log, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取日志失败: {str(e)}"

    def get_report(self, timestamp):
        """根据时间戳获取最新的测试报告"""
        try:
            reports_dir = self.reports_dir
            if not os.path.exists(reports_dir):
                return None

            # 查找匹配时间戳的报告文件
            report_pattern = os.path.join(reports_dir, f'report_{timestamp}*.html')
            report_files = glob.glob(report_pattern)

            if not report_files:
                # 如果没有找到精确匹配，尝试获取最新的报告文件
                all_reports = glob.glob(os.path.join(reports_dir, 'report_*.html'))
                if all_reports:
                    return max(all_reports, key=os.path.getctime)
                return None

            # 返回最新的匹配报告文件
            return max(report_files, key=os.path.getctime)
        except Exception as e:
            print(f"查找报告失败: {e}")
            return None


if __name__ == '__main__':
    platform = TestPlatform()
    print(f'base_dir: {platform.base_dir}')
    print(f'tests_data_dir: {platform.tests_data_dir}')
    print(f'reports_dir: {platform.reports_dir}')
