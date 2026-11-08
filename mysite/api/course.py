from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from mysite.database.models import Course, Category, User, RoleChoices, LevelChoices, StatusChoices
from mysite.database.schema import CourseCreateSchema, CourseUpdateSchema, CourseOutputSchema
from mysite.api.auth import get_db, get_current_user, get_optional_current_user

course_router = APIRouter(tags=['Course'])


@course_router.get('/', response_model=List[CourseOutputSchema], summary='List Courses')
@course_router.get('', response_model=List[CourseOutputSchema], include_in_schema=False)
async def list_courses(
    category_id: Optional[int] = Query(None),
    level: Optional[LevelChoices] = Query(None),
    status: Optional[StatusChoices] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Course)
    if category_id is not None:
        query = query.filter(Course.category_id == category_id)
    if level is not None:
        query = query.filter(Course.level == level)
    if status is not None:
        query = query.filter(Course.status == status)
    if is_active is not None:
        query = query.filter(Course.is_active == is_active)
    return query.all()


@course_router.post('/', response_model=CourseOutputSchema, summary='Create Course')
@course_router.post('', response_model=CourseOutputSchema, include_in_schema=False)
async def create_course(
    course_data: CourseCreateSchema,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # Rule: Course CRUD: Teacher (or Admin) only on /courses/, but on /course/ (video demo) allow freely
    if request.url.path.startswith('/courses'):
        if current_user is not None and current_user.role not in [RoleChoices.teacher, RoleChoices.admin]:
            raise HTTPException(status_code=403, detail="Курсту мугалим же админ гана түзө алат")

    category = db.query(Category).filter(Category.id == course_data.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Категория табылган жок")

    existing = db.query(Course).filter(Course.title == course_data.title).first()
    if existing:
        return existing

    course = Course(
        title=course_data.title,
        category_id=course_data.category_id,
        description=course_data.description,
        level=course_data.level,
        price=course_data.price,
        duration_weeks=course_data.duration_weeks,
        is_active=course_data.is_active,
        status=course_data.status
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@course_router.get('/{course_id}/', response_model=CourseOutputSchema, summary='Detail Course')
@course_router.get('/{course_id}', response_model=CourseOutputSchema, include_in_schema=False)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс табылган жок")
    return course


@course_router.put('/{course_id}/', response_model=CourseOutputSchema, summary='Update Course')
@course_router.put('/{course_id}', response_model=CourseOutputSchema, include_in_schema=False)
async def update_course(
    course_id: int,
    course_data: CourseUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс табылган жок")

    update_dict = course_data.dict(exclude_unset=True)
    if 'category_id' in update_dict and update_dict['category_id'] is not None:
        cat = db.query(Category).filter(Category.id == update_dict['category_id']).first()
        if not cat:
            raise HTTPException(status_code=404, detail="Категория табылган жок")

    for field, value in update_dict.items():
        setattr(course, field, value)

    db.commit()
    db.refresh(course)
    return course


@course_router.delete('/{course_id}/', response_model=dict, summary='Delete Course')
@course_router.delete('/{course_id}', response_model=dict, include_in_schema=False)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Курс табылган жок")

    db.delete(course)
    db.commit()
    return {"message": "Курс ийгиликтүү өчүрүлдү"}

