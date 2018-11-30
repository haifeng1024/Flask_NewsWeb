from flask import Flask
from flask.ext.migrate import Migrate
from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis

from config import config_dict



def create_app(config_type):    # 工厂函数，外界提供物料，函数内部封装对象创建过程
    """
    创建应用
    :param config_type: 配置类型
    :return: flask 应用
    """
    # 根据不同的类型取出对应的配置子类
    config_class = config_dict.get(config_type)
    # 创建应用
    app = Flask(__name__)
    # 从对象中加载配置
    app.config.from_object(config_class)
    # 创建数据库操作对象
    db = SQLAlchemy(app)
    # 创建redis操作对象
    sr = StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 初始化Session存储
    Session(app)
    # 初始化迁移器
    Migrate(app, db)

    # 注册蓝图
    from info.modules.home import home_blu
    app.register_blueprint(home_blu)

    return app