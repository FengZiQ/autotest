# -*- coding: utf-8 -*-
import json
import logging
from typing import List, Dict, Any
from config.ai_config import AIConfig
from ai.deepseek_client import DeepSeekClient

logger = logging.getLogger('testcase_generator')


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

    def generate_testcases(self, interface_path: str, scenarios: List[str] = None) -> Dict[str, Any]:
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

        if scenarios is None:
            scenarios = ["正常流程", "边界值测试", "异常情况"]

        all_testcases = []

        for scenario in scenarios:
            logger.info(f"生成测试场景: {scenario}")

            # 调用AI生成测试用例
            result = self.client.generate_testcase(interface_info, scenario)

            if "test_cases" in result:
                all_testcases.extend(result["test_cases"])
            else:
                # 如果返回格式不同，尝试直接使用
                all_testcases.append(result)

        return {"test_cases": all_testcases}

    def save_testcases(
            self,
            service_name: str,
            interface_name: str,
            testcases: Dict[str, Any]
    ):
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

        logger.info(f"测试用例已保存: {filepath}")
        return filepath