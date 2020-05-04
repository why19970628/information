import logging
from redis import StrictRedis

# 设置配置信息(基类配置信息)
class Config(object):
    # 调试信息
    DEBUG = True

    # session签名用的秘钥
    SECRET_KEY = 'fdsafhudsafdjksafkdjsahfkdsj'

    # redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 默认日志级别
    LEVEL_NAME = logging.DEBUG

    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True # 每当改变数据内容之后，在视图函数结束的时候会自动提交

    # session配置
    SESSION_TYPE = 'redis' # 设置redis存储的类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT) # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True # 设置签名存储


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