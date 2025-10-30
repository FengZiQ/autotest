# -*- coding: utf-8 -*-
import os
import logging
import pytest
from config.api_test_plan import plan
from utils.path_util import get_path
from utils.file_utils import reading_json_file as load_test_data

#
# class TestExecute:
#     @pytest.mark.smoke
#     @pytest.mark.usefixtures("http_client")
#     @pytest.mark.parametrize("case_data", plan.get('smoke_cases'))
#     def test_execute_smoke_cases(self, http_client, case_data):
#         # 加载测试用例
#         test_data = load_test_data(get_path('tests_data', 'user_center', case_data + '.json'))
#
#         # 执行测试用例
#         http_client.execute_test_case(
#             test_case_datas=test_data,
#             case_name=test_data[0].get('case_name')
#         )
#         assert http_client.assert_tool.FailedFlag
#
#     @pytest.mark.smoke
#     @pytest.mark.usefixtures("http_client")
#     @pytest.mark.parametrize("case_data", plan.get('all_fun_cases'))
#     def test_execute_all_fun_cases(self, http_client, case_data):
#         # 加载测试用例
#         test_data = load_test_data(get_path('tests_data', 'user_center', case_data + '.json'))
#
#         # 执行测试用例
#         http_client.execute_test_case(
#             test_case_datas=test_data,
#             case_name=test_data[0].get('case_name')
#         )
#         assert http_client.assert_tool.FailedFlag


class TestAPIEntrance:
    """API测试入口类"""

    @pytest.mark.usefixtures("http_client")
    def test_execute_cases_by_plan(self, http_client, test_case_data, case_data):
        """
        根据测试计划执行对应的测试用例

        Args:
            http_client: HTTP客户端夹具
            test_case_data: 测试用例数据夹具
            case_data: 测试用例名称
        """
        # 记录开始执行的测试用例
        logging.info(f"开始执行测试用例: {case_data}")

        # 执行测试用例
        http_client.execute_test_case(
            test_case_datas=test_case_data,
            case_name=test_case_data[0].get('case_name', case_data)
        )

        # 断言测试结果
        assert http_client.assert_tool.FailedFlag == False, f"测试用例 {case_data} 执行失败"

        # 记录测试完成
        logging.info(f"测试用例 {case_data} 执行完成")

