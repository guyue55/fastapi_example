# -*- coding: utf-8 -*-
from pydantic.errors import PydanticValueError


class NotFoundError(PydanticValueError):
    code = "not_found"
    msg_template = "{msg}"


class ExistsError(PydanticValueError):
    code = "exists"
    msg_template = "{msg}"
