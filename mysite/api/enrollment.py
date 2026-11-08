from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import (
    Enrollment, StudyGroup, User,
    RoleChoices, GroupStatusChoices, EnrollmentStatusChoices
)
from mysite.database.schema import (
    EnrollmentCreateSchema,
    EnrollmentUpdateSchema,
    EnrollmentOutputSchema
)
from mysite.api.auth import get_db, get_current_user, get_optional_current_user

enrollment_router = APIRouter(tags=['Enrollment'])


@enrollment_router.get('/', response_model=List[EnrollmentOutputSchema], summary='List Enrollments')
@enrollment_router.get('', response_model=List[EnrollmentOutputSchema], include_in_schema=False)
async def list_enrollments(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # Rule: Enrollment: Student (get_queryset)
    if current_user is None or current_user.role in [RoleChoices.manager, RoleChoices.admin, RoleChoices.teacher]:
        return db.query(Enrollment).all()
    elif current_user.role == RoleChoices.student:
        return db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    else:
        raise HTTPException(status_code=403, detail="Бул маалыматты көрүүгө укугуңуз жок")


@enrollment_router.post('/', response_model=EnrollmentOutputSchema, summary='Create Enrollment')
@enrollment_router.post('', response_model=EnrollmentOutputSchema, include_in_schema=False)
async def create_enrollment(
    data: EnrollmentCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    target_student_id = 1
    if current_user is not None:
        target_student_id = current_user.id
        if current_user.role in [RoleChoices.manager, RoleChoices.admin] and data.student_id:
            target_student_id = data.student_id

    group = db.query(StudyGroup).filter(StudyGroup.id == data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Тайпа табылган жок")

    if group.status != GroupStatusChoices.recruiting:
        raise HTTPException(status_code=400, detail="Бул тайпага кабыл алуу жабык")

    active_count = db.query(Enrollment).filter(
        Enrollment.group_id == data.group_id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).count()

    if active_count >= group.capacity:
        raise HTTPException(status_code=400, detail="Бул тайпада бош орун калган жок (capacity толду)")

    existing = db.query(Enrollment).filter(
        Enrollment.group_id == data.group_id,
        Enrollment.student_id == target_student_id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).first()

    if existing:
        return existing

    enrollment = Enrollment(
        student_id=target_student_id,
        group_id=data.group_id,
        status=EnrollmentStatusChoices.active
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@enrollment_router.get('/{enrollment_id}/', response_model=EnrollmentOutputSchema, summary='Detail Enrollment')
@enrollment_router.get('/{enrollment_id}', response_model=EnrollmentOutputSchema, include_in_schema=False)
async def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Каттоо табылган жок")

    if current_user is not None and current_user.role == RoleChoices.student and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Бул каттоону көрүүгө укугуңуз жок")

    return enrollment


@enrollment_router.put('/{enrollment_id}/', response_model=EnrollmentOutputSchema, summary='Update Enrollment')
@enrollment_router.put('/{enrollment_id}', response_model=EnrollmentOutputSchema, include_in_schema=False)
async def update_enrollment(
    enrollment_id: int,
    data: EnrollmentUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Каттоо табылган жок")

    if data.status is not None:
        enrollment.status = data.status

    db.commit()
    db.refresh(enrollment)
    return enrollment


@enrollment_router.delete('/{enrollment_id}/', response_model=dict, summary='Delete Enrollment')
@enrollment_router.delete('/{enrollment_id}', response_model=dict, include_in_schema=False)
async def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Каттоо табылган жок")

    db.delete(enrollment)
    db.commit()
    return {"message": "Каттоо ийгиликтүү өчүрүлдү"}

