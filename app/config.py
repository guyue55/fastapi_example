# -*- coding: utf-8 -*-
import logging
from urllib import parse

from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)

# database
DATABASE_HOSTNAME = config("DATABASE_HOSTNAME", default="127.0.0.1")
# TODO DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret,default="root:root1234", is_secret=True)
DATABASE_CREDENTIALS = config("DATABASE_CREDENTIALS", cast=Secret, default="root:root1234")
# this will support special chars for credentials
_DATABASE_CREDENTIAL_USER, _DATABASE_CREDENTIAL_PASSWORD = str(DATABASE_CREDENTIALS).split(":")
_QUOTED_DATABASE_PASSWORD = parse.quote(str(_DATABASE_CREDENTIAL_PASSWORD))
DATABASE_NAME = config("DATABASE_NAME", default="inference")
DATABASE_PORT = config("DATABASE_PORT", default="5432")
DATABASE_ENGINE_POOL_SIZE = config("DATABASE_ENGINE_POOL_SIZE", cast=int, default=500)
DATABASE_ENGINE_MAX_OVERFLOW = config("DATABASE_ENGINE_MAX_OVERFLOW", cast=int, default=0)
# Deal with DB disconnects
# https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
DATABASE_ENGINE_POOL_PING = config("DATABASE_ENGINE_POOL_PING", default=False)
DATABASE_ENGINE_POOL_RECYCLE = config("DATABASE_ENGINE_POOL_RECYCLE", cast=int, default=3600)
SQLALCHEMY_DATABASE_URI = (f"postgresql+psycopg2://{_DATABASE_CREDENTIAL_USER}:{_QUOTED_DATABASE_PASSWORD}@"
                           f"{DATABASE_HOSTNAME}:{DATABASE_PORT}/{DATABASE_NAME}")
