from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager

from info import create_app



# 创建应用
app = create_app("dev")
# 创建管理器
mgr = Manager(app)
# 添加迁移命令
mgr.add_command("mc", MigrateCommand)



if __name__ == '__main__':
    mgr.run()
