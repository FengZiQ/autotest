# -*- coding: utf-8 -*-
import logging
import pytest
from config.api_test_plan import plan
from utils.path_util import get_path
from utils.file_utils import reading_json_file as load_test_data


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", plan.get('smoke_cases'))
    def test_execute_smoke_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'user_center', case_data + '.json'))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag

    @pytest.mark.smoke
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", plan.get('all_fun_cases'))
    def test_execute_all_fun_cases(self, http_client, case_data):
        # 加载测试用例
        test_data = load_test_data(get_path('tests_data', 'user_center', case_data + '.json'))

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_data,
            case_name=test_data[0].get('case_name')
        )
        assert http_client.assert_tool.FailedFlag

