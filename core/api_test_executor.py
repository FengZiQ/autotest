# -*- coding: utf-8 -*-
import re
import json
import logging
import traceback
from typing import Dict, List, Any
from utils.path_util import get_path
from core.reference_step import handel_references
from core.http_client import HTTPClient, APIAssert

logger = logging.getLogger('api_test_executor')


class TestCaseExecutor:
    def __init__(self, base_url='', timeout=10):
        """
        初始化测试用例执行器
        :param base_url: 基础URL
        :param timeout: 默认超时时间
        """
        self.http_client = HTTPClient(base_url=base_url, timeout=timeout)
        self.assert_tool = APIAssert()
        self.test_results = []
        self.context = {}  # 用于存储提取的变量
        self.response = None

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
        从响应中提取数据并存储到上下文中
        :param response: 响应对象
        :param extract_rules: 提取规则字典
        """
        if not extract_rules:
            return

        try:
            response_data = response.json()
            for var_name, json_path in extract_rules.items():
                # 简单的JSON路径解析（支持 content.key.subkey 格式）
                keys = json_path.split('.')
                value = response_data

                for key in keys:
                    if key == 'content' and key in value:
                        value = value[key]
                    elif isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break

                if value is not None:
                    self.context[var_name] = value
                    logger.info(f"提取变量成功: {var_name} = {value}")
                else:
                    logger.warning(f"警告: 无法提取变量 {var_name}，路径: {json_path}")

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

    def execute_step(self, action):
        """
        待完成，参考airtest_executor.py中的execute_step方法
        :param action: 接口动作配置
        :return: 响应对象
        """
        method = action.get('_interface').get('method', '').upper()
        url_path = action.get('_interface').get('url_path', '')
        headers = action.get('_interface').get('headers', {})
        data = action.get('data', None)
        params = action.get('params', None)
        extract_rules = action.get('extract', None)

        # 替换变量：不为空且字典中的values中存在"$"时替换变量
        if headers and [v for v in headers.values() if '$' in v]:
            headers = self.replace_variables(headers)
        if data and [v for v in data.values() if '$' in v]:
            data = self.replace_variables(data)
        if params and [v for v in params.values() if '$' in v]:
            params = self.replace_variables(params)

        if data:
            logger.info(f"请求头headers为{headers}，请求数据data为{data}")
        if params:
            logger.info(f"请求头headers为{headers}，请求数据params为{params}")

        # 发送请求
        try:
            if method == 'GET':
                response = self.http_client.get(url_path, params=params, headers=headers)
            elif method == 'POST':
                content_type = headers.get('content-type', 'application/json')
                if 'application/json' in content_type:
                    response = self.http_client.post(url_path, json_data=data, headers=headers)
                else:
                    response = self.http_client.post(url_path, data=data, headers=headers)
            else:
                logger.warning(f"不支持的HTTP方法: {method}")
                return None

            if response:
                logger.info(f"响应内容为: {response.text}")

                # 提取数据
                if extract_rules:
                    self.extract_data(response, extract_rules)
            self.response = response
            return response

        except Exception as e:
            logger.warning(f"请求执行失败: {str(e)}")
            return None

    def perform_assertion(self, expected_results):
        """
        执行断言
        :param expected_results: 期望结果配置
        """
        assert_flag = None
        if not self.response:
            logger.warning("无法执行断言: 响应对象为空")
            return
        assert_form = expected_results.get('assert_form')
        assert_data = expected_results.get('assert_data')

        logger.info(f"断言方式: {assert_form}")
        logger.info(f"期望结果: {assert_data}")

        # 根据断言形式选择对应的断言方法
        if assert_form == 'response_status_equal':
            self.assert_tool.response_status_equal(self.response)
        elif assert_form == 'response_json_structure':
            if isinstance(assert_data, dict):
                self.assert_tool.response_json_structure(self.response, assert_data)
            else:
                logger.warning(f'{assert_data}不是json！要求为dict类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'response_text_contents':
            if isinstance(assert_data, str):
                self.assert_tool.response_text_contents(self.response, assert_data)
            else:
                logger.warning(f'{assert_data}不是str！要求为str类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'response_json_contents':
            if isinstance(assert_data, dict):
                self.assert_tool.response_json_contents(self.response, assert_data)
            else:
                logger.warning(f'{assert_data}不是json！要求为dict类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'equals_key_value':
            if isinstance(assert_data, dict):
                self.assert_tool.equals_key_value(self.response, assert_data)
            else:
                logger.warning(f'{assert_data}不是json！要求为dict类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'databases_equal':
            pass
        elif assert_form == 'databases_contents':
            pass
        elif assert_form == 'redis_equal':
            pass
        elif assert_form == 'redis_contents':
            pass
        else:
            logger.info(f"不支持的断言形式: {assert_form}")

        return assert_flag

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

    def close(self):
        """关闭HTTP客户端"""
        self.http_client.close()


# 使用示例
if __name__ == "__main__":

    # 创建执行器实例
    executor = TestCaseExecutor(base_url="http://127.0.0.1:5000")  # 替换为实际的base_url

    a= executor.load_test_case('query_order.json')
    print(json.dumps(a, ensure_ascii=False, indent=4))
