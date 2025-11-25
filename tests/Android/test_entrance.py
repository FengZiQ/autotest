# -*- coding: utf-8 -*-
import pytest
from config.android_test_plan import test_plan


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("netease_pris")
    @pytest.mark.parametrize("case_data", test_plan.get('smoke'))
    def test_execute_smoke_cases(self, netease_pris, case_data):
        # 执行测试用例
        netease_pris.execute_test_case(case_data)
