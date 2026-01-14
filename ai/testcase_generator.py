# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any
from config.ai_config import AIConfig
from ai.deepseek_client import DeepSeekClient


class TestCaseGenerator:
    """测试用例生成器"""

    def __init__(self):
        self.client = DeepSeekClient()
        self.test_data_dir = AIConfig.TEST_DATA_DIR
        self.interface_dir = AIConfig.API_INTERFACE_DIR

    def load_interface(self, interface_path: str) -> Dict[str, Any]:
        """
        加载接口信息

        Args:
            interface_path: 接口文件路径，如 "order_service/orderCreate.json"

        Returns:
            接口信息字典
        """
        filepath = self.interface_dir / interface_path
        if not filepath.exists():
            raise FileNotFoundError(f"接口文件不存在: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_testcases(self, interface_path: str):
        """
        为接口生成测试用例

        Args:
            interface_path: 接口文件路径
            scenarios: 测试场景列表

        Returns:
            生成的测试用例
        """
        # 加载接口信息
        interface_info = self.load_interface(interface_path)

        # 调用AI生成测试用例
        testcases = self.client.generate_testcase(interface_info)

        return testcases

    def save_testcases(self, service_name: str, interface_name: str, testcases: List):
        """
        保存测试用例到文件

        Args:
            service_name: 服务名称
            interface_name: 接口名称
            testcases: 测试用例数据
        """
        service_dir = self.test_data_dir / service_name
        service_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        safe_name = "".join(c for c in interface_name if c.isalnum() or c in ('_', '-')).lower()
        filename = f"{safe_name}.json"

        filepath = service_dir / filename

        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(testcases, f, ensure_ascii=False, indent=2)

        print(f"测试用例已保存: {filepath}")
        return filepath


if __name__ == "__main__":
    # 简单测试TestCaseGenerator
    tcg = TestCaseGenerator()
    tcs = tcg.generate_testcases("user_center/账号密码登录.json")
    tcg.save_testcases("user_center", "账号密码登录", tcs)
