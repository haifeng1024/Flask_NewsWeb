from datetime import timedelta
from redis import StrictRedis


# 封装所有配置
class Config():
    DEBUG = True  # 开启调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/info24"  # 数据库连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的ip地址
    REDIS_PORT = 6379  # redis的端口
    SESSION_TYPE = "redis"  # 设置session存储的方式  redis 性能好 可以设置过期时间
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置保存数据的redis操作对象
    SESSION_USE_SIGNER = True  # 设置sessionid是否加密
    SECRET_KEY = "0uapub3iKhrMyb7MRSHlg8Jvjw0q09jIXDPzXytTVqlPa8meOJo2/Y3nQI0mx2Re"  # 应用秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置session过期时间, 默认就支持设置过期时间


# 针对不同的环境设置不同的配置信息（配置信息子类化）
class DevelopmentConfig(Config):
    DEBUG = True    # 开发环境


class ProductConfig(Config):
    DEBUG = False   # 生产环境

config_dict = {
    "pro":ProductConfig,
    "dev":DevelopmentConfig
}