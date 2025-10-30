# -*- coding: utf-8 -*-
import pytest
import os
from core.api_test_executor import TestCaseExecutor
from utils.path_util import get_path
from utils.file_utils import reading_json_file as load_test_data


def pytest_addoption(parser):
    """添加自定义命令行选项"""
    parser.addoption(
        "--test-plan",
        action="store",
        default="smoke",
        help="指定要执行的测试计划，如：smoke, FZQ, LYJ, full_functional"
    )


def get_test_cases_by_plan(test_plan):
    """根据测试计划获取对应的测试用例文件"""
    test_cases = []
    tests_data_dir = get_path('tests_data')

    if not os.path.exists(tests_data_dir):
        return test_cases

    for filename in os.listdir(tests_data_dir):
        if filename.endswith('.json') and f"@{test_plan}@" in filename:
            # 移除.json后缀，返回用于parametrize的参数
            case_name = filename.replace('.json', '')
            test_cases.append(case_name)

    return test_cases


def pytest_generate_tests(metafunc):
    """动态生成测试参数"""
    if "case_data" in metafunc.fixturenames:
        test_plan = metafunc.config.getoption("--test-plan")
        test_cases = get_test_cases_by_plan(test_plan)

        if not test_cases:
            pytest.skip(f"没有找到测试计划 '{test_plan}' 对应的测试用例")

        metafunc.parametrize("case_data", test_cases)


# 接口测试相关夹具
@pytest.fixture(scope="session")
def http_client():
    client = TestCaseExecutor(base_url="http://127.0.0.1:5000")
    yield client
    client.close()


@pytest.fixture(scope="function")
def test_case_data(case_data, request):
    """加载测试用例数据的夹具"""
    # 处理可能存在的子目录路径
    if '/' in case_data or '\\' in case_data:
        # 如果case_data包含路径分隔符，直接使用
        json_path = get_path('tests_data', case_data + '.json')
    else:
        # 否则在tests_data根目录下查找
        json_path = get_path('tests_data', case_data + '.json')

    test_data = load_test_data(json_path)

    # 为测试用例设置更有意义的名称
    request.node._nodeid = f"{case_data}"

    return test_data
