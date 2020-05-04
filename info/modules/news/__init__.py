from flask import Blueprint

# 1.创建蓝图对象
news_bp = Blueprint('news', __name__, url_prefix='/news')

# 2.导入views 装饰视图函数
from . import views