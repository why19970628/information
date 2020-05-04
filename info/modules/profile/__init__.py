from flask import Blueprint

# 1.创建蓝图对象
profile_bp = Blueprint('profile', __name__, url_prefix='/user')

# 2.使用蓝图对象装饰路由
from . import views