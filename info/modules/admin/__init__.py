from flask import Blueprint, request, session, redirect

# 1.创建蓝图对象
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 2.装饰视图函数
from . import views


# 使用请求钩子，拦截用户的请求，只有访问了admin_bp,所装饰的视图函数需要拦截
# 1.拦截的是访问了非登录页面
# 2.拦截的是普通用户
@admin_bp.before_request
def before_request():
    # 判断访问的是否是非登录页面
    if not request.url.endswith('/admin/login'):
        if not session.get('is_admin'):
            return redirect('/')