import logging
from flask import render_template, current_app

from . import index_bp
from info import redis_store


@index_bp.route('/')
def show_index():
    # 渲染首页
    return render_template('news/index.html')


# 处理网站logo
@index_bp.route('/favicon.ico')
def get_web_logo():

    return current_app.send_static_file('news/favicon.ico')

