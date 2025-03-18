# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from ..database.core import DbSession
from ..exceptions import ExistsError
from ..models import PrimaryKey

from .models import (
    ProjectCreate,
    ProjectRead,
)
from .service import create, get, get_by_name


router = APIRouter()


@router.post(
    "",
    response_model=ProjectRead,
    summary="Create a new project.",
)
def create_project(db_session: DbSession, project_in: ProjectCreate):
    """Create a new project."""
    project = get_by_name(db_session=db_session, name=project_in.name)
    if project:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="A project with this name already exists."), loc="name")],
            model=ProjectCreate,
        )

    project = create(db_session=db_session, project_in=project_in)
    return project


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get a project.",
)
def get_project(db_session: DbSession, project_id: PrimaryKey):
    """Get a project by its id."""
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A project with this id does not exist."}],
        )
    return project
