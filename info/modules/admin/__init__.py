from flask import Blueprint

# 1.创建蓝图对象
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 2.导入views文件装饰视图函数
from . import views