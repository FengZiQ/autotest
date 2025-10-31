# -*- coding: utf-8 -*-
import pytest
from core.api_test_executor import TestCaseExecutor


# 接口测试相关夹具
@pytest.fixture(scope="session")
def http_client():
    client = TestCaseExecutor(base_url="http://127.0.0.1:5000")
    yield client
    client.close()


