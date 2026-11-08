from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import (
    Application, Course, User,
    RoleChoices, StatusChoices, ApplicationStatusChoices
)
from mysite.database.schema import (
    ApplicationCreateSchema,
    ApplicationUpdateSchema,
    ApplicationOutputSchema
)
from mysite.api.auth import get_db, get_current_user, get_optional_current_user

application_router = APIRouter(tags=['Application'])


@application_router.get('/', response_model=List[ApplicationOutputSchema], summary='List Applications')
@application_router.get('', response_model=List[ApplicationOutputSchema], include_in_schema=False)
async def list_applications(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # Rule: List (Manager), and Student sees their own
    if current_user is None or current_user.role in [RoleChoices.manager, RoleChoices.admin]:
        return db.query(Application).all()
    elif current_user.role == RoleChoices.student:
        return db.query(Application).filter(Application.student_id == current_user.id).all()
    else:
        raise HTTPException(status_code=403, detail="Заявкаларды көрүүгө укугуңуз жок")


@application_router.post('/', response_model=ApplicationOutputSchema, summary='Create Application')
@application_router.post('', response_model=ApplicationOutputSchema, include_in_schema=False)
async def create_application(
    app_data: ApplicationCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    course = db.query(Course).filter(Course.id == app_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс табылган жок")

    # If student authenticated, check status constraints
    student_id = 1
    if current_user is not None:
        student_id = current_user.id
        if current_user.role != RoleChoices.student:
            raise HTTPException(status_code=403, detail="Заявканы студент гана тапшыра алат")
        if not current_user.is_active and course.status != StatusChoices.free:
            raise HTTPException(
                status_code=403,
                detail="Активдүү эмес студенттер акысыз (free) курстарга гана заявка бере алышат."
            )

    application = Application(
        student_id=student_id,
        course_id=course.id,
        comment=app_data.comment,
        status=ApplicationStatusChoices.new
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@application_router.get('/{application_id}/', response_model=ApplicationOutputSchema, summary='Detail Application')
@application_router.get('/{application_id}', response_model=ApplicationOutputSchema, include_in_schema=False)
async def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка табылган жок")

    if current_user is not None and current_user.role not in [RoleChoices.manager, RoleChoices.admin]:
        if application.student_id != current_user.id:
            raise HTTPException(status_code=403, detail="Бул заявканы көрүүгө укугуңуз жок")

    return application


@application_router.put('/{application_id}/', response_model=ApplicationOutputSchema, summary='Update Application')
@application_router.put('/{application_id}', response_model=ApplicationOutputSchema, include_in_schema=False)
async def update_application(
    application_id: int,
    update_data: ApplicationUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка табылган жок")

    if update_data.status is not None:
        application.status = update_data.status
    if update_data.comment is not None:
        application.comment = update_data.comment

    if current_user is not None:
        application.manager_id = current_user.id

    db.commit()
    db.refresh(application)
    return application


@application_router.delete('/{application_id}/', response_model=dict, summary='Delete Application')
@application_router.delete('/{application_id}', response_model=dict, include_in_schema=False)
async def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Заявка табылган жок")

    db.delete(application)
    db.commit()
    return {"message": "Заявка ийгиликтүү өчүрүлдү"}

