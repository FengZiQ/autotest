# -*- coding: utf-8 -*-
import pytest
from core.get_test_plan import all_test_plan
from utils.path_util import get_path
from utils.file_utils import reading_json_file as load_test_data

test_plan = all_test_plan(get_path('tests_data'))


class TestExecute:
    @pytest.mark.api_smoke
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", test_plan.get('smoke'))
    def test_execute_smoke_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'smoke', case_data))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag

    @pytest.mark.api_full_functional
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", test_plan.get('full_functional'))
    def test_execute_all_fun_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'full_functional', case_data))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag

    @pytest.mark.api_order
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", test_plan.get('order'))
    def test_execute_all_fun_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'order', case_data))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag

    @pytest.mark.api_user_center
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", test_plan.get('user_center'))
    def test_execute_all_fun_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'user_center', case_data))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag


