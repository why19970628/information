from flask import Flask
from redis import StrictRedis
import logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf.csrf import CSRFProtect, generate_csrf

from config import config_dict

redis_store = None
redis_store = StrictRedis()

# 在外部定义db变量
db = SQLAlchemy()

# 定义工厂方法
def create_app(config_name):

    app = Flask(__name__)

    # 根据传入的配置类名称，取出对应的配置类
    config = config_dict[config_name]

    # 加载配置类
    app.config.from_object(config)

    # 创建sqlalchemy对象，关联app
    db.init_app(app)

    # 调用日志方法，记录程序运行信息
    log_file(config.LEVEL_NAME)

    # 创建Session对象，读取app中的session配置信息
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    # 创建redis 对象
    global redis_store
    redis_store = StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

    # 将函数添加到系统默认的过滤器中
    from info.utils.commons import hot_news_filter
    # 参数1：函数的名字 参数2：过滤器的名字
    app.add_template_filter(hot_news_filter, 'my_filter')

    # 讲首页蓝图index_bp, 注册到app中
    from info.modules.index import index_bp
    app.register_blueprint(index_bp)

    # 将认证蓝图passport，注册到app中
    from info.modules.passport import passport_bp
    app.register_blueprint(passport_bp)

    # 将新闻蓝图news_bp, 注册到app中
    from info.modules.news import news_bp
    app.register_blueprint(news_bp)

    # 将用户蓝图profile_bp, 注册到app中
    from info.modules.profile import profile_bp
    app.register_blueprint(profile_bp)

    # 使用请求钩子拦截所有请求, 在返回的响应cookie设置csrf_token
    @app.after_request
    def after_request(resp):
        # 调用系统方法，获取csrf_token
        csrf_token = generate_csrf()

        # 将csrf_token 设置到cookie中
        resp.set_cookie('csrf_token', csrf_token)

        # 返回响应
        return resp

    return app


def log_file(LEVEL_NAME):
    # 设置日志的记录等级,常见的有四种,大小关系如下: DEBUG < INFO < WARNING < ERROR
    logging.basicConfig(level=LEVEL_NAME)  # 调试debug级,一旦设置级别那么大于等于该级别的信息全部都会输出
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
