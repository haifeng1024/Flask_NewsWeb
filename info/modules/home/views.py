import logging

from flask import current_app

from info import sr
from info.modules.home import home_blu



# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    # sr.set("age", 20)
    # logging.error("出现了一个错误")
    # current_app.logger.error("出现了错误")
    return "index page"