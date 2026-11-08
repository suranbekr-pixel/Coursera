from fastapi import FastAPI
from sqladmin import Admin
from mysite.database.db import engine
from .views import (
    UserAdmin,
    CategoryAdmin,
    CourseAdmin,
    StudyGroupAdmin,
    ApplicationAdmin,
    EnrollmentAdmin
)


def setup_admin(app: FastAPI):
    admin = Admin(app, engine, title="Coursera Admin Panel")
    admin.add_view(UserAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(StudyGroupAdmin)
    admin.add_view(ApplicationAdmin)
    admin.add_view(EnrollmentAdmin)
