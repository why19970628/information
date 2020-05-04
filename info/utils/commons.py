from flask import session, current_app, g, redirect, url_for, request
from info.models import User
from functools import wraps

# 定义登录装饰器，封装用户的登录数据
def user_login_data(view_func):
    # 加上不会修改被装饰的函数
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 1.通过session获取用户的登录信息
        user_id = session.get('user_id')

        # 2.通过user_id取出用户对象
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 3.将user数据封装到g对象
        g.user = user
        return view_func(*args, **kwargs)
    return wrapper


# 自定义过滤器实现热门新闻的颜色过滤
def hot_news_filter(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ""

