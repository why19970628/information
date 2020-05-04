from flask import request, current_app, make_response, jsonify, session
import re
import random
from datetime import datetime

from . import passport_bp
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants
from info.utils.response_code import RET
from info.libs.yuntongxun.sms import CCP
from info.models import User, db


# 退出登陆
# 请求路径: /passport/logout
# 请求方式: POST
# 请求参数: 无
# 返回值: errno, errmsg
@passport_bp.route('/logout', methods=['POST'])
def logout():
    # 1.清除session信息
    session.pop('user_id', None)

    # 2.返回响应
    return jsonify(errno=RET.OK, errmsg='退出成功')


# 登陆用户
# 请求路径: /passport/login
# 请求方式: POST
# 请求参数: mobile,password
# 返回值: errno, errmsg
@passport_bp.route('/login', methods=['POST'])
def login():
    # 1.获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')

    # 2.校验参数, 为空校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 3.通过手机号码，到数据库查询用户对象
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户失败')

    # 4.判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='该用户不存在')

    # 5.校验密码是否正确
    if not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='密码错误')

    # 6.讲用户的登录信息保存到session中
    session['user_id'] = user.id

    # 6.1 记录用户最后一次的登录时间
    # 记录登录时间，是为了方便后期进行用户的活跃统计
    user.last_login = datetime.now()

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='修改用户登录时间错误')

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg='登录成功')


# 注册用户
# 请求路径: /passport/register
# 请求方式: POST
# 请求参数: mobile, sms_code,password
# 返回值: errno, errmsg
@passport_bp.route('/register', methods=['POST'])
def register():
    # 1.获取参数
    dict_data = request.json
    mobile = dict_data.get('mobile')
    sms_code = dict_data.get('sms_code')
    password = dict_data.get('password')

    # 2.校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 3.手机号作为key取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码取出失败')

    # 4.判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已经过期')

    # 5.判断验证码是否正确
    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码填写错误')

    # 6.删除短信验证码
    try:
        redis_store.delete('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码删除失败')

    # 7. 创建用户对象
    user = User()

    # 8. 设置用户对象属性
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile
    user.signature = '改用户很懒，什么都没写'

    # 9. 保存用户到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='用户注册失败')

    # 10. 返回响应
    return jsonify(errno=RET.OK, errmsg='注册成功')


# 获取短信验证码
# 请求路径: /passport/sms_code
# 请求方式: POST
# 请求参数: mobile, image_code,image_code_id
# 返回值: errno, errmsg
@passport_bp.route('/sms_code', methods=['POST'])
def sms_code():
    # 1.获取参数
    dict_data = request.json
    mobile = dict_data.get('mobile')
    image_code = dict_data.get('image_code')
    image_code_id = dict_data.get('image_code_id')

    # 2.为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 3.检验手机的格式
    if not re.match(r'1[3-9]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')

    # 4.通过图片验证码编号，获取图片验证码
    try:
        redis_image_code = redis_store.get('image_code:%s' %image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='操作redis失败')

    # 5.判断图片验证是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已经过期')

    # 6.判断图片验证码是否正确
    if image_code.upper() != redis_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码填写错误')

    # 7.删除redis 中的图片验证码
    try:
        redis_store.delete('image_code:%s' %image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='删除redis图片验证码失败')

    # 8.生成一个随机的短信验证码，条用ccp 发送短信，判断是否发送成功
    sms_code = "%06d" %(random.randint(0, 999999))

    current_app.logger.debug('短信验证码是 = %s' %sms_code)

    # ccp = CCP()
    # # 参数1: mobile 要给那个手机发送短信 参数2 ["验证码", 有效期] 参数3: 短信模板的编号: 默认1
    # result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    #
    # if result == -1:
    #     return jsonify(errno=RET.DATAERR, errmsg='短信发送失败')

    # 9.保存短信验证码到redis中
    try:
        redis_store.set('sms_code:%s' %mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码保存到redis失败')

    # 10. 返回响应
    return jsonify(errno=RET.OK, errmsg='短信发送成功')


# 功能: 获取图片验证码
# 请求路径: /passport/image_code
# 请求方式: GET
# 请求参数: cur_id, pre_id
# 返回值: 图片验证码
@passport_bp.route('/image_code')
def image_code():

    # 1.获取前端传递的参数
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')

    # 2.调用generate_captcha 获取图片验证码编号，验证码值，图片(二进制)
    name, text, image_data = captcha.generate_captcha()

    # 3.将图片验证码的值保存到redis

    try:
        # 参数1: key, 参数2: value, 参数3: 有效期
        redis_store.set('image_code:%s' %cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('image_code:%s' %pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return '图片验证码操作失败'

    # 4.返回图片
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response