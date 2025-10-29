# -*- coding: utf-8 -*-
import re
import requests
import logging


logger = logging.getLogger('http_client')


def _replace_placeholders(text, context):
    """替换文本中的占位符 ${key}"""
    if not context or not text:
        return text

    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, lambda match: str(context.get(match.group(1), match.group(0))), text)


class HTTPClient:
    def __init__(self, base_url='', default_headers=None, timeout=10):
        """
        初始化 HTTP 客户端
        :param base_url: 基础URL（所有请求会基于此URL）
        :param default_headers: 默认请求头
        :param timeout: 默认超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')  # 移除末尾斜杠
        self.default_headers = default_headers or {'Content-Type': 'application/json'}
        self.timeout = timeout
        self.session = requests.Session()  # 创建会话保持连接

    def _send_request(self, method, url_path, **kwargs):
        """
        发送 HTTP 请求的核心方法
        :param method: HTTP 方法 ('GET', 'POST')
        :param url_path: url路径
        :param kwargs: requests 支持的参数（params, data, json, headers等）
        :return: 响应对象或 None（请求失败时）
        """
        # 构建完整URL
        url = f"{self.base_url}/{url_path.lstrip('/')}" if self.base_url else url_path

        # 合并默认请求头和自定义请求头
        headers = {**self.default_headers, **kwargs.pop('headers', {})}

        # 设置超时（优先使用调用时指定的超时）
        timeout = kwargs.pop('timeout', self.timeout)

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()  # 检查HTTP错误状态
            # logger.info(f"{method} {url} - Status {response.status_code}")
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - Error: {str(e)}")
            return None

    def get(self, url_path, params=None, **kwargs):
        """
        GET 请求
        :param url_path: url路径
        :param params: 查询参数字典
        :return: 响应对象或 None
        """
        response = self._send_request('GET', url_path, params=params, **kwargs)
        return response

    def post(self, url_path, data=None, json_data=None, **kwargs):
        """
        POST 请求
        :param url_path: url路径
        :param data: 表单数据（字典或字节）
        :param json_data: JSON 可序列化对象
        :return: 响应对象或 None
        """
        # 根据参数类型自动设置Content-Type
        if json_data is not None:
            kwargs['json'] = json_data
        elif data is not None:
            kwargs['data'] = data
        response = self._send_request('POST', url_path, **kwargs)
        return response

    def _replace_dict_placeholders(self, data, context):
        """递归替换字典中的占位符"""
        if isinstance(data, dict):
            return {k: self._replace_dict_placeholders(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_dict_placeholders(item, context) for item in data]
        elif isinstance(data, str):
            return _replace_placeholders(data, context)
        else:
            return data

    def request_with_params(self, method, url_path, context=None, **kwargs):
        """支持动态参数替换的请求方法"""
        # 替换URL中的动态参数
        url_path = _replace_placeholders(url_path, context)

        # 替换请求体中的动态参数
        if 'json' in kwargs and kwargs['json']:
            kwargs['json'] = self._replace_dict_placeholders(kwargs['json'], context)
        if 'data' in kwargs and kwargs['data']:
            kwargs['data'] = self._replace_dict_placeholders(kwargs['data'], context)

        # 替换请求头中的动态参数
        if 'headers' in kwargs and kwargs['headers']:
            kwargs['headers'] = self._replace_dict_placeholders(kwargs['headers'], context)

        return self._send_request(method, url_path, **kwargs)

    def close(self):
        """关闭会话连接"""
        self.session.close()


class APIAssert:
    def __init__(self):

        """
        初始化数据库、Redis连接
        """
        self.FailedFlag = False

    def response_status_equal(self, response, expectation=200):
        """断言响应状态码等于期望值"""
        assert_result = None
        try:
            actuality = response.status_code
            logger.info(f'期望结果为:{expectation}')
            logger.info(f'实际结果为:{actuality}')
            if actuality == expectation:
                # logger.info('通过')
                logger.info('<span style="color: green; font-weight: bold;">通过</span>')
                self.FailedFlag = True
            else:
                # logger.info('失败')
                logger.info('<span style="color: red; font-weight: bold;">失败</span>')
                self.FailedFlag = False
            if self.FailedFlag:
                assert_result = True
            else:
                assert_result = False
        except Exception as e:
            logger.error(f'期望结果为:{expectation}；异常信息为：{e}')
            # logger.info('失败')
            logger.info('<span style="color: red; font-weight: bold;">失败</span>')
            self.FailedFlag = False
        finally:
            return assert_result

    def response_text_contents(self, response, expectation):
        """断言响应内容包含期望值"""
        assert_result = None
        try:
            actuality = response.text
            logger.info(f'期望结果为:{expectation}')
            logger.info(f'实际结果为:{actuality}')
            if expectation in actuality:
                # logger.info('通过')
                logger.info('<span style="color: green; font-weight: bold;">通过</span>')
                self.FailedFlag = True
            else:
                # logger.info('失败')
                logger.info('<span style="color: red; font-weight: bold;">失败</span>')
                self.FailedFlag = False
            if self.FailedFlag:
                assert_result = True
            else:
                assert_result = False
        except Exception as e:
            logger.error(f'期望结果为:{expectation}；异常信息为：{e}')
            # logger.info('失败')
            logger.info('<span style="color: red; font-weight: bold;">失败</span>')
            self.FailedFlag = False
        finally:
            return assert_result

    def response_json_structure(self, response, expectation):
        """断言响应json中的数据结构与期望json数据结构一致"""
        assert_result = None
        try:
            actuality = response.json()
            logger.info(f'期望结果为:{expectation}')
            logger.info(f'实际结果为:{actuality}')
            match, differences = compare_structure(actuality, expectation)
            if match:
                # logger.info('通过')
                logger.info('<span style="color: green; font-weight: bold;">通过</span>')
                self.FailedFlag = True
            else:
                # logger.info('失败')
                logger.info('<span style="color: red; font-weight: bold;">失败</span>')
                logger.info(f'{differences}')
                self.FailedFlag = False

            if self.FailedFlag:
                assert_result = True
            else:
                assert_result = False
        except Exception as e:
            logger.error(f'期望结果为:{expectation}；异常信息为：{e}')
            # logger.info('失败')
            logger.info('<span style="color: red; font-weight: bold;">失败</span>')
            self.FailedFlag = False
        finally:
            return assert_result

    def response_json_contents(self, response, expectation):
        """断言响应json中键值对包含期望json中的键值对"""
        assert_result = None
        try:
            actuality = response.json()
            logger.info(f'期望结果为:{expectation}')
            logger.info(f'实际结果为:{actuality}')
            if expectation.items() <= actuality.items():
                # logger.info('通过')
                logger.info('<span style="color: green; font-weight: bold;">通过</span>')
                self.FailedFlag = True
            else:
                # logger.info('失败')
                logger.info('<span style="color: red; font-weight: bold;">失败</span>')

            if self.FailedFlag:
                assert_result = True
            else:
                assert_result = False
        except Exception as e:
            logger.error(f'期望结果为:{expectation}；异常信息为：{e}')
            # logger.info('失败')
            logger.info('<span style="color: red; font-weight: bold;">失败</span>')
            self.FailedFlag = False
        finally:
            return assert_result

    def databases_equal(self):
        """
        数据库表中的某个字段值等于期望结果，断言成功
        """
        pass

    def databases_contents(self):
        """
        数据库表中的某个字段值包含期望结果，断言成功
        """
        pass

    def redis_equal(self):
        """
        redis中的某个字段值等于期望结果，断言成功
        """
        pass

    def redis_contents(self):
        """
        redis中的某个字段值包含期望结果，断言成功
        """
        pass


def compare_structure(actuality, expectation, path=""):
    """
    比较两个JSON结构是否一致
    expectation: 标准JSON
    actuality: 要比较的JSON
    path: 当前路径（用于定位差异）
    返回: (是否一致, 差异描述)
    """
    # 检查类型是否一致
    if type(expectation) is not type(actuality):
        error = f"在 {path} 处类型不一致。期望类型 {type(expectation).__name__}，实际类型 {type(actuality).__name__}"
        return False, error

    if isinstance(expectation, dict):
        # 检查字典的键集合是否一致
        expectation_keys = set(expectation.keys())
        actuality_keys = set(actuality.keys())

        if expectation_keys != actuality_keys:
            missing = expectation_keys - actuality_keys
            extra = actuality_keys - expectation_keys
            error = f"在 {path} 处键不一致。"
            if missing:
                error += f"缺失键: {missing}"
            if extra:
                error += f"多余键: {extra}"
            return False, error

        # 递归检查每个键对应的值结构是否一致
        for key in expectation:
            new_path = f"{path}['{key}']"
            is_match, error_msg = compare_structure(expectation[key], actuality[key], new_path)
            if not is_match:
                return False, error_msg
        return True, "结构一致"

    elif isinstance(expectation, list):
        # 处理空列表
        if len(expectation) == 0 and len(actuality) == 0:
            return True, "结构一致"

        # 标准列表非空但比较列表为空
        if len(expectation) > 0 and len(actuality) == 0:
            return False, f"在 {path} 处：期望非空列表，但实际为空"

        # 比较列表元素结构
        for i, (expectation_item, actuality_item) in enumerate(zip(expectation, actuality)):
            new_path = f"{path}[{i}]"
            is_match, error_msg = compare_structure(expectation_item, actuality_item, new_path)
            if not is_match:
                return False, error_msg

        return True, "结构一致"

    else:
        # 基础类型（str, int, float, bool等）直接返回成功
        return True, "结构一致"


# 使用示例
if __name__ == "__main__":
    pass
