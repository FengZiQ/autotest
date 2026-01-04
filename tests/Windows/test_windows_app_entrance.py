# -*- coding: utf-8 -*-
import pytest
from config.windows_test_plan import test_plan


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("app_a_executor")
    @pytest.mark.parametrize("case_data", test_plan.get('smoke'))
    def test_execute_smoke_cases(self, app_a_executor, case_data):
        # 执行测试用例
        case_result = app_a_executor.execute_test_case(case_data)

        # 断言测试结果
        assert case_result.get('failed_steps') == 0
