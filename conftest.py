# -*- coding: utf-8 -*-
import logging
import sys
import os.path
import pytest
import datetime
from utils.logger import log_record
from utils.path_util import get_path


@pytest.fixture(scope="session", autouse=True)
def global_logger():
    """全局日志记录器"""
    logging.info("===== 测试套件开始 =====")
    yield
    logging.info("===== 测试套件结束 =====")


@pytest.fixture(scope="function")
def test_logger(request):
    """为每个测试创建专用日志"""
    test_name = request.node.name
    logger = logging.getLogger(f"test.{test_name}")
    logger.info(f"----- 开始测试: {test_name} -----")
    yield logger
    logger.info(f"----- 结束测试: {test_name} -----")


def pytest_configure(config):
    """配置测试环境"""
    # 设置报告目录
    reports_dir = get_path('reports')
    if os.path.exists(reports_dir):
        os.makedirs(os.path.dirname(reports_dir), exist_ok=True)

    # 创建截图和日志目录
    screenshots_dir = get_path('reports', 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)
    logs_dir = get_path('reports', 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # 设置资源目录为 screenshots 的父目录
    config.option.assetpath = screenshots_dir

    # 带时间戳的报告文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = f"{reports_dir}/report_{timestamp}.html"

    # 动态设置报告路径
    config.option.htmlpath = str(html_report)
    config.option.self_contained_html = True

    # 初始化统计字典
    pytest.stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

    # 初始化日志系统
    log_record(timestamp)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """处理测试报告"""
    outcome = yield
    report = outcome.get_result()

    # 只在测试函数调用阶段处理
    if report.when == "call":
        pytest.stats["total"] += 1
        if report.outcome == "passed":
            pytest.stats["passed"] += 1
        elif report.outcome == "failed":
            pytest.stats["failed"] += 1
        elif report.outcome == "skipped":
            pytest.stats["skipped"] += 1

        report_extras = getattr(report, "extras", [])

        # 优化日志部分
        if hasattr(report, "sections"):
            new_sections = []
            for section in report.sections:
                # 保留主要的日志部分
                if section[0].startswith("Captured log call"):
                    new_sections.append(section)
                # 保留自定义的额外信息
                elif section[0] == "Extra":
                    new_sections.append(section)
            report.sections = new_sections

        report.extras = report_extras


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "自动化测试报告"


def pytest_html_results_summary(summary):
    # 计算通过率
    total = pytest.stats["total"]
    passed = pytest.stats["passed"]
    pass_rate = (passed / total) * 100 if total > 0 else 0

    # 添加中文概述 - 使用原始HTML
    summary.append(f'<p>通过率: {pass_rate:.2f}%</p>')


