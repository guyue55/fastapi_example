# -*- coding: utf-8 -*-
from enum import StrEnum


class ProjectEnum(StrEnum):
    """
    A custom Enum class that extends StrEnum.

    This class inherits all functionality from StrEnum, including
    string representation and automatic value conversion to strings.

    Example:
        class Visibility(ProjectEnum):
            OPEN = "Open"
            RESTRICTED = "Restricted"

        assert str(Visibility.OPEN) == "Open"

    Note:
        In `3.12` we will get `__contains__` functionality:

        DeprecationWarning: in 3.12 __contains__ will no longer raise TypeError, but will return True or
        False depending on whether the value is a member or the value of a member
    """

    pass  # No additional implementation needed
