# -*- coding: utf-8 -*-
import json
import re
import logging
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

    def send_requests(self, action):
        """
        执行单个接口请求
        :param action: 接口动作配置
        :return: 响应对象
        """
        method = action.get('method', '').upper()
        url_path = action.get('url_path', '')
        headers = action.get('headers', {})
        data = action.get('data', None)
        params = action.get('params', None)
        extract_rules = action.get('extract', None)

        # 替换变量
        headers = self.replace_variables(headers)
        data = self.replace_variables(data)
        params = self.replace_variables(params)

        if data:
            logger.info(f"请求头headers为{headers}，请求数据为{data}")
        if params:
            logger.info(f"请求头headers为{headers}，请求数据为{params}")

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
        if assert_form == 'response_json_structure':
            if isinstance(assert_data, dict):
                self.assert_tool.response_json_structure(self.response, assert_data)
                # self.assert_tool.FailedFlag = False
            else:
                logger.warning(f'{assert_data}不是json！要求为dict类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'response_text_contents':
            if isinstance(assert_data, str):
                self.assert_tool.response_text_contents(self.response, assert_data)
                # self.assert_tool.FailedFlag = False
            else:
                logger.warning(f'{assert_data}不是str！要求为str类型。')
                self.assert_tool.FailedFlag = False
        elif assert_form == 'response_json_contents':
            if isinstance(assert_data, dict):
                self.assert_tool.response_json_contents(self.response, assert_data)
                # self.assert_tool.FailedFlag = False
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

    def execute_test_case(self, test_case_datas, case_name="未命名测试用例"):
        """
        执行测试用例
        :param test_case_datas: 测试用例数据
        :param case_name: 测试用例名称
        """
        logger.info(f"{'=' * 50}")
        logger.info(f"开始执行测试用例: {case_name}")
        logger.info(f"{'=' * 50}")

        if not isinstance(test_case_datas, list):
            logger.warning(f'收集的测试用例数据不是list类型，测试用例{case_name}执行结束！')
            self.assert_tool.FailedFlag = False

        # 重置上下文（可选，根据需求决定是否在用例间重置）
        self.context = {}

        for tcd in test_case_datas:
            # 在测试用例数据中找出actions与expected_results
            actions = tcd.get('actions', [])
            expected_results = tcd.get('expected_results', {})

            logger.info(f"--- 执行步骤 {tcd.get('step_number')} ---")

            # 发送请求
            response = self.send_requests(actions)

            # 如果某个步骤失败，可以选择终止执行
            if not response:
                logger.warning(f"步骤 {tcd.get('step_number')} 执行失败，终止测试")
                self.assert_tool.FailedFlag = False
                break

            if response:
                logger.info(f"--- 步骤 {tcd.get('step_number')} 执行断言 ---")
                self.perform_assertion(expected_results)
            else:
                logger.warning(f"步骤 {tcd.get('step_number')} 无法断言，请检查断言方式与响应结果是否匹配！")
                self.assert_tool.FailedFlag = False

        logger.info(f"测试用例执行完成: {case_name}")

    def close(self):
        """关闭HTTP客户端"""
        self.http_client.close()


# 使用示例
if __name__ == "__main__":
    # 单接口测试用例数据
    test_case_data = [
        {
            "case_name": "账号密码登录",
            "step_number": "1",
            "actions": {
                "method": "POST",
                "url_path": "/gbsp/auth/userlogin",
                "headers": {
                    "content-type": "application/json"
                },
                "data": {
                    "password": "test123@",
                    "userName": "13717641870"
                },
                "extract": {
                    "access_token": "data.access_token",
                    "refresh_token": "data.refresh_token"
                }
            },
            "expected_results": {
                "assert_form": "response_json_structure",
                "assert_data": {
                    "success": True,
                    "code": 200,
                    "data": {
                        "access_token": "cn-8b894f1b-4f39-4fdb-9b48-f44f13c0fee8",
                        "refresh_token": "cn-e24938d3-0936-464b-9ba9-fe92a978f35a",
                        "scope": "account_security ent_account_read account_token_login account_privacy_write account_info_write account_info_read",
                        "token_type": "bearer",
                        "expires_in": 504018
                    },
                    "responseTime": 1760065131643
                }
            }
        },
        {
            "case_name": "账号密码登录",
            "step_number": "2",
            "actions": {
                "method": "GET",
                "url_path": "/gbsp/user/getUserInfo",
                "headers": {
                    "content-type": "application/x-www-form-urlencoded",
                    "Authorization": "${access_token}"
                },
                "params": {
                    "deviceId": "",
                    "type": ""
                }
            },
            "expected_results": {
                "assert_form": "response_text_contents",
                "assert_data": "\"message\":\"未登录!\""
            }
        }
    ]
    # 创建执行器实例
    executor = TestCaseExecutor(base_url="http://10.0.106.2:8011")  # 替换为实际的base_url

    try:
        # 执行单接口测试
        executor.execute_test_case(test_case_data, "用户登录接口测试")

    finally:
        # 关闭连接
        executor.close()

