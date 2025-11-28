# -*- coding: utf-8 -*-
import logging
import pytest
import os
from pytest_html import extras
from config.android_test_plan import test_plan
from utils.path_util import get_path

logger = logging.getLogger('Android test_entrance')


class TestExecute:
    @pytest.mark.smoke
    @pytest.mark.usefixtures("netease_pris")
    @pytest.mark.parametrize("case_data", test_plan.get('smoke'))
    def test_execute_smoke_cases(self, netease_pris, case_data, request):
        # 确保netease_pris有test_results属性
        if not hasattr(netease_pris, 'test_results'):
            netease_pris.test_results = []

        # 执行测试用例
        case_result = netease_pris.execute_test_case(case_data)
        netease_pris.test_results.append(case_result)

        logger.debug(f'netease_pris.test_results: {netease_pris.test_results}')

        # 直接为每个步骤的截图添加到HTML报告
        for step_result in case_result.get('step_results', []):
            screenshot_file = step_result.get('step_screen')
            if screenshot_file:
                screenshot_path = get_path('reports', 'screenshots', screenshot_file)
                logger.debug(f'screenshot_path: {screenshot_path}')
                if os.path.exists(screenshot_path):
                    # 使用pytest-html的extra机制直接添加截图
                    pytest_html = request.config.pluginmanager.getplugin('html')
                    if pytest_html:
                        # 获取或创建extra列表
                        extra = getattr(request.node, 'extra', [])
                        # 导入extras并添加图片
                        image_extra = extras.image(screenshot_path, f"{step_result.get('step_name', '步骤')}")
                        logger.debug(f'image_extra添加图片中')
                        extra.append(image_extra)

                        # 将extra列表设置回节点
                        request.node.extra = extra
                        logger.debug(f"成功添加截图到报告: {screenshot_file}")

        # 断言测试结果
        assert case_result.get(
            'failed_steps') == 0, f"测试用例 {case_data} 执行失败，失败步骤数: {case_result.get('failed_steps')}"