# -*- coding: utf-8 -*-
import pytest


class TestCalculator:
    @pytest.mark.parametrize("param, expected", [
        (
                [
                    {"button_name": "报价决策", "threshold": 0.8, "target_pos": 5},
                    {"button_name": "开标记录", "threshold": 0.8, "target_pos": 5},
                ],
                {"feature_name": "开标记录_搜索"}
        )
    ])
    @pytest.mark.usefixtures("app_a")
    def test_a(self, app_a, param, expected):
        for p in param:
            app_a.click(
                feature_name=p.get('button_name'),
                threshold=p.get('threshold'),
                target_pos=p.get('target_pos')
            )

        assert app_a.assert_feature_exist(feature_name=expected.get('feature_name'))
