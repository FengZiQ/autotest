# -*- coding: utf-8 -*-
import os
import json
import subprocess
import threading
from flask import Blueprint, render_template, request, jsonify
import sys

# 创建主蓝图
main_bp = Blueprint('main', __name__)


class TestPlatform:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

    def execute_tests(self, mark=None):
        """执行测试用例"""
        try:
            test_entrance = os.path.join(self.base_dir, 'tests', 'API', 'test_entrance.py')
            cmd = ['pytest', test_entrance, '-v']

            if mark and mark != 'all':
                cmd.extend(['-m', mark])

            # 在后台线程中执行测试
            def run_tests():
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                print(f"测试执行完成: {result.returncode}")

            thread = threading.Thread(target=run_tests)
            thread.daemon = True
            thread.start()

            return True, "测试已开始执行"
        except Exception as e:
            return False, f"执行失败: {str(e)}"


platform = TestPlatform()


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/test-cases')
def test_case_management():
    test_plans = platform.get_test_plans()
    return render_template('test_case_management.html', test_plans=test_plans)


@main_bp.route('/api/test-cases', methods=['POST'])
def save_test_case():
    data = request.json
    test_plan = data.get('test_plan')
    case_name = data.get('case_name')
    case_data = data.get('case_data')

    if not test_plan or not case_name or not case_data:
        return jsonify({'success': False, 'message': '测试计划、用例名称和数据不能为空'})

    success, message = platform.save_test_case(test_plan, case_name, case_data)
    return jsonify({'success': success, 'message': message})


@main_bp.route('/api/test-cases/<test_plan>/<case_name>', methods=['GET'])
def get_test_case(test_plan, case_name):
    """获取测试用例内容"""
    try:
        file_path = os.path.join(platform.tests_data_dir, test_plan, f"{case_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'data': content})
        else:
            return jsonify({'success': False, 'message': '用例不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取失败: {str(e)}'})


@main_bp.route('/api/test-cases/<test_plan>/<case_name>', methods=['DELETE'])
def delete_test_case(test_plan, case_name):
    """删除测试用例"""
    try:
        file_path = os.path.join(platform.tests_data_dir, test_plan, f"{case_name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '用例不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@main_bp.route('/test-execution')
def test_execution():
    return render_template('test_execution.html')


@main_bp.route('/api/execute-tests', methods=['POST'])
def execute_tests():
    data = request.json
    mark = data.get('mark', 'all')

    success, message = platform.execute_tests(mark)
    return jsonify({'success': success, 'message': message})


@main_bp.route('/mock-management')
def mock_management():
    return render_template('mock_management.html')
