# -*- coding: utf-8 -*-
import re
import json
import logging
import traceback
from typing import Dict, List, Any
from utils.path_util import get_path
from core.reference_step import handel_references
from core.api_test_client import APITestClient

logger = logging.getLogger('api_test_executor')


class TestCaseExecutor:
    def __init__(self, base_url='', timeout=10):
        """
        初始化测试用例执行器
        :param base_url: 基础URL
        :param timeout: 默认超时时间
        """
        self.test_client = APITestClient(base_url=base_url, timeout=timeout)
        self.test_results = []
        self.context = {}  # 用于存储提取的变量

    def replace_variables(self, data):
        """
        替换数据中的变量占位符
        :param data: 需要替换的数据
        :return: 替换后的数据
        """
        if isinstance(data, dict):
            return {key: self.replace_variables(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.replace_variables(item) for item in data]
        elif isinstance(data, str):
            # 使用正则表达式匹配 ${variable} 格式的变量
            pattern = r'\$\{(\w+)\}'
            matches = re.findall(pattern, data)
            for var_name in matches:
                if var_name in self.context:
                    data = data.replace(f'${{{var_name}}}', str(self.context[var_name]))
            return data
        else:
            return data

    def extract_data(self, response, extract_rules):
        """
        从响应中提取数据并存储到上下文self.context字典中
        :param response: 响应对象
        :param extract_rules: 提取规则字典
        """
        if not extract_rules:
            return

        try:
            response_data = response.json()

            for target_key, rule in extract_rules.items():
                # 支持直接设置值到context
                if target_key.startswith('$$'):
                    self.context[target_key[2:]] = rule
                    continue
                # 解析规则
                if isinstance(rule, str):
                    # 简单的路径规则
                    path = rule
                    convert_type = None
                elif isinstance(rule, dict):
                    # 复杂的规则字典
                    path = rule.get('path')
                    convert_type = rule.get('type')

                    # 支持别名
                    if path is None:
                        path = rule.get('field')
                else:
                    logger.error(f"规则格式错误！提取 {target_key}: {rule} 失败。")
                    continue

                if not path:
                    logger.warning(f"{target_key} 的提取路径为空，跳过该项")
                    continue

                # 提取值
                value = extract_value(response_data, path)

                # 类型转换
                value = convert_value(value, convert_type)

                # 存储到context
                self.context[target_key] = value

        except Exception as e:
            logger.warning(f"提取数据时发生错误: {str(e)}")

    def load_test_case(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        加载测试用例JSON文件，支持引用其他JSON文件
        :param json_file_path: JSON文件路径
        :return: 测试用例步骤列表
        """
        try:
            # 获取完整路径
            case_path = get_path('tests_data', 'API', json_file_path)

            # 处理引用并加载测试用例
            test_case = handel_references(case_path)

            # 替换_interface字段为接口参数
            for i in range(len(test_case)):

                interface = test_case[i].get('actions', {}).get('_interface', None)

                if not interface:
                    logger.error(f"测试用例第{i+1}步缺少_interface字段。")
                    raise ValueError(f"测试用例第{i+1}步缺少_interface字段。")

                with open(get_path('resources', 'api_interface', interface), 'r', encoding='utf-8') as f:
                    test_case[i]['actions']['_interface'] = json.load(f)

            return test_case
        except Exception as e:
            logger.error(f"加载测试用例失败: {str(e)}")
            raise

    def execute_step(self, step: Dict[str, Any], step_number: int = 0) -> Dict[str, Any]:
        """
        执行单个测试步骤，有断言则执行断言，最后返回step_result
        :param step: 接口动作配置
        :param step_number: 接口动作配置
        :return: step_result
        """
        step_result = {
            'step_number': step_number,
            'action_info': step.get('actions', {}),
            'action_success': False,
            'assertions': [],
            'error': None
        }
        method = step_result['action_info'].get('_interface').get('method', '').upper()
        url_path = step_result['action_info'].get('_interface').get('url_path', '')
        headers = step_result['action_info'].get('_interface').get('headers', {})
        data = step_result['action_info'].get('data', None)
        params = step_result['action_info'].get('params', None)
        extract_rules = step_result['action_info'].get('extract', None)

        # 替换变量：不为空且字典中的values中存在"$"时替换变量
        if headers and [v for v in headers.values() if '$' in v]:
            headers = self.replace_variables(headers)
        if data and [v for v in data.values() if '$' in v]:
            data = self.replace_variables(data)
        if params and [v for v in params.values() if '$' in v]:
            params = self.replace_variables(params)

        logger.info(f"开始执行第{step_result['step_number']}步")
        logger.info(f"请求方法为{method}，请求路径为{url_path}")

        if data:
            logger.info(f"请求头headers为{headers}，请求数据data为{data}")
        if params:
            logger.info(f"请求头headers为{headers}，请求数据params为{params}")

        # 发送请求
        try:
            if method == 'GET':
                self.test_client.get(url_path, params=params, headers=headers)
            elif method == 'POST':
                content_type = headers.get('content-type', 'application/json')
                if 'application/json' in content_type:
                    self.test_client.post(url_path, json_data=data, headers=headers)
                else:
                    self.test_client.post(url_path, data=data, headers=headers)
            else:
                logger.error(f"不支持的HTTP方法: {method}")

            if self.test_client.response:
                logger.info(f"响应内容为: {self.test_client.response.text}")
                step_result['action_success'] = True

                # 提取数据
                if extract_rules:
                    self.extract_data(self.test_client.response, extract_rules)

        except Exception as e:
            logger.warning(f"请求执行失败: {str(e)}")
            step_result['action_success'] = False
            return step_result

        try:
            # 执行断言
            expected_results = step.get('expected_results', {})
            if expected_results:
                step_result['assertions'].append(self.perform_assertion(expected_results))
        except Exception as e:
            step_result['error'] = str(e)
            logger.error(f"第{step_result['step_number']}步执行断言时发生异常: {str(e)}")
            logger.error(traceback.format_exc())

        return step_result

    def perform_assertion(self, expected_results):
        """
        执行断言
        :param expected_results: 期望结果配置
        """
        if not self.test_client.response:
            logger.error("无法执行断言: 响应对象为空")
            return
        assert_form = expected_results.get('assert_form')
        assert_data = expected_results.get('assert_data')

        logger.info(f"断言方式: {assert_form}")
        logger.info(f"期望结果: {assert_data}")

        # 根据断言形式选择对应的断言方法
        if assert_form == '响应状态码等于':
            assert_result = self.test_client.response_status_equal(assert_data)
        elif assert_form == '响应体结构一致':
            assert_result = self.test_client.response_json_structure(assert_data)
        elif assert_form == '响应体内容包含':
            assert_result = self.test_client.response_text_contents(assert_data)
        elif assert_form == '响应体有键值对':
            assert_result = self.test_client.equals_key_value(assert_data)
        elif assert_form == 'databases_equal':
            assert_result = self.test_client.databases_equal()
        elif assert_form == 'databases_contents':
            assert_result = self.test_client.databases_contents()
        elif assert_form == 'redis_equal':
            assert_result = self.test_client.redis_equal()
        elif assert_form == 'redis_contents':
            assert_result = self.test_client.redis_contents()
        else:
            logger.info(f"不支持的断言形式: {assert_form}")
            assert_result = False

        return assert_result

    def execute_test_case(self, json_file_path: str):
        """
        执行测试用例
        :param json_file_path: 测试用例数据
        """
        case_name = json_file_path[:-5]

        logger.info(f"{'=' * 50}")
        logger.info(f"开始执行测试用例: {case_name}")
        logger.info(f"{'=' * 50}")

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
                step_result = self.execute_step(step, test_steps.index(step) + 1)
                test_case_result['step_results'].append(step_result)

                # 统计成功/失败的步骤
                if step_result['action_success'] and all(assertion for assertion in step_result['assertions']):
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

    def close(self):
        """关闭HTTP客户端"""
        self.test_client.close()


def extract_value(data, path):
    """递归地从嵌套结构中提取值"""
    if not path:
        return data

    parts = path.split('.')
    current = data

    for part in parts:
        # 处理数组索引，如 list[0]
        if '[' in part and ']' in part:
            key = part.split('[')[0]
            if key and key in current:
                current = current[key]

            # 处理多个数组索引，如 list[0][1]
            while '[' in part:
                start = part.find('[')
                end = part.find(']')
                if start != -1 and end != -1:
                    index_str = part[start + 1:end]
                    try:
                        index = int(index_str)
                        if isinstance(current, list) and 0 <= index < len(current):
                            current = current[index]
                        else:
                            return None
                    except (ValueError, TypeError):
                        return None
                    part = part[end + 1:]
                else:
                    break
        else:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

    return current


def convert_value(value, convert_type):
    """转换值的类型"""
    if convert_type is None or value is None:
        return value

    try:
        if convert_type == str:
            return str(value)
        elif convert_type == int:
            return int(value) if isinstance(value, (int, float, str)) else None
        elif convert_type == float:
            # 处理可能的字符串格式，如 "2.00"
            if isinstance(value, str):
                # 移除可能存在的逗号分隔符
                value = value.replace(',', '')
            return float(value) if isinstance(value, (int, float, str)) else None
        elif convert_type == bool:
            if isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ('true', '1', 'yes', 'y'):
                    return True
                elif lower_val in ('false', '0', 'no', 'n'):
                    return False
            return bool(value)
        else:
            # 尝试调用用户自定义的转换函数
            return convert_type(value)
    except (ValueError, TypeError):
        # 转换失败时返回原值
        return value


if __name__ == '__main__':
    executor = TestCaseExecutor(base_url='http://127.0.0.1:5000', timeout=10)
    executor.test_client.post('/order/create', json_data={})
    print(executor.test_client.response.text)
    executor.extract_data(executor.test_client.response, {'order_id': 'data[0].orderId', 'message': 'message', '$$setting': "value.value"})
    print(executor.context)
