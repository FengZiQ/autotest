INTERFACE_PARSE_TEMPLATE = """你是一个专业的API接口文档解析器。请根据提供的接口文档内容，提取并结构化接口信息。

要求：
1. 分析接口文档，提取出所有接口信息
2. 必须包含以下字段：
   - method: HTTP方法（GET/POST）
   - url_path: 接口路径
   - headers: 请求头信息（如果有）
   - data/params: method值为GET时使用params，为POST时使用data。请求参数结构，每个参数需要标注类型和是否必填
   - response: 响应结构
   - description: 接口功能描述

输入文档：
服务名称：{service_name}
文档内容：
{doc_content}

请按照以下JSON格式返回结构化信息：
{{
    "interface_name": "接口名称",
    "method": "POST",
    "url_path": "/order/create",
    "headers": {{"content-type": "application/json"}},
    "data": {{
        "params1": {{"type": "string", "required": true, "detail": ""}},
        "params2": {{"type": "int","required": false, "detail": ""}}
    }},
    "response": {{
        "params1": {{"type": "string", "detail": ""}}
    }},
    "description": "接口功能描述"
}}

注意：
1. 必须返回有效的JSON，不要包含其他文本
2. 字段类型要准确（string, int, float, boolean）
3. 嵌套结构要完整解析
4. 如果文档中没有某些信息，可以留空但必须包含字段
"""

TESTCASE_GENERATE_TEMPLATE = """你是一名经验丰富的测试工程师。请根据给定的接口信息，生成具体的测试用例数据。

接口信息：
{interface_info}

测试场景：
正常流程，边界值，异常输入

要求：
1. 正常流程场景，由必填写段组成一条用例，每个没必填字段生成一条用例
2. 边界值场景，没有边界约束的不生成边界值用例。对于存在边界约束的字段使用最小值和最大值各生成一条用例
3. 异常输入场景，每个必填字段缺失生成一条用例，每个字段使用错误类型生成一条用例，有边界约束的字段使用上下界外的值各生成一条用例

请按照以下JSON数组形式输出：
[
    {{
        "case_name": "",
        "actions": {{
            "_interface": "{service_name}/{interface_name}.json",
            "data": {{
                "params1": "",
                "params1": ""
            }},
            "extract": {{
                "order_id": "data.orderId"
            }}
        }},
        "expected_results": {{
            "assert_form": "断言方式（响应体结构一致/响应体有键值对/响应体内容包含/响应状态码等于）",
            "assert_data": {{}}
        }}
    }}
]

注意：
1. 数组由多条用例组成，每条用例为一个字典
2. case_name字段为用例名称，描述用例目的
3. 每条用例必须包含actions和expected_results字段
4. actions中的_interface字段值不变
5. actions中的data/params字段由接口信息中method值决定，为GET时使用params，为POST时使用data
6. actions中的extract字段用于提取响应数据中的信息，用以后续用例参数化使用，不提取时没有该字段。格式为"变量名": "响应体路径"，如 "order_id": "data.orderId"
7. expected_results中必须包含assert_form和assert_data字段，内容为以下二个对象中的任意一个：
    {{
        "assert_form": "响应状态码等于",
        "assert_data": 200 # 值为Int类型，http状态码, 如200
    }}
    {{
        "assert_form": "响应体结构一致",
        "assert_data": {{}} # 值为dict，断言response.json()与模板一致
    }}
8. 正向用例的expected_results使用“响应体结构一致”，异常用例使用“响应状态码等于”
9. 返回格式必须是有效的数组JSON，不要包含其他文本。
"""