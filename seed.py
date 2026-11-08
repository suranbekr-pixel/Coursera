from datetime import date, datetime
from mysite.database.db import engine, SessionLocal, Base
from mysite.database.models import (
    User, Category, Course, StudyGroup, Application, Enrollment,
    RoleChoices, UserStatusChoices, LevelChoices, StatusChoices,
    GroupStatusChoices, ApplicationStatusChoices, EnrollmentStatusChoices
)
from mysite.api.auth import get_password_hash


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data for clean seeding
    db.query(Enrollment).delete()
    db.query(Application).delete()
    db.query(StudyGroup).delete()
    db.query(Course).delete()
    db.query(Category).delete()
    db.query(User).delete()
    db.commit()

    print("Seeding Users...")
    admin = User(
        full_name="Администратор Платформы",
        email="admin@coursera.kg",
        password=get_password_hash("admin123"),
        role=RoleChoices.admin,
        user_status=UserStatusChoices.pro,
        is_active=True
    )
    teacher = User(
        full_name="Марлен Агаевич",
        email="teacher@coursera.kg",
        password=get_password_hash("teacher123"),
        role=RoleChoices.teacher,
        user_status=UserStatusChoices.pro,
        is_active=True
    )
    manager = User(
        full_name="Айпери Менеджер",
        email="manager@coursera.kg",
        password=get_password_hash("manager123"),
        role=RoleChoices.manager,
        user_status=UserStatusChoices.pro,
        is_active=True
    )
    student_active = User(
        full_name="Азамат Активдүү Студент",
        email="student@coursera.kg",
        password=get_password_hash("student123"),
        role=RoleChoices.student,
        user_status=UserStatusChoices.pro,
        is_active=True
    )
    student_free = User(
        full_name="Бекзат Акысыз Студент",
        email="free_student@coursera.kg",
        password=get_password_hash("student123"),
        role=RoleChoices.student,
        user_status=UserStatusChoices.free,
        is_active=False
    )

    db.add_all([admin, teacher, manager, student_active, student_free])
    db.commit()

    print("Seeding Categories...")
    cat_prog = Category(category_name="Программирование")
    cat_db = Category(category_name="Базы данных")
    cat_ai = Category(category_name="Искусственный Интеллект")

    db.add_all([cat_prog, cat_db, cat_ai])
    db.commit()

    print("Seeding Courses...")
    c1 = Course(
        title="Основы программирования на Python",
        category_id=cat_prog.id,
        description="Базовый курс по Python для начинающих. Переменные, списки, циклы, функции. Длительность 4 недели.",
        level=LevelChoices.beginner,
        price=0,
        duration_weeks=4,
        is_active=True,
        status=StatusChoices.free
    )
    c2 = Course(
        title="Быстрый старт в Python и автоматизация",
        category_id=cat_prog.id,
        description="Курс по написанию скриптов, автоматизации рутины и парсингу веб-сайтов на Python за 3 недели.",
        level=LevelChoices.beginner,
        price=8000,
        duration_weeks=3,
        is_active=True,
        status=StatusChoices.plus
    )
    c3 = Course(
        title="Python Backend Разработчик (FastAPI)",
        category_id=cat_prog.id,
        description="Углубленный бэкенд на FastAPI, SQLAlchemy, PostgreSQL, JWT и Docker. Длительность 12 недель.",
        level=LevelChoices.intermediate,
        price=35000,
        duration_weeks=12,
        is_active=True,
        status=StatusChoices.plus
    )
    c4 = Course(
        title="Введение в реляционные базы данных и SQL",
        category_id=cat_db.id,
        description="Изучение SQL запросов, соединений таблиц JOIN, проектирования структуры баз данных.",
        level=LevelChoices.beginner,
        price=0,
        duration_weeks=4,
        is_active=True,
        status=StatusChoices.free
    )

    db.add_all([c1, c2, c3, c4])
    db.commit()

    print("Seeding Study Groups...")
    group1 = StudyGroup(
        name="Python Basics - Группа 101",
        course_id=c1.id,
        teacher_id=teacher.id,
        starts_on=date(2026, 11, 15),
        ends_on=date(2026, 12, 15),
        capacity=20,
        status=GroupStatusChoices.recruiting
    )
    group_full = StudyGroup(
        name="Full Capacity Test Group",
        course_id=c2.id,
        teacher_id=teacher.id,
        starts_on=date(2026, 11, 20),
        ends_on=date(2026, 12, 20),
        capacity=1,
        status=GroupStatusChoices.recruiting
    )
    group_closed = StudyGroup(
        name="Closed Active Study Group",
        course_id=c3.id,
        teacher_id=teacher.id,
        starts_on=date(2026, 10, 1),
        ends_on=date(2026, 12, 30),
        capacity=15,
        status=GroupStatusChoices.active
    )

    db.add_all([group1, group_full, group_closed])
    db.commit()

    # Pre-fill group_full with 1 enrollment to reach capacity
    enrollment_mock = Enrollment(
        student_id=student_free.id,
        group_id=group_full.id,
        status=EnrollmentStatusChoices.active
    )
    db.add(enrollment_mock)
    db.commit()

    db.close()
    print("Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
