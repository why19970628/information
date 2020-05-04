from flask import request, current_app, make_response

from . import passport_bp
from info.utils.captcha.captcha import captcha
from info import redis_store
from info import constants

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