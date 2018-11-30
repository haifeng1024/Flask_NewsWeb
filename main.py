from flask import session
from flask_script import Manager
from flask_migrate import MigrateCommand
from info import create_app

# 创建应用
app = create_app("dev")
# 创建管理器
mgr = Manager(app)

# 添加迁移命令
mgr.add_command("mc", MigrateCommand)


@app.route('/')
def index():
    session["name"] = "zs"
    return "index"


if __name__ == '__main__':
    mgr.run()