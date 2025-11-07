# -*- coding: utf-8 -*-
import pytest
from core.windows_client import WinAppHandel


class TestCalculator:
    # 加法测试
    @pytest.mark.add
    @pytest.mark.parametrize("param, expected", [
        (('1', '2'), '=3'),
        (('2', '2'), '=4'),
    ])
    @pytest.mark.usefixtures("bz_calculator")
    def test_addition(self, bz_calculator, param, expected):
        """测试加法运算"""
        calc = WinAppHandel(bz_calculator)

        # 方法1: 使用图像识别操作
        calc.click_button(param[0], threshold=0.9)
        calc.click_button("+")
        calc.click_button(param[1], threshold=0.9)
        calc.click_button("=")
        assert calc.feature_exit(expected) is True

    # 减法测试
    @pytest.mark.subtract
    @pytest.mark.parametrize("param, expected", [
        (('5', '2'), '=3'),
        (('6', '1'), '=4'),
    ])
    @pytest.mark.usefixtures("bz_calculator")
    def test_subtract(self, bz_calculator, param, expected):
        """测试加法运算"""
        calc = WinAppHandel(bz_calculator)

        # 方法1: 使用图像识别操作
        calc.click_button(param[0], threshold=0.9)
        calc.click_button("-")
        calc.click_button(param[1], threshold=0.9)
        calc.click_button("=")
        assert calc.feature_exit(expected) is True
