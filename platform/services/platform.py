# -*- coding: utf-8 -*-
import os
import json
import subprocess
import threading
from datetime import datetime


class TestPlatform:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.tests_data_dir = os.path.join(self.base_dir, 'tests_data')
        self.reports_dir = os.path.join(self.base_dir, 'reports')

    def get_test_cases(self):
        """获取所有测试用例文件"""
        cases = []
        if os.path.exists(self.tests_data_dir):
            for file in os.listdir(self.tests_data_dir):
                if file.endswith('.json'):
                    cases.append(file.replace('.json', ''))
        return sorted(cases)

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

    def save_test_case(self, test_plan, case_name, case_data):
        """保存测试用例到指定测试计划"""
        try:
            # 验证JSON格式
            json.loads(case_data)

            # 确保测试计划目录存在
            plan_dir = os.path.join(self.tests_data_dir, test_plan)
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

    def execute_test_plan(self, test_plan):
        """执行指定的测试计划"""
        try:
            # 构建 pytest 命令
            test_entrance = os.path.join(self.base_dir, 'tests', 'API', 'test_entrance.py')
            mark_name = f"api_{test_plan}"
            cmd = ['pytest', test_entrance, '-v', '-m', mark_name]

            # 创建日志文件
            log_dir = os.path.join(self.reports_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = os.path.join(log_dir, f'test_execution_{test_plan}_{timestamp}.log')

            # 在后台线程中执行测试
            def run_tests():
                with open(log_file, 'w', encoding='utf-8') as f:
                    # 写入开始时间
                    f.write(f"=== 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                    f.write(f"=== 执行的测试计划: {test_plan} ===\n")
                    f.write(f"=== 执行的命令: {' '.join(cmd)} ===\n\n")
                    f.flush()

                    # 执行测试
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=self.base_dir,
                        bufsize=1,
                        universal_newlines=True
                    )

                    # 实时读取输出
                    for line in process.stdout:
                        f.write(line)
                        f.flush()

                    process.wait()

                    # 写入结束时间和结果
                    f.write(f"\n=== 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                    f.write(f"=== 退出码: {process.returncode} ===\n")

            thread = threading.Thread(target=run_tests)
            thread.daemon = True
            thread.start()

            return True, "测试已开始执行", log_file
        except Exception as e:
            return False, f"执行失败: {str(e)}", None

    def get_execution_log(self, log_file):
        """获取测试执行日志"""
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            else:
                return "日志文件不存在或测试尚未开始"
        except Exception as e:
            return f"读取日志失败: {str(e)}"


if __name__ == '__main__':
    platform = TestPlatform()
    print(f'base_dir: {platform.base_dir}')
    print(f'tests_data_dir: {platform.tests_data_dir}')
    print(f'reports_dir: {platform.reports_dir}')