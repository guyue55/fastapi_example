# -*- coding: utf-8 -*-
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String

from ..database.core import Base
from ..models import InferenceBase, NameStr, PrimaryKey, TimeStampMixin


class Project(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)


class ProjectBase(DataBase):
    id: Optional[PrimaryKey]
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    pass
