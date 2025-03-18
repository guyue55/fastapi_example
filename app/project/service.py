# -*- coding: utf-8 -*-
from typing import Optional

from sqlalchemy.orm import Session

from .models import Project, ProjectCreate


def get_by_name(*, db_session: Session, name: str) -> Optional[Project]:
    """Returns a project based on the given project name."""
    return db_session.query(Project).filter(Project.name == name).one_or_none()


def get(*, db_session: Session, project_id: int) -> Optional[Project]:
    """Gets a notifcation by id."""
    return db_session.query(Project).filter(Project.id == project_id).one_or_none()


def create(*, db_session: Session, project_in: ProjectCreate) -> Project:
    """Creates a project."""
    project = Project(**project_in.dict())

    db_session.add(project)
    db_session.commit()
    return project
