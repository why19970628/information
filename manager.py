from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 导入models的作用是让整个应用程序知道有models的存在
from info import create_app, db, models


app = create_app('develop')

# 创建manager对象, 管理app
manager = Manager(app)

# 使用Migrate 关联app, db
Migrate(app, db)

# 给manager 添加一条操作命令
manager.add_command("db", MigrateCommand)


if __name__ == '__main__':
    manager.run()
