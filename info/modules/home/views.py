from info import sr
from info.modules.home import home_blu



# 视图函数
@home_blu.route("/")
def index():
    sr.set("age", 20)
    return "index page"