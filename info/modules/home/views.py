from info.modules.home import home_blu



# 视图函数
@home_blu.route("/")
def index():
    return "index page"