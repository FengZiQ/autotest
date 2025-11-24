# -*- coding: utf-8 -*-
import pytest
from appium.webdriver.common.appiumby import AppiumBy


class TestCalculator:
    @pytest.mark.usefixtures("netease_pris")
    def test_open_login_page(self, netease_pris):
        netease_pris.click_element(
            locator=(
                AppiumBy.XPATH,
                '//android.widget.TextView[@resource-id="com.netease.pris:id/title" and @text="我的"]'
            )
        )
        netease_pris.click_element(
            locator=(
                AppiumBy.ID,
                'com.netease.pris:id/button_login'
                # 'com.netease.pris:id/home_pro_textView_my_note_text'
            )
        )
        page_feature1 = netease_pris.assert_element_present(
            locator=(
                AppiumBy.ID,
                'com.netease.pris:id/ui_login_name'
            )
        )
        if not page_feature1:
            netease_pris.take_screenshot('haha.png')
        assert page_feature1

