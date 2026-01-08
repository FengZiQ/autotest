# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any
from utils.path_util import get_path
from core.airtest_client import AirtestClient
from core.reference_step import handel_references

logger = logging.getLogger('airtest_executor')


class AirtestTestExecutor:
    def __init__(self, airtest_tool: AirtestClient):
        """
        初始化airtest测试执行器
        :param airtest_tool: airtest自动化工具实例
        """
        self.airtest_tool = airtest_tool
        self.test_results = []
        self.step_screenshots = []

    def load_test_case(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        加载测试用例JSON文件，支持引用其他JSON文件
        :param json_file_path: JSON文件路径
        :return: 测试用例步骤列表
        """
        try:
            # 获取完整路径
            full_path = get_path('tests_data', 'Windows', json_file_path)

            # 递归加载JSON文件并处理引用
            return handel_references(full_path)
        except Exception as e:
            logger.error(f"加载测试用例失败: {str(e)}")
            raise

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个测试步骤
        :param step: 测试步骤字典
        :return: 执行结果
        """
        step_result = {
            'image_path': step.get('image_path', ''),
            'step_name': step.get('step_name', '未知步骤'),
            'step_number': step.get('step_number', '0'),
            'action_info': step.get('action_info', {}),
            'action_success': False,
            'assertions': [],
            'error': None
        }
        if step_result['image_path']:
            self.airtest_tool.app_feature_dir += step_result['image_path']
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            logger.info(f"开始执行第{step_result['step_number']}步")

            # 测试用例.json文件操作映射
            action_success = None
            if step_result['action_info'].get('action') == '点击':
                action_success = self.airtest_tool.click(
                    feature_name=step_result['action_info'].get('feature_name'),
                    threshold=step_result['action_info'].get('threshold', 0.7),
                    target_pos=step_result['action_info'].get('target_pos', 5),
                    rgb=step_result['action_info'].get('rgb', False),
                    right_click=step_result['action_info'].get('right_click', False)
                )
            elif step_result['action_info'].get('action') == '点击并输入':
                action_success = self.airtest_tool.input_text(
                    feature_name=step_result['action_info'].get('feature_name'),
                    threshold=step_result['action_info'].get('threshold', 0.7),
                    target_pos=step_result['action_info'].get('target_pos', 5),
                    input_text=step_result['action_info'].get('input_text', ''),
                    time_sleep=step_result['action_info'].get('time_sleep', 0.5)
                )
            elif step_result['action_info'].get('action') == '特征出现后点击':
                action_success = self.airtest_tool.click_if_feature(
                    feature_name=step_result['action_info'].get('feature_name'),
                    if_feature=step_result['action_info'].get('if_feature'),
                    threshold=step_result['action_info'].get('threshold', 0.7),
                    target_pos=step_result['action_info'].get('target_pos', 5),
                    right_click=step_result['action_info'].get('right_click', False),
                    timeout=step_result['action_info'].get('timeout', 15)
                )
            elif step_result['action_info'].get('action') == '特征消失后点击':
                action_success = self.airtest_tool.click_if_not_feature(
                    feature_name=step_result['action_info'].get('feature_name'),
                    if_feature=step_result['action_info'].get('if_feature'),
                    threshold=step_result['action_info'].get('threshold', 0.7),
                    target_pos=step_result['action_info'].get('target_pos', 5),
                    right_click=step_result['action_info'].get('right_click', False),
                    timeout=step_result['action_info'].get('timeout', 15)
                )
            elif step_result['action_info'].get('action') == '滑动找到特征':
                action_success = self.airtest_tool.scroll_until_feature(
                    feature_name=step_result['action_info'].get('feature_name'),
                    scroll_value=step_result['action_info'].get('scroll_value', 0),
                    threshold=step_result['action_info'].get('threshold', 0.7),
                    timeout=step_result['action_info'].get('timeout', 15)
                )
            elif step_result['action_info'].get('action') == '拖拽':
                action_success = self.airtest_tool.swipe(
                    feature_name1=step_result['action_info'].get('feature_name1'),
                    feature_name2=step_result['action_info'].get('feature_name2'),
                    threshold=step_result['action_info'].get('threshold', 0.7)
                )
            elif step_result['action_info'].get('action') == '输入':
                # 设置action_success为True，操作不截图
                action_success = True
                # 有times参数，按times次TAB键后再输入
                if step_result['action_info'].get('times', 0) > 0:
                    self.airtest_tool.other_operate(
                        {'keyevent': ['{TAB}' for i in range(step_result['action_info'].get('times', 0))]},
                        time_sleep=step_result['action_info'].get('time_sleep', 0.5),
                    )
                self.airtest_tool.other_operate(
                    {'text': step_result['action_info'].get('input_text', '')},
                    time_sleep=step_result['action_info'].get('time_sleep', 0.5),
                )
            elif step_result['action_info'].get('action') == '剪贴板输入':
                # 设置action_success为True，操作不截图
                action_success = True
                # 给剪贴板赋值后粘贴输入
                self.airtest_tool.other_operate(
                    {'input_by_clipboard': step_result['action_info'].get('input_text', '')},
                    time_sleep=step_result['action_info'].get('time_sleep', 0.5),
                )
            elif step_result['action_info'].get('action') == '回车':
                # 设置action_success为True，操作不截图
                action_success = True
                # 按times次回车
                self.airtest_tool.other_operate(
                    {'keyevent': ['{ENTER}' for i in range(step_result['action_info'].get('times', 1))]},
                    time_sleep=step_result['action_info'].get('time_sleep', 0.5),
                )
            elif step_result['action_info'].get('action') == 'TAB':
                # 设置action_success为True，操作不截图
                action_success = True
                # 按times次Tab
                self.airtest_tool.other_operate(
                    {'keyevent': ['{TAB}' for i in range(step_result['action_info'].get('times', 1))]},
                    time_sleep=step_result['action_info'].get('time_sleep', 0.5),
                )

            step_result['action_success'] = action_success

            if not action_success:
                step_result['error'] = f"操作失败: {step_result['action_info'].get('action')}"
                logger.warning(f"步骤 {step_result['step_name']} 执行失败")

                # 失败截图
                self.step_screenshots.append(
                    self.airtest_tool.take_screenshot(
                        f"第{step_result['step_number']}步{step_result['step_name']}失败截图_{current_time}.png"
                    )
                )

                return step_result

            # 执行断言验证
            expected_results = step.get('expected_results', [])
            if expected_results:
                for i, assertion in enumerate(expected_results):
                    assertion_result = self.execute_assertion(assertion)
                    step_result['assertions'].append(assertion_result)

                # 断言结束后截图
                self.step_screenshots.append(
                    self.airtest_tool.take_screenshot(
                        f"第{step_result['step_number']}步{step_result['step_name']}的断言截图_{current_time}.png"
                    )
                )

        except Exception as e:
            step_result['error'] = str(e)
            logger.error(f"执行步骤时发生异常: {str(e)}")
            logger.error(traceback.format_exc())

            # 异常截图
            self.step_screenshots.append(
                self.airtest_tool.take_screenshot(
                    f"第{step_result['step_number']}步{step_result['step_name']}的异常截图_{current_time}.png"
                )
            )

        return step_result

    def get_step_screenshots(self):
        return self.step_screenshots

    def execute_assertion(self, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个断言
        :param assertion: 断言配置字典
        :return: 断言结果
        """
        assertion_result = {
            'assert_form': assertion.get('assert_form', ''),
            'success': False,
            'expected': None,
            'actual': None,
            'error': None
        }

        try:
            # 断言
            if assertion.get('assert_form', '') == '存在特征':
                result = self.airtest_tool.assert_feature_exist(
                    feature_name=assertion.get('feature_name', ''),
                    threshold=assertion.get('threshold', 0.8),
                )
            elif assertion.get('assert_form', '') == '不存在特征':
                result = self.airtest_tool.assert_feature_not_exist(
                    feature_name=assertion.get('feature_name', ''),
                    threshold=assertion.get('threshold', 0.8),
                )
            else:
                result = False
                logger.error(f'断言方式错误！请确认断言信息中assert_form值，应为：存在特征/不存在特征')
            assertion_result['success'] = result
            assertion_result['actual'] = "断言通过" if result else "断言失败"

        except Exception as e:
            assertion_result['error'] = str(e)
            assertion_result['success'] = False
            logger.error(f"断言执行! 发生异常: <{str(e)}>")
            logger.error(traceback.format_exc())

        return assertion_result

    def execute_test_case(self, json_file_path: str) -> Dict[str, Any]:
        """
        执行完整的测试用例
        :param json_file_path: JSON测试用例文件路径
        :return: 测试结果汇总
        """
        case_name = json_file_path[:-5]

        logger.info(f"开始执行测试用例: {case_name}")

        test_case_result = {
            'test_case': json_file_path,
            'total_steps': 0,
            'passed_steps': 0,
            'failed_steps': 0,
            'step_results': [],
            'overall_success': False
        }

        try:
            # 加载测试用例
            test_steps = self.load_test_case(json_file_path)
            test_case_result['total_steps'] = len(test_steps)

            # 执行每个步骤
            for step in test_steps:
                step_result = self.execute_step(step)
                test_case_result['step_results'].append(step_result)

                # 统计成功/失败的步骤
                if step_result['action_success'] and all(
                        assertion['success'] for assertion in step_result['assertions']):
                    test_case_result['passed_steps'] += 1
                else:
                    test_case_result['failed_steps'] += 1

            # 判断整体测试结果
            test_case_result['overall_success'] = test_case_result['failed_steps'] == 0

            # 记录测试结果
            if test_case_result['overall_success']:
                logger.info(f"测试用例【{case_name}】执行成功.")
            else:
                logger.warning(f"测试用例【{case_name}】执行失败!")

        except Exception as e:
            logger.error(f"执行测试用例{case_name}时发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            test_case_result['overall_success'] = False
            test_case_result['error'] = str(e)
        # logger.debug(f'测试用例 {case_name} 执行结果: {test_case_result}')

        return test_case_result


