from flask import current_app, render_template

from info.modules.home import home_blu



# 使用蓝图来注册路由
@home_blu.route("/")
def index():

    return render_template("index.html")