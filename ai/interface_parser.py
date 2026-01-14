# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Any
from config.ai_config import AIConfig
from ai.deepseek_client import DeepSeekClient


class InterfaceParser:
    """接口文档解析器"""

    def __init__(self, api_docs_dir):
        self.client = DeepSeekClient()
        self.interface_dir = AIConfig.API_INTERFACE_DIR
        self.docs_dir = api_docs_dir

    def read_document(self, doc_path: str) -> str:
        """读取文档内容"""
        suffix = doc_path.split('.')[-1].lower()

        if suffix == 'json':
            with open(doc_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        elif suffix == 'yaml' or suffix == 'yml':
            import yaml
            with open(doc_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            # 文本格式直接读取
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()

    def parse_document(self, service_name: str, doc_filename: str = None) -> Dict[str, Any]:
        """
        解析接口文档

        Args:
            service_name: 服务名称
            doc_filename: 文档文件名，如果为None则查找服务目录下的第一个文档

        Returns:
            解析后的接口列表
        """
        # 查找文档文件
        if not os.path.isdir(self.docs_dir):
            raise FileNotFoundError(f"接口文档目录不存在: {self.docs_dir}")

        doc_path = os.path.join(self.docs_dir, doc_filename)

        if not os.path.isfile(doc_path):
            raise FileNotFoundError(f"接口文档文件不存在: {doc_path}")

        # 读取文档内容
        doc_content = self.read_document(doc_path)

        # 调用AI解析
        interfaces = self.client.parse_interface(doc_content, service_name)

        return interfaces

    def save_interface(self, service_name: str, interface_info: Dict[str, Any]):
        """
        保存接口信息到JSON文件

        Args:
            service_name: 服务名称
            interface_info: 接口信息
        """
        service_dir = self.interface_dir / service_name
        service_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        interface_name = interface_info.get("interface_name", "unnamed_interface")
        # 移除特殊字符，只保留字母数字和下划线
        safe_name = "".join(c for c in interface_name if c.isalnum() or c in ('_', '-')).lower()
        filename = f"{safe_name}.json"

        filepath = service_dir / filename

        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interface_info, f, ensure_ascii=False, indent=2)

        print(f"接口已保存: {filepath}")
        return filepath


if __name__ == "__main__":
    # 简单测试InterfaceParser
    parser = InterfaceParser(api_docs_dir=r"D:\files\api_docs")
    service = "user_center"
    try:
        interfaces_info = parser.parse_document(service_name=service, doc_filename="login.txt")
        print(interfaces_info)
        parser.save_interface(service_name=service, interface_info=interfaces_info)
    except Exception as e:
        print(f"接口解析失败: {e}")

