
## PostgreSQL

在 Ubuntu 20.04 上安装 PostgreSQL 数据库的步骤如下：

1 安装 PostgreSQL

```shell
apt update
apt install postgresql postgresql-contrib
```

2 启动 PostgreSQL 服务

```shell
systemctl start postgresql
systemctl enable postgresql
systemctl status postgresql
```

3 设置 PostgreSQL 用户

默认情况下，PostgreSQL 创建一个名为 postgres 的用户。你可以切换到这个用户并进入 PostgreSQL 提供的命令行界面：

```shell
sudo -i -u postgres
psql
```

4 创建数据库和用户

在 PostgreSQL 提示符下，你可以创建新的数据库和用户。例如，创建一个名为 inference 的数据库和一个名为 schinper 的用户：

```shell
CREATE DATABASE inference;
CREATE USER schinper WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE inference TO schinper;
\l
```

5 退出 PostgreSQL

```shell
\q
```

6 配置远程访问（可选）

如果你希望允许远程访问 PostgreSQL，需要编辑配置文件。打开 postgresql.conf，找到并修改以下行：

```
listen_addresses = '*'
```

然后，编辑 pg_hba.conf 文件以允许远程连接，在文件末尾添加以下行：

```
host    all             all             0.0.0.0/0               md5
```

## Alembic

1 安装 Alembic

```shell
pip install alembic==1.12.0
```

2 初始化 Alembic

```shell
cd /path/to/inference-server/inference
alembic init alembic
```

3 配置 Alembic

将 `alembic` 文件夹移到 `./database` 目录下，并修改 `alembic.ini` 文件。
 
```diff
diff --git a/inference/alembic.ini b/inference/alembic.ini
index 1e8c258..3332c07 100644
--- a/inference/alembic.ini
+++ b/inference/alembic.ini
@@ -2,13 +2,13 @@
 
 [alembic]
 # path to migration scripts
-script_location = alembic
+script_location = inference:database/alembic
 
 # template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
 # Uncomment the line below if you want the files to be prepended with date and time
 # see https://alembic.sqlalchemy.org/en/latest/tutorial.html#editing-the-ini-file
 # for all available tokens
-# file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
+file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s
 
 # sys.path path, will be prepended to sys.path if present.
 # defaults to the current working directory.
@@ -60,7 +60,7 @@ version_path_separator = os  # Use os.pathsep. Default configuration used for ne
 # are written from script.py.mako
 # output_encoding = utf-8
 
-sqlalchemy.url = driver://user:pass@localhost/dbname
+# sqlalchemy.url = driver://user:pass@localhost/dbname
 
 
 [post_write_hooks]
```

4 修改 env.py

```diff
diff --git a/inference/database/alembic/env.py b/inference/database/alembic/env.py
index 36112a3..4e3b605 100644
--- a/inference/database/alembic/env.py
+++ b/inference/database/alembic/env.py
@@ -1,9 +1,9 @@
-from logging.config import fileConfig
-
-from sqlalchemy import engine_from_config
-from sqlalchemy import pool
-
 from alembic import context
+from sqlalchemy import engine_from_config, pool
+
+from inference.config import SQLALCHEMY_DATABASE_URI
+from inference.database.core import Base
+from inference.logging import logging
 
 # this is the Alembic Config object, which provides
 # access to the values within the .ini file in use.
@@ -11,43 +11,23 @@ config = context.config
 
 # Interpret the config file for Python logging.
 # This line sets up loggers basically.
-if config.config_file_name is not None:
-    fileConfig(config.config_file_name)
+log = logging.getLogger(__name__)
 
 # add your model's MetaData object here
 # for 'autogenerate' support
 # from myapp import mymodel
 # target_metadata = mymodel.Base.metadata
-target_metadata = None
+target_metadata = Base.metadata
 
 # other values from the config, defined by the needs of env.py,
 # can be acquired:
 # my_important_option = config.get_main_option("my_important_option")
 # ... etc.
+config.set_main_option("sqlalchemy.url", str(SQLALCHEMY_DATABASE_URI))
 
 
-def run_migrations_offline() -> None:
-    """Run migrations in 'offline' mode.
-
-    This configures the context with just a URL
-    and not an Engine, though an Engine is acceptable
-    here as well.  By skipping the Engine creation
-    we don't even need a DBAPI to be available.
-
-    Calls to context.execute() here emit the given string to the
-    script output.
-
-    """
-    url = config.get_main_option("sqlalchemy.url")
-    context.configure(
-        url=url,
-        target_metadata=target_metadata,
-        literal_binds=True,
-        dialect_opts={"paramstyle": "named"},
-    )
-
-    with context.begin_transaction():
-        context.run_migrations()
+def include_object(object, name, type_, reflected, compare_to):
+    return True
 
 
 def run_migrations_online() -> None:
@@ -57,15 +37,28 @@ def run_migrations_online() -> None:
     and associate a connection with the context.
 
     """
+
+    # don't create empty revisions
+    def process_revision_directives(context, revision, directives):
+        script = directives[0]
+        if script.upgrade_ops.is_empty():
+            directives[:] = []
+            log.info("No changes found skipping revision creation.")
+
     connectable = engine_from_config(
         config.get_section(config.config_ini_section, {}),
         prefix="sqlalchemy.",
         poolclass=pool.NullPool,
     )
 
+    log.info("Migrating inference schema...")
     with connectable.connect() as connection:
         context.configure(
-            connection=connection, target_metadata=target_metadata
+            connection=connection,
+            target_metadata=target_metadata,
+            include_schemas=True,
+            include_object=include_object,
+            process_revision_directives=process_revision_directives,
         )
 
         with context.begin_transaction():
@@ -73,6 +66,6 @@ def run_migrations_online() -> None:
 
 
 if context.is_offline_mode():
-    run_migrations_offline()
+    log.info("Can't run migrations offline")
 else:
     run_migrations_online()
```

5 创建迁移

```shell
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

这将生成一个新的迁移文件，位于 versions 目录中。Alembic 会自动检测模型的更改，并生成相应的迁移代码。

6 查看和修改迁移

生成的迁移文件可能需要手动调整。打开 versions 目录中的迁移文件，检查生成的代码是否符合你的预期。

7 应用迁移

```shell
alembic upgrade head
```

8 回滚迁移

```shell
alembic downgrade -1
```

这将回滚到上一个版本。你也可以指定特定的版本号进行回滚。

9 其他命令

查看当前版本

```shell
alembic current
```

列出所有版本

```shell
alembic history
```

生成空的迁移

```shell
alembic revision -m "描述信息"
```
