# -*- coding: utf-8 -*-
import os
from services.platform import TestPlatform
from flask import Blueprint, render_template, request, jsonify

# 创建主蓝图
main_bp = Blueprint('main', __name__)

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


# 获取测试计划列表
@main_bp.route('/api/test-plans')
def get_test_plans():
    """获取所有测试计划"""
    test_plans = platform.get_test_plans()
    return jsonify({'success': True, 'test_plans': list(test_plans.keys())})


# 执行测试计划
@main_bp.route('/api/execute-test-plan', methods=['POST'])
def execute_test_plan():
    data = request.json
    test_plan = data.get('test_plan')

    if not test_plan:
        return jsonify({'success': False, 'message': '请选择测试计划'})

    success, message, log_file = platform.execute_test_plan(test_plan)
    return jsonify({
        'success': success,
        'message': message,
        'log_file': log_file
    })


# 获取执行日志
@main_bp.route('/api/execution-log')
def get_execution_log():
    log_file = request.args.get('log_file')
    if not log_file:
        return jsonify({'success': False, 'message': '缺少日志文件参数'})

    log_content = platform.get_execution_log(log_file)
    return jsonify({'success': True, 'log_content': log_content})


@main_bp.route('/mock-management')
def mock_management():
    return render_template('mock_management.html')
