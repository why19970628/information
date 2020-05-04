import logging


# 设置配置信息(基类配置信息)
class Config(object):
    # 调试信息
    DEBUG = True

    # redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 默认日志级别
    LEVEL_NAME = logging.DEBUG

    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 每当改变数据内容之后，在视图函数结束的时候会自动提交


# 开发环境配置信息
class DevelopConfig(Config):
    pass


# 生产(线上)环境配置信息
class ProductConfig(Config):
    DEBUG = False

    LEVEL_NAME = logging.ERROR


# 测试环境配置信息
class TestConfig(Config):
    pass


# 提供一个统一的访问入口
config_dict = {
    'develop': DevelopConfig,
    'product': ProductConfig,
    'test': TestConfig,
}