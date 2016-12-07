# html
How To Machine Learning in five minute

# 开发启动
安装依赖

```shell
$ virtualenv .env
$ . .env/bin/activate
$ pip install -r scripts/requirements.txt
$ python main.py
```

# 依赖说明

`tornado` web框架  
`simplejson==3.8.2` json处理  
`alembic==0.8.6` 数据库迁移脚本  
`SQLAlchemy==1.0.12` ORM  
`wtforms==2.1` 表单验证
`pytz==2016.4` 时区处理  
`nose` 单元测试 Python3.3后成为标准库  
`mock==2.0.0` 单元测试mock  
`Flask-Admin`管理页面
`Mysql-python` mysql底层连接库

## 依赖系统包
`sudo yum install Percona-Server-devel-55 Percona-Server-shared-55 ncurses-devel`

连接器选择Mysql-python
ncurses-devel 提供ipython交互环境
Percona-Server-devel-55 提供mysql_config
Percona-Server-shared-55 提供libmysql_r
选择这个连接器的原因，一是因为这是SQLAlchemy的mysql默认连接器，二是因为不依赖系统包的mysql-connector会在sql执行时携带一句
`SET NAMES 'utf8' COLLATE 'utf8_general_ci'`
但atlas不支持SET COLLATE 。。。
Mysql-python就只set names

# 迁移
## 自动检测model变更
产生一个迁移脚本
```
$ alembic -c conf/alembic.ini revision --autogenerate -m "Added xxxx table"
```
修改alembic/versions/下对应的脚本

## 升级
(要求conf/app.conf的sql_connection是可以连接的)
离线生成迁移sql，`--sql`也可以用于降级查看对应sql
```
$ alembic -c conf/alembic.ini upgrade head --sql
```

直接进行迁移

```
$ alembic -c conf/alembic.ini upgrade head
```

## 降级
```
$ alembic -c conf/alembic.ini downgrade -1
```

# 单元测试

`nosetests --processes 4 -s --with-coverage --cover-package=apps`
`--processes`并发四个单元测试 ,这个和`--pdb`以及各种pdb.set_trace()不兼容
`-s`不捕获标准输出  
`--with-coverage`检测单元测试覆盖率
`--cover-package=apps`只检测apps路径下的

要求必须继承`core.test`中的BaseTestCase基类。这样不会删掉真实数据库
一般来说core尽可能往上就好

TODO:app的单元测试失败貌似会导致tearDown没删干净，导致core或者auth的单元测试报错

# 部署
主要依靠supervisord启动

