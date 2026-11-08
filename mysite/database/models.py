from .db import Base
from sqlalchemy import String, Integer, Date, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime
from typing import Optional, List
from enum import Enum as PyEnum


class RoleChoices(str, PyEnum):
    student = "student"
    teacher = "teacher"
    manager = "manager"
    admin = "admin"


class UserStatusChoices(str, PyEnum):
    free = "free"
    pro = "pro"


class LevelChoices(str, PyEnum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class StatusChoices(str, PyEnum):
    free = "free"
    plus = "plus"


class GroupStatusChoices(str, PyEnum):
    recruiting = "recruiting"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class ApplicationStatusChoices(str, PyEnum):
    new = "new"
    in_progress = "in_progress"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class EnrollmentStatusChoices(str, PyEnum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[RoleChoices] = mapped_column(Enum(RoleChoices), default=RoleChoices.student)
    user_status: Mapped[UserStatusChoices] = mapped_column(Enum(UserStatusChoices), default=UserStatusChoices.free)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    teacher_groups: Mapped[List['StudyGroup']] = relationship('StudyGroup', back_populates='teacher', cascade='all, delete-orphan')
    student_applications: Mapped[List['Application']] = relationship('Application', back_populates='student', foreign_keys='Application.student_id', cascade='all, delete-orphan')
    student_enrollments: Mapped[List['Enrollment']] = relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    user_tokens: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='token_user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    token: Mapped[str] = mapped_column(String, index=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    token_user: Mapped['User'] = relationship('User', back_populates='user_tokens')


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True)

    category_courses: Mapped[List['Course']] = relationship('Course', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Category {self.category_name}>"


class Course(Base):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[LevelChoices] = mapped_column(Enum(LevelChoices), default=LevelChoices.beginner)
    price: Mapped[int] = mapped_column(Integer, default=0)
    duration_weeks: Mapped[int] = mapped_column(Integer, default=4)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[StatusChoices] = mapped_column(Enum(StatusChoices), default=StatusChoices.free)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped['Category'] = relationship('Category', back_populates='category_courses')
    course_groups: Mapped[List['StudyGroup']] = relationship('StudyGroup', back_populates='course', cascade='all, delete-orphan')
    course_applications: Mapped[List['Application']] = relationship('Application', back_populates='course', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Course {self.title}>"


class StudyGroup(Base):
    __tablename__ = 'study_group'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    capacity: Mapped[int] = mapped_column(Integer, default=20)
    status: Mapped[GroupStatusChoices] = mapped_column(Enum(GroupStatusChoices), default=GroupStatusChoices.recruiting)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course: Mapped['Course'] = relationship('Course', back_populates='course_groups')
    teacher: Mapped['User'] = relationship('User', back_populates='teacher_groups')
    group_enrollments: Mapped[List['Enrollment']] = relationship('Enrollment', back_populates='group', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<StudyGroup {self.name}>"


class Application(Base):
    __tablename__ = 'application'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatusChoices] = mapped_column(Enum(ApplicationStatusChoices), default=ApplicationStatusChoices.new)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped['User'] = relationship('User', foreign_keys=[student_id], back_populates='student_applications')
    course: Mapped['Course'] = relationship('Course', back_populates='course_applications')
    manager: Mapped[Optional['User']] = relationship('User', foreign_keys=[manager_id])

    def __repr__(self):
        return f"<Application {self.id} (student={self.student_id}, course={self.course_id})>"


class Enrollment(Base):
    __tablename__ = 'enrollment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    group_id: Mapped[int] = mapped_column(ForeignKey('study_group.id'))
    status: Mapped[EnrollmentStatusChoices] = mapped_column(Enum(EnrollmentStatusChoices), default=EnrollmentStatusChoices.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped['User'] = relationship('User', back_populates='student_enrollments')
    group: Mapped['StudyGroup'] = relationship('StudyGroup', back_populates='group_enrollments')

    def __repr__(self):
        return f"<Enrollment {self.id} (student={self.student_id}, group={self.group_id})>"
