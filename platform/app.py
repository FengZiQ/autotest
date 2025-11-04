# -*- coding: utf-8 -*-
from flask import Flask

# 注册蓝图
from routes import main_bp
from mock.user_service import mock_login
from mock.order_service import mock_order


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['JSON_AS_ASCII'] = False  # 禁用ASCII编码，强制使用UTF-8
app.config['DEFAULT_CHARSET'] = 'utf-8'  # 设置默认字符集

app.register_blueprint(main_bp)
app.register_blueprint(mock_login, url_prefix='//gbsp')
app.register_blueprint(mock_order, url_prefix='')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
