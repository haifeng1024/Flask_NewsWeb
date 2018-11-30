from flask import current_app, render_template

from info.modules.home import home_blu



# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    # 返回跟路由页面
    return render_template("index.html")


# 网站小图标设置favicon.ico
@home_blu.route("/favicon.ico")
def favicon():
    # favicon.ico返回
    return current_app.send_static_file("news/favicon.ico")