from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List
from datetime import date, datetime
from .models import (
    RoleChoices,
    UserStatusChoices,
    LevelChoices,
    StatusChoices,
    GroupStatusChoices,
    ApplicationStatusChoices,
    EnrollmentStatusChoices
)


# ===================== USER SCHEMAS =====================
class UserRegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: RoleChoices = RoleChoices.student
    user_status: UserStatusChoices = UserStatusChoices.free
    is_active: bool = True


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserUpdateSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleChoices] = None
    user_status: Optional[UserStatusChoices] = None
    is_active: Optional[bool] = None


class CurrentUserSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleChoices
    user_status: UserStatusChoices
    is_active: bool

    class Config:
        from_attributes = True


class UserOutputSchema(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleChoices
    user_status: UserStatusChoices
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== CATEGORY SCHEMAS =====================
class CategoryCreateSchema(BaseModel):
    category_name: str


class CategoryOutputSchema(BaseModel):
    id: int
    category_name: str

    class Config:
        from_attributes = True


# ===================== COURSE SCHEMAS =====================
class CourseCreateSchema(BaseModel):
    title: str
    category_id: int
    description: str
    level: LevelChoices = LevelChoices.beginner
    price: int = 0
    duration_weeks: int = 4
    is_active: bool = True
    status: StatusChoices = StatusChoices.free


class CourseUpdateSchema(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    level: Optional[LevelChoices] = None
    price: Optional[int] = None
    duration_weeks: Optional[int] = None
    is_active: Optional[bool] = None
    status: Optional[StatusChoices] = None


class CourseOutputSchema(BaseModel):
    id: int
    title: str
    category_id: int
    description: str
    level: LevelChoices
    price: float = 0.0
    duration_weeks: int
    is_active: bool
    status: StatusChoices
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== STUDY GROUP SCHEMAS =====================
class StudyGroupCreateSchema(BaseModel):
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: date
    capacity: int = 20
    status: GroupStatusChoices = GroupStatusChoices.recruiting


class StudyGroupUpdateSchema(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None
    teacher_id: Optional[int] = None
    starts_on: Optional[date] = None
    ends_on: Optional[date] = None
    capacity: Optional[int] = None
    status: Optional[GroupStatusChoices] = None


class StudyGroupOutputSchema(BaseModel):
    id: int
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: date
    capacity: int
    status: GroupStatusChoices
    created_at: datetime
    updated_at: datetime
    enrolled_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ===================== APPLICATION SCHEMAS =====================
class ApplicationCreateSchema(BaseModel):
    course_id: int
    comment: Optional[str] = None


class ApplicationUpdateSchema(BaseModel):
    status: Optional[ApplicationStatusChoices] = None
    comment: Optional[str] = None
    manager_id: Optional[int] = None


class ApplicationOutputSchema(BaseModel):
    id: int
    student_id: int
    course_id: int
    manager_id: Optional[int] = None
    comment: Optional[str] = None
    status: ApplicationStatusChoices
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== ENROLLMENT SCHEMAS =====================
class EnrollmentCreateSchema(BaseModel):
    group_id: int
    student_id: Optional[int] = None  # If student enrolls self, extracted from current_user


class EnrollmentUpdateSchema(BaseModel):
    status: Optional[EnrollmentStatusChoices] = None


class EnrollmentOutputSchema(BaseModel):
    id: int
    student_id: int
    group_id: int
    status: EnrollmentStatusChoices
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===================== SEARCH SCHEMAS =====================
class SearchQuerySchema(BaseModel):
    question: Optional[str] = None
    text: Optional[str] = None
    query: Optional[str] = None
    prompt: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def populate_question(cls, data):
        if isinstance(data, dict):
            q = data.get('question') or data.get('text') or data.get('query') or data.get('prompt')
            if q:
                data['question'] = q
        elif isinstance(data, str):
            data = {'question': data}
        return data


class CourseRecommendationSchema(BaseModel):
    title: str
    category: str
    level: str
    price: float = 0.0
    status: str
    reason: str


class AISearchResponseSchema(BaseModel):
    reply: str
    recommendations: List[CourseRecommendationSchema] = []
    question: Optional[str] = None
    answer: Optional[str] = None
