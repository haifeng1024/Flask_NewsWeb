from flask import Blueprint

# 创建蓝图
pass_blu = Blueprint("passport", __name__, url_prefix="/passport")


# 关联视图函数
from .views import *