# -*- coding: utf-8 -*-
import json
import logging
from openai import OpenAI
from config.ai_config import AIConfig

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(self):
        self.api_key = AIConfig.DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=AIConfig.DEEPSEEK_API_BASE
        )

    def chat_completion(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = None,
            max_tokens: int = None
    ) -> str:
        """
        调用DeepSeek API进行对话

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            AI响应文本
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=AIConfig.DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature or AIConfig.TEMPERATURE,
                max_tokens=max_tokens or AIConfig.MAX_TOKENS,
                response_format={"type": "json_object"}  # 强制返回JSON格式
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"调用DeepSeek API失败: {e}")
            raise

    def parse_interface(self, doc_content: str, service_name: str):
        """
        解析接口文档

        Args:
            doc_content: 接口文档内容
            service_name: 服务名称

        Returns:
            解析后的接口结构
        """
        from ai.prompt_templates import INTERFACE_PARSE_TEMPLATE

        prompt = INTERFACE_PARSE_TEMPLATE.format(
            service_name=service_name,
            doc_content=doc_content
        )

        response = self.chat_completion(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"解析AI响应JSON失败: {e}")
            logger.debug(f"原始响应: {response}")
            raise

    def generate_testcase(self, interface_info: dict, service_name="", interface_name=""):
        """
        生成测试用例

        Args:
            interface_info: 接口信息
            service_name: 服务名称
            interface_name: 接口名称

        Returns:
            生成的测试用例
        """
        from ai.prompt_templates import TESTCASE_GENERATE_TEMPLATE

        prompt = TESTCASE_GENERATE_TEMPLATE.format(
            interface_info=json.dumps(interface_info, ensure_ascii=False, indent=2),
            service_name=service_name,
            interface_name=interface_name
        )

        response = self.chat_completion(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"解析测试用例JSON失败: {e}")
            raise


if __name__ == "__main__":
    # 简单测试DeepSeekClient
    client = DeepSeekClient()
    client.parse_interface("示例接口文档内容", "示例服务")