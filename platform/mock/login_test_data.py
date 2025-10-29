# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from datetime import datetime

# 创建蓝图
mock_login = Blueprint('mock_login', __name__)

# 模拟用户数据
login_data = {
    "access_token": "cn-8b894f1b-4f39-4fdb-9b48-f44f13c0fee8",
    "refresh_token": "cn-e24938d3-0936-464b-9ba9-fe92a978f35a",
    "scope": "account_security ent_account_read account_token_login account_privacy_write account_info_write account_info_read",
    "token_type": "bearer",
    "expires_in": 504018
}

user_info_data = {
    "userId": "1076249187848705",
    "tcId": "7322174849002799604",
    "userName": "1f0d4652bb7023f6",
    "nickName": "13717641870",
    "mobile": "13717641870",
    "accountType": "PERSON",
    "orgId": "",
    "organName": "",
    "testUser": 0
}


@mock_login.route('/auth/userlogin', methods=['POST'])
def get_users():
    data = request.json
    user_name = data.get('userName')
    print(user_name)
    if len(user_name) != 11:
        return jsonify({
            "success": False,
            "code": 998,
            "message": "用户名或者密码无效",
            "data": {
                "error_description": "用户名或者密码无效",
                "error": "invalid_request"
            },
            "responseTime": 1761729973262
        })
    return jsonify({
        "code": 200,
        "success": True,
        "data": login_data,
        "responseTime": 1761729973262
    })


@mock_login.route('/user/getUserInfo', methods=['GET', 'POST'])
def create_user():
    return jsonify({
        "code": 200,
        "success": True,
        "data": user_info_data,
        "responseTime": 1761729973262
    })