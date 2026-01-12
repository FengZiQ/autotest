# -*- coding: utf-8 -*-
import pytest
from config.api_test_plan import test_plan


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("test_client")
    @pytest.mark.parametrize("case_data", test_plan.get('smoke'))
    def test_execute_plan_smoke(self, test_client, case_data):
        # 执行测试用例
        case_result = test_client.execute_test_case(case_data)

        # 断言测试结果
        assert case_result.get('failed_steps') == 0

    @pytest.mark.usefixtures("test_client")
    @pytest.mark.parametrize("case_data", test_plan.get('all_fun'))
    def test_execute_plan_all_fun(self, test_client, case_data):
        # 执行测试用例
        case_result = test_client.execute_test_case(case_data)

        # 断言测试结果
        assert case_result.get('failed_steps') == 0



