# -*- coding: utf-8 -*-
import random
from flask import Blueprint, jsonify, request
from datetime import datetime

# 创建蓝图
mock_order = Blueprint('mock_order', __name__)


@mock_order.route('/order/create', methods=['POST'])
def get_users():
    order_id = random.randint(100000, 10000000)
    return jsonify({
        "success": True,
        "code": 200,
        "message": "订单创建成功",
        "data": {
            "orderId": order_id,
            "orderNumber": f"D{datetime.now().strftime('%Y%m%d')}ID{order_id}"
        }
    })


@mock_order.route('/order/getInfo', methods=['GET', 'POST'])
def create_user():
    order_id = random.randint(100000, 10000000)
    return jsonify({
        "code": 200,
        "success": True,
        "data": {
            "orderId": order_id,
            "orderNumber": f"D{datetime.now().strftime('%Y%m%d')}ID{order_id}",
            "address": '西安市鱼化寨街道',
            "goods": '货物',
            "customerInfo": {
                'userId': 253262,
                'userName': '测试账户',
                'mobile': '13700000000'
            }
        }
    })
