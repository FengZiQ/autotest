# -*- coding: utf-8 -*-
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from config.ai_config import AIConfig
from ai.deepseek_client import DeepSeekClient

logger = logging.getLogger('interface_parser')


class InterfaceParser:
    """接口文档解析器"""

    def __init__(self):
        self.client = DeepSeekClient()
        self.interface_dir = AIConfig.API_INTERFACE_DIR
        self.docs_dir = AIConfig.API_DOCS_DIR

    def read_document(self, doc_path: Path) -> str:
        """读取文档内容"""
        if not doc_path.exists():
            raise FileNotFoundError(f"文档不存在: {doc_path}")

        suffix = doc_path.suffix.lower()

        if suffix == '.json':
            with open(doc_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        elif suffix == '.yaml' or suffix == '.yml':
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
        service_docs_dir = self.docs_dir / service_name
        if not service_docs_dir.exists():
            raise FileNotFoundError(f"服务文档目录不存在: {service_docs_dir}")

        if doc_filename:
            doc_path = service_docs_dir / doc_filename
            if not doc_path.exists():
                raise FileNotFoundError(f"文档文件不存在: {doc_path}")
            doc_files = [doc_path]
        else:
            # 查找所有支持的文档文件
            doc_files = []
            for suffix in AIConfig.SUPPORTED_DOC_FORMATS:
                doc_files.extend(list(service_docs_dir.glob(f"*{suffix}")))

            if not doc_files:
                raise FileNotFoundError(f"未找到支持的文档格式: {service_docs_dir}")

            # 按优先级排序
            priority_order = ['.json', '.yaml', '.yml', '.md', '.txt', '.html']
            doc_files.sort(key=lambda x: priority_order.index(x.suffix.lower())
            if x.suffix.lower() in priority_order else len(priority_order))

            doc_path = doc_files[0]

        logger.info(f"使用文档文件: {doc_path}")

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
        interface_name = interface_info.get("interface_name", "unknown")
        # 移除特殊字符，只保留字母数字和下划线
        safe_name = "".join(c for c in interface_name if c.isalnum() or c in ('_', '-')).lower()
        filename = f"{safe_name}.json"

        filepath = service_dir / filename

        # 保存JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(interface_info, f, ensure_ascii=False, indent=2)

        logger.info(f"接口已保存: {filepath}")
        return filepath
