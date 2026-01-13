# -*- coding: utf-8 -*-
"""
AI自动化测试工具
用于解析接口文档和生成测试用例
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from ai.interface_parser import InterfaceParser
from ai.testcase_generator import TestCaseGenerator
from config.ai_config import AIConfig


def parse_interfaces():
    """解析接口文档"""
    parser = argparse.ArgumentParser(description='解析接口文档')
    parser.add_argument('service', help='服务名称')
    parser.add_argument('--doc', help='文档文件名（可选）')
    parser.add_argument('--output', help='输出目录（可选）')

    args = parser.parse_args()

    try:
        interface_parser = InterfaceParser()

        # 解析文档
        interfaces = interface_parser.parse_document(args.service, args.doc)

        # 保存接口
        for interface in interfaces:
            interface_parser.save_interface(args.service, interface)

        print(f"✓ 成功解析并保存了 {len(interfaces)} 个接口")

    except Exception as e:
        print(f"✗ 解析失败: {e}")
        sys.exit(1)


def generate_testcases():
    """生成测试用例"""
    parser = argparse.ArgumentParser(description='生成测试用例')
    parser.add_argument('interface', help='接口文件路径，如 order_service/orderCreate.json')
    parser.add_argument('--scenarios', nargs='+',
                        default=["正常流程", "边界值测试", "异常情况"],
                        help='测试场景列表')

    args = parser.parse_args()

    try:
        # 从接口路径中提取服务名
        parts = args.interface.split('/')
        if len(parts) != 2:
            raise ValueError("接口路径格式应为: service_name/interface_file.json")

        service_name = parts[0]
        interface_file = parts[1]
        interface_name = Path(interface_file).stem  # 移除扩展名

        generator = TestCaseGenerator()

        # 生成测试用例
        testcases = generator.generate_testcases(args.interface, args.scenarios)

        # 保存测试用例
        generator.save_testcases(service_name, interface_name, testcases)

        print(f"✓ 成功生成了 {len(testcases.get('test_cases', []))} 个测试用例")

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI自动化测试工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 解析接口子命令
    parse_parser = subparsers.add_parser('parse', help='解析接口文档')
    parse_parser.add_argument('service', help='服务名称')
    parse_parser.add_argument('--doc', help='文档文件名（可选）')

    # 生成测试用例子命令
    gen_parser = subparsers.add_parser('generate', help='生成测试用例')
    gen_parser.add_argument('interface', help='接口文件路径')
    gen_parser.add_argument('--scenarios', nargs='+',
                            default=["正常流程", "边界值测试", "异常情况"])

    args = parser.parse_args()

    if args.command == 'parse':
        try:
            interface_parser = InterfaceParser()
            interfaces = interface_parser.parse_document(args.service, args.doc)

            for interface in interfaces:
                interface_parser.save_interface(args.service, interface)

            print(f"✓ 成功解析并保存了 {len(interfaces)} 个接口")

        except Exception as e:
            print(f"✗ 解析失败: {e}")
            sys.exit(1)

    elif args.command == 'generate':
        try:
            parts = args.interface.split('/')
            if len(parts) != 2:
                raise ValueError("接口路径格式应为: service_name/interface_file.json")

            service_name = parts[0]
            interface_file = parts[1]
            interface_name = Path(interface_file).stem

            generator = TestCaseGenerator()
            testcases = generator.generate_testcases(args.interface, args.scenarios)
            generator.save_testcases(service_name, interface_name, testcases)

            print(f"✓ 成功生成了 {len(testcases.get('test_cases', []))} 个测试用例")

        except Exception as e:
            print(f"✗ 生成失败: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()