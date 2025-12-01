# -*- coding: utf-8 -*-
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any
from appium.webdriver.common.appiumby import AppiumBy
from utils.path_util import get_path
from core.android_client import AndroidAutomationTool

logger = logging.getLogger('android_test_executor')


class AndroidTestExecutor:
    def __init__(self, android_tool: AndroidAutomationTool):
        """
        初始化Android测试执行器
        :param android_tool: Android自动化工具实例
        """
        self.android_tool = android_tool
        self.test_results = []
        self.step_screenshots = []
        # logger.debug("Android测试执行器初始化完成")

    def load_test_case(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        加载测试用例JSON文件
        :param json_file_path: JSON文件路径
        :return: 测试用例步骤列表
        """
        try:
            full_path = get_path('tests_data', 'Android', json_file_path)
            with open(full_path, 'r', encoding='utf-8') as file:
                test_case = json.load(file)
            return test_case
        except Exception as e:
            logger.error(f"加载测试用例失败: {str(e)}")
            raise

    def convert_locator_by(self, locator_by_str: str) -> Any:
        """
        将字符串定位方式转换为AppiumBy常量
        :param locator_by_str: 定位方式字符串
        :return: AppiumBy常量
        """
        locator_mapping = {
            'AppiumBy.XPATH': AppiumBy.XPATH,
            'AppiumBy.ID': AppiumBy.ID,
            'AppiumBy.CLASS_NAME': AppiumBy.CLASS_NAME,
            'AppiumBy.ACCESSIBILITY_ID': AppiumBy.ACCESSIBILITY_ID,
            'AppiumBy.ANDROID_UIAUTOMATOR': AppiumBy.ANDROID_UIAUTOMATOR,
            'AppiumBy.CSS_SELECTOR': AppiumBy.CSS_SELECTOR,
            'AppiumBy.TAG_NAME': AppiumBy.TAG_NAME,
            'AppiumBy.LINK_TEXT': AppiumBy.LINK_TEXT,
            'AppiumBy.PARTIAL_LINK_TEXT': AppiumBy.PARTIAL_LINK_TEXT,
            'AppiumBy.NAME': AppiumBy.NAME
        }

        if locator_by_str in locator_mapping:
            return locator_mapping[locator_by_str]
        else:
            logger.warning(f"未知的定位方式: {locator_by_str}，默认使用XPATH")
            return AppiumBy.XPATH

    def execute_step(self, step: Dict[str, Any], case_name: str) -> Dict[str, Any]:
        """
        执行单个测试步骤
        :param step: 测试步骤字典
        :param case_name: 测试用例名称
        :return: 执行结果
        """
        step_result = {
            'step_name': step.get('step_name', '未知步骤'),
            'step_number': step.get('step_number', '0'),
            'action': step.get('action', '点击'),
            'send_keys': step.get('send_keys', ''),
            'loading_time': step.get('loading_time', 0.5),
            'locator_waiting_time': step.get('locator_waiting_time', 0.5),
            'action_success': False,
            'assertions': [],
            'error': None
        }
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # 构建定位器
            locator_by = self.convert_locator_by(step.get('locator_by', 'AppiumBy.XPATH'))
            locator_value = step.get('locator', '')
            locator = (locator_by, locator_value)

            logger.info(f"执行第{step_result['step_number']}步——>{step_result['step_name']}")
            if locator_value:
                logger.debug(f"定位器: {locator}")

            # 执行点击操作（根据您的JSON结构，默认是点击操作）
            # 如果需要支持更多操作类型，可以在这里扩展
            action_success = None
            if step_result.get('action') == '点击':
                action_success = self.android_tool.click_element(
                    locator=locator,
                    loading_time=step_result.get('loading_time'),
                    timeout=step_result.get('locator_waiting_time')
                )
            elif step_result.get('action') == '输入':
                action_success = self.android_tool.send_keys(
                    locator=locator,
                    text=step_result.get('send_keys'),
                    timeout=step_result.get('locator_waiting_time'),
                    loading_time=step_result.get('loading_time')
                )
            elif step_result.get('action') == '按返回键':
                action_success = self.android_tool.back()
            elif step_result.get('action') == '滑动向上':
                action_success = self.android_tool.swipe_up()
            elif step_result.get('action') == '滑动向下':
                action_success = self.android_tool.swipe_down()
            elif step_result.get('action') == '滑动向左':
                action_success = self.android_tool.swipe_left()
            elif step_result.get('action') == '滑动向右':
                action_success = self.android_tool.swipe_right()

            step_result['action_success'] = action_success

            if not action_success:
                step_result['error'] = f"点击操作失败: {locator}"
                logger.warning(f"步骤 {step_result['step_name']} 执行失败")

                # 失败截图
                self.step_screenshots.append(
                    self.android_tool.take_screenshot(
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
                    self.android_tool.take_screenshot(
                        f"第{step_result['step_number']}步{step_result['step_name']}的断言截图_{current_time}.png"
                    )
                )

        except Exception as e:
            step_result['error'] = str(e)
            logger.error(f"执行步骤时发生异常: {str(e)}")
            logger.error(traceback.format_exc())

            # 异常截图
            self.step_screenshots.append(
                self.android_tool.take_screenshot(
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
            # 构建定位器
            locator_by = self.convert_locator_by(assertion.get('locator_by', 'AppiumBy.XPATH'))
            locator_value = assertion.get('locator', '')
            locator = (locator_by, locator_value)

            # 获取断言方法
            assert_method_name = assertion.get('assert_form', '')
            assert_method = getattr(self.android_tool, assert_method_name, None)

            if not assert_method:
                assertion_result['error'] = f"不支持的断言方法: {assert_method_name}"
                logger.error(assertion_result['error'])
                return assertion_result

            # 根据断言方法类型传递参数
            if assert_method_name in ['assert_text_equals', 'assert_text_contains']:
                expected_text = assertion.get('expected_text', '')
                assertion_result['expected'] = expected_text
                result = assert_method(locator, expected_text)
            else:
                result = assert_method(locator)

            assertion_result['success'] = result
            assertion_result['actual'] = "断言通过" if result else "断言失败"

            if not result:
                logger.info("断言失败!")
                logger.info(f"断言方式：{assert_method_name} - 定位器: {locator}")
            else:
                logger.info(f"断言成功：{assertion.get('assert_describe', '缺失断言描述参数<assert_describe>')}")

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
                step_result = self.execute_step(step, case_name)
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


# 使用示例
if __name__ == "__main__":
    # 设备能力配置
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '12',
        'deviceName': 'Mumu emulator',
        'appPackage': 'com.netease.pris',
        'appActivity': 'com.netease.pris.activity.PRISActivityFlasScreen',
        'automationName': 'UiAutomator2',
        'noReset': True,
        "udid": "emulator-5554"
    }

    # 创建工具实例
    automation_tool = AndroidAutomationTool()

    try:
        # 启动驱动
        driver = automation_tool.setup_driver(desired_caps)
        if not driver:
            logger.error("驱动启动失败，退出测试")
            exit(1)

        # 创建测试执行器
        executor = AndroidTestExecutor(automation_tool)

        # 执行测试用例
        test_result = executor.execute_test_case('add_book_from_bookstore.json')

    finally:
        # 退出驱动
        automation_tool.quit_driver()

