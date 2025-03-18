# -*- coding: utf-8 -*-
import logging
from contextvars import ContextVar
from uuid import uuid1
from typing import Optional, Final

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request

from .api import api_router
from .database.core import engine, sessionmaker
from .logging import configure_logging


log = logging.getLogger(__name__)

# we configure the logging level and format
configure_logging()


async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": [{"msg": "Not Found."}]}
    )


exception_handlers = {404: not_found}

# we create the ASGI for the app
app = FastAPI(exception_handlers=exception_handlers, openapi_url="")
app.add_middleware(GZipMiddleware, minimum_size=1000)

# we create the Web API framework
api = FastAPI(
    title="Project Example",
    description="Welcome to Inference's API documentation!",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)
api.add_middleware(GZipMiddleware, minimum_size=1000)


REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


@api.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request_id = str(uuid1())

    # we create a per-request id such that we can ensure that our session is scoped for a particular request.
    # see: https://github.com/tiangolo/fastapi/issues/726
    ctx_token = _request_id_ctx_var.set(request_id)

    schema = "public"
    # validate schema exists
    schema_names = inspect(engine).get_schema_names()
    if schema in schema_names:
        # add correct schema mapping depending on the request
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: schema,
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": [{"msg": f"Unknown database schema name: {schema}"}]},
        )

    try:
        session = scoped_session(sessionmaker(bind=schema_engine), scopefunc=get_request_id)
        request.state.db = session()
        response = await call_next(request)
    except Exception as e:
        raise e from None
    finally:
        request.state.db.close()

    _request_id_ctx_var.reset(ctx_token)
    return response


# we add all API routes to the Web API framework
api.include_router(api_router)

app.mount("/api/v1", app=api)
