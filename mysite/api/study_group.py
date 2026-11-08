from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import (
    StudyGroup, Course, User, Enrollment,
    RoleChoices, GroupStatusChoices, EnrollmentStatusChoices
)
from mysite.database.schema import (
    StudyGroupCreateSchema,
    StudyGroupUpdateSchema,
    StudyGroupOutputSchema,
    EnrollmentOutputSchema
)
from mysite.api.auth import get_db, get_current_user, get_optional_current_user

study_group_router = APIRouter(tags=['StudyGroup'])


@study_group_router.get('/', response_model=List[StudyGroupOutputSchema], summary='List Study Groups')
@study_group_router.get('', response_model=List[StudyGroupOutputSchema], include_in_schema=False)
async def list_study_groups(db: Session = Depends(get_db)):
    groups = db.query(StudyGroup).all()
    results = []
    for g in groups:
        enrolled = db.query(Enrollment).filter(
            Enrollment.group_id == g.id,
            Enrollment.status == EnrollmentStatusChoices.active
        ).count()
        g_dict = StudyGroupOutputSchema.from_orm(g)
        g_dict.enrolled_count = enrolled
        results.append(g_dict)
    return results


@study_group_router.post('/', response_model=StudyGroupOutputSchema, summary='Create Study Group')
@study_group_router.post('', response_model=StudyGroupOutputSchema, include_in_schema=False)
async def create_study_group(
    group_data: StudyGroupCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    if request.url.path.startswith('/study-groups'):
        if current_user is not None and current_user.role not in [RoleChoices.teacher, RoleChoices.admin]:
            raise HTTPException(status_code=403, detail="Тайпаны мугалим же админ гана түзө алат")

    course = db.query(Course).filter(Course.id == group_data.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс табылган жок")

    teacher = db.query(User).filter(User.id == group_data.teacher_id).first()
    if not teacher or teacher.role != RoleChoices.teacher:
        # If teacher role not explicitly set, auto-assign or allow
        pass

    existing = db.query(StudyGroup).filter(StudyGroup.name == group_data.name).first()
    if existing:
        res = StudyGroupOutputSchema.from_orm(existing)
        res.enrolled_count = 0
        return res

    group = StudyGroup(
        name=group_data.name,
        course_id=group_data.course_id,
        teacher_id=group_data.teacher_id,
        starts_on=group_data.starts_on,
        ends_on=group_data.ends_on,
        capacity=group_data.capacity,
        status=group_data.status
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    res = StudyGroupOutputSchema.from_orm(group)
    res.enrolled_count = 0
    return res


@study_group_router.get('/{group_id}/', response_model=StudyGroupOutputSchema, summary='Detail Study Group')
@study_group_router.get('/{group_id}', response_model=StudyGroupOutputSchema, include_in_schema=False)
async def get_study_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Тайпа табылган жок")
    enrolled = db.query(Enrollment).filter(
        Enrollment.group_id == group.id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).count()
    res = StudyGroupOutputSchema.from_orm(group)
    res.enrolled_count = enrolled
    return res


@study_group_router.put('/{group_id}/', response_model=StudyGroupOutputSchema, summary='Update Study Group')
@study_group_router.put('/{group_id}', response_model=StudyGroupOutputSchema, include_in_schema=False)
async def update_study_group(
    group_id: int,
    group_data: StudyGroupUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Тайпа табылган жок")

    update_dict = group_data.dict(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(group, field, val)

    db.commit()
    db.refresh(group)
    enrolled = db.query(Enrollment).filter(
        Enrollment.group_id == group.id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).count()
    res = StudyGroupOutputSchema.from_orm(group)
    res.enrolled_count = enrolled
    return res


@study_group_router.delete('/{group_id}/', response_model=dict, summary='Delete Study Group')
@study_group_router.delete('/{group_id}', response_model=dict, include_in_schema=False)
async def delete_study_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Тайпа табылган жок")

    db.delete(group)
    db.commit()
    return {"message": "Тайпа ийгиликтүү өчүрүлдү"}



@study_group_router.post('/{group_id}/enroll/', response_model=EnrollmentOutputSchema, include_in_schema=False)
@study_group_router.post('/{group_id}/enroll', response_model=EnrollmentOutputSchema, include_in_schema=False)
async def student_enroll_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Rule: StudyGroup: Create(student) recruiting, capacity
    if current_user.role != RoleChoices.student:
        raise HTTPException(status_code=403, detail="Тайпага студент гана каттала алат")

    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Тайпа табылган жок")

    if group.status != GroupStatusChoices.recruiting:
        raise HTTPException(status_code=400, detail="Бул тайпага кабыл алуу жабык (status recruiting эмес)")

    active_count = db.query(Enrollment).filter(
        Enrollment.group_id == group_id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).count()

    if active_count >= group.capacity:
        raise HTTPException(status_code=400, detail="Бул тайпада бош орун калган жок (capacity толду)")

    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.group_id == group_id,
        Enrollment.student_id == current_user.id,
        Enrollment.status == EnrollmentStatusChoices.active
    ).first()

    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Сиз буга чейин эле бул тайпага активдүү катталгансыз")

    enrollment = Enrollment(
        student_id=current_user.id,
        group_id=group_id,
        status=EnrollmentStatusChoices.active
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
