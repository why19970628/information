from flask import Blueprint

# 1.创建蓝图对象
index_bp = Blueprint('index', __name__)

# 2.导入views文件装饰视图函数
from . import views