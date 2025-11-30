# -*- coding: utf-8 -*-
import os
from services.platform import TestPlatform
from flask import Blueprint, render_template, request, jsonify, send_from_directory, send_file

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
    test_project = data.get('test_project')
    case_name = data.get('case_name')
    case_data = data.get('case_data')

    if not test_project or not case_name or not case_data:
        return jsonify({'success': False, 'message': '测试计划、用例名称和数据不能为空'})

    success, message = platform.save_test_case(test_project, case_name, case_data)
    return jsonify({'success': success, 'message': message})


@main_bp.route('/api/test-cases/<test_project>/<case_name>', methods=['GET'])
def get_test_case(test_project, case_name):
    """获取测试用例内容"""
    try:
        file_path = os.path.join(platform.tests_data_dir, test_project, f"{case_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'data': content})
        else:
            return jsonify({'success': False, 'message': '用例不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取失败: {str(e)}'})


@main_bp.route('/api/test-cases/<test_project>/<case_name>', methods=['DELETE'])
def delete_test_case(test_project, case_name):
    """删除测试用例"""
    try:
        file_path = os.path.join(platform.tests_data_dir, test_project, f"{case_name}")
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


@main_bp.route('/api/download-report')
def download_report():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '文件名不能为空'})

    # 获取项目根目录（autotest目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 构建正确的报告文件路径
    report_path = os.path.join(project_root, 'reports', filename)

    print(f"查找报告文件: {report_path}")  # 调试信息

    if not os.path.exists(report_path):
        return jsonify({'success': False, 'message': f'报告文件不存在: {report_path}'})

    try:
        return send_file(report_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})


# 执行测试计划
@main_bp.route('/api/execute-test-plan', methods=['POST'])
def execute_test_plan():
    data = request.json
    test_project = data.get('test_project')
    test_plan = data.get('test_plan')

    if not test_plan or not test_project:
        return jsonify({'success': False, 'message': '请选择测试项目及计划'})

    # 重置状态
    platform.test_completed = False
    platform.test_exit_code = None

    success, message, timestamp = platform.execute_test_plan(test_project, test_plan)
    platform.current_timestamp = timestamp

    return jsonify({
        'success': success,
        'message': message,
        'timestamp': timestamp
    })


# 获取执行日志
@main_bp.route('/api/execution-log')
def get_execution_log():
    timestamp = request.args.get('timestamp')
    if not timestamp:
        return jsonify({'success': False, 'message': '缺少时间戳参数'})

    log_content = platform.get_log_content(timestamp)

    if platform.current_timestamp == timestamp:
        platform.test_completed = True
        report_path = platform.get_report(timestamp)
        if report_path:
            # 转换为相对路径用于URL
            report_url = report_path.replace(platform.base_dir, '').lstrip('/')
        else:
            report_url = None
    else:
        report_url = None

    return jsonify({
        'success': True,
        'log_content': log_content,
        'completed': platform.test_completed,
        'report_url': report_url
    })


# 提供测试报告访问
@main_bp.route('/reports/<path:filename>')
def serve_report(filename):
    reports_dir = platform.reports_dir
    return send_from_directory(reports_dir, filename)


@main_bp.route('/mock-management')
def mock_management():
    return render_template('mock_management.html')
