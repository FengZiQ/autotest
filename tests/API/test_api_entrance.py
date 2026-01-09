# -*- coding: utf-8 -*-
import pytest
from config.api_test_plan import test_plan
from utils.path_util import get_path
from utils.file_utils import reading_json_file as load_test_data


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("http_client")
    @pytest.mark.parametrize("case_data", test_plan.get('all_fun'))
    def test_execute_smoke_cases(self, http_client, case_data):
        # 执行测试用例
        case_result = http_client.execute_test_case(case_data)

        # 断言测试结果
        assert case_result.get('failed_steps') == 0



