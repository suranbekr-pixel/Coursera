from fastapi import FastAPI
import uvicorn

from mysite.database.db import engine, Base
from mysite.api.auth import auth_router
from mysite.api.user import user_router
from mysite.api.category import category_router
from mysite.api.course import course_router
from mysite.api.study_group import study_group_router
from mysite.api.application import application_router
from mysite.api.enrollment import enrollment_router
from mysite.chains.ai_search import search_router
from mysite.admin.setup import setup_admin

# 1. Автоматическое создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)

openapi_tags = [
    {'name': 'User'},
    {'name': 'Application'},
    {'name': 'Enrollment'},
    {'name': 'StudyGroup'},
    {'name': 'Category'},
    {'name': 'Course'},
]

# 2. Инициализация FastAPI приложения
app = FastAPI(
    title='Courser Project6-7',
    version='0.1.0',
    openapi_tags=openapi_tags
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 3. Подключение роутеров
# 3.1 Точный порядок и префиксы как на видео преподавателя (Swagger UI)
app.include_router(user_router, prefix='/user')
app.include_router(application_router, prefix='/application')
app.include_router(enrollment_router, prefix='/enrollment')
app.include_router(study_group_router, prefix='/study_group')
app.include_router(category_router, prefix='/category')
app.include_router(course_router, prefix='/course')

# 3.2 Обратная совместимость и скрытые сервисы
app.include_router(user_router, prefix='/users', include_in_schema=False)
app.include_router(application_router, prefix='/applications', include_in_schema=False)
app.include_router(enrollment_router, prefix='/enrollments', include_in_schema=False)
app.include_router(study_group_router, prefix='/study-groups', include_in_schema=False)
app.include_router(study_group_router, prefix='/study_groups', include_in_schema=False)
app.include_router(category_router, prefix='/categories', include_in_schema=False)
app.include_router(course_router, prefix='/courses', include_in_schema=False)
app.include_router(auth_router, include_in_schema=False)
app.include_router(search_router, include_in_schema=False)
app.include_router(search_router, prefix='/ai', include_in_schema=False)

# 4. Подключение админ-панели SQLAdmin
setup_admin(app)


@app.get('/', include_in_schema=False)
async def root():
    return {
        'message': 'Кош келиңиз! Coursera Platform API иштеп жатат.',
        'docs': '/docs',
        'admin': '/admin',
        'ai_search': '/search/'
    }


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
