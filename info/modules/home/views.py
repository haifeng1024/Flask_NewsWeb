from flask import current_app, render_template, jsonify
from flask import session

from info.models import User
from info.modules.home import home_blu
from info.utils.response_code import RET, error_map

# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    # 判断用户是否登陆
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 用户数据模型
    user = user.to_dict() if user else None
    # 返回跟路由页面
    return render_template("index.html", user=user)


# 网站小图标设置favicon.ico
@home_blu.route("/favicon.ico")
def favicon():
    # favicon.ico返回
    return current_app.send_static_file("news/favicon.ico")