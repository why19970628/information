from flask import render_template
from flask import redirect, g, request, jsonify

from . import profile_bp
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from info.models import db


# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_bp.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.携带用户数据，渲染页面
        if not g.user:
            # 如果没有登录，重定向到首页
            redirect('/')
        return render_template('news/user_base_info.html', user_info=g.user.to_dict())
    else:
        # 3.post请求
        # 4.获取参数
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 5.校验参数，为空校验
        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

        if not gender in ['MAN', 'WOMAN']:
            return jsonify(errno=RET.DATAERR, errmsg='性别异常')

        # 6.修改用户数据
        g.user.signature = signature
        g.user.nick_name = nick_name
        g.user.gender = gender

        db.session.add(g.user)
        db.session.commit()

        # 7.返回响应
        return jsonify(errno=RET.OK, errmsg='修改成功')


@profile_bp.route('/info')
@user_login_data
def user_info():
    # 1.判断用户是否登录
    if not g.user:
        return redirect('/')
    # 2.携带数据渲染页面
    data = {
        'user_info': g.user.to_dict()
    }
    return render_template('news/user.html', data=data)
