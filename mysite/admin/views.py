from sqladmin import ModelView
from mysite.database.models import User, Category, Course, StudyGroup, Application, Enrollment


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.full_name, User.email, User.role, User.user_status, User.is_active, User.created_at]
    column_searchable_list = [User.full_name, User.email]
    column_filters = [User.role, User.user_status, User.is_active]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.category_name]
    column_searchable_list = [Category.category_name]
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-list"


class CourseAdmin(ModelView, model=Course):
    column_list = [Course.id, Course.title, Course.category_id, Course.level, Course.price, Course.duration_weeks, Course.is_active, Course.status]
    column_searchable_list = [Course.title]
    column_filters = [Course.level, Course.status, Course.is_active]
    name = "Course"
    name_plural = "Courses"
    icon = "fa-solid fa-book"


class StudyGroupAdmin(ModelView, model=StudyGroup):
    column_list = [StudyGroup.id, StudyGroup.name, StudyGroup.course_id, StudyGroup.teacher_id, StudyGroup.starts_on, StudyGroup.ends_on, StudyGroup.capacity, StudyGroup.status]
    column_searchable_list = [StudyGroup.name]
    column_filters = [StudyGroup.status]
    name = "Study Group"
    name_plural = "Study Groups"
    icon = "fa-solid fa-users"


class ApplicationAdmin(ModelView, model=Application):
    column_list = [Application.id, Application.student_id, Application.course_id, Application.manager_id, Application.status, Application.created_at]
    column_filters = [Application.status]
    name = "Application"
    name_plural = "Applications"
    icon = "fa-solid fa-file-lines"


class EnrollmentAdmin(ModelView, model=Enrollment):
    column_list = [Enrollment.id, Enrollment.student_id, Enrollment.group_id, Enrollment.status, Enrollment.created_at]
    column_filters = [Enrollment.status]
    name = "Enrollment"
    name_plural = "Enrollments"
    icon = "fa-solid fa-graduation-cap"
