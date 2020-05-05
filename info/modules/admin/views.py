from flask import render_template, request, current_app, jsonify, session, redirect, g
import time
from datetime import datetime, timedelta

from . import admin_bp
from info.models import User
from info.models import db
from info.models import News
from info.models import Category
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from info.utils.image_storage import image_storage
from info import constants



# 获取/登陆,管理员登陆
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # 1.判断请求方式，如果是GET，直接渲染页面
    if request.method == 'GET':
        # 判断管理员是否已经登录过了，如果登录了直接跳转到首页
        if session.get('is_admin'):
            return redirect('/admin/index')
        return render_template('admin/login.html')

    # 2.如果是POST请求，获取参数
    username = request.form.get('username')
    password = request.form.get('password')

    # 3.为空校验
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数不全')

    # 4.根据用户名取出管理员对象，判断管理员是否存在
    try:
        admin = User.query.filter(
            User.mobile == username,
            User.is_admin == True
        ).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg='用户查询失败')

    if not admin:
        return render_template('admin/login.html', errmsg='管理员不存在')

    # 5.判断管理员的密码是否正确
    if not admin.check_password(password):
        return render_template('admin/login.html', errmsg='密码错误')

    # 6.管理员的session信息记录
    session['user_id'] = admin.id
    session['is_admin'] = True

    # 7.重定向到首页展示
    return redirect('/admin/index')

@admin_bp.route('/index')
@user_login_data
def admin_index():

    data = {
        'user_info': g.user.to_dict() if g.user else ""
    }
    return render_template('admin/index.html', data=data)