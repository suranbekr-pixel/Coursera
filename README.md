# Coursera Platform Backend (FastAPI + SQLAlchemy + LangChain + SQLAdmin)

Бул долбоор Марлен агайдын сабактарындагы **1-тапшырма (ДЗ 1 FastAPI)** жана **кошумча тапшырма (ДЗ 1.1 Доп ДЗ AI Search)** боюнча толук иштелип чыккан бэкенд системасы.

---

## 🚀 Негизги функциялар жана мүмкүнчүлүктөр

### 1. Моделдер (SQLAlchemy 2.0 ORM)
- `User`: id, full_name, email, password, role (`student`, `teacher`, `manager`, `admin`), user_status (`free`, `pro`), is_active (`True`/`False`), created_at, updated_at.
- `RefreshToken`: JWT Refresh токендерин сактоо жана башкаруу.
- `Category`: Курстардын категориялары (id, category_name).
- `Course`: Курстар (id, title, category_id, description, level: `beginner`/`intermediate`/`advanced`, price, duration_weeks, is_active, status: `free`/`plus`, created_at, updated_at).
- `StudyGroup`: Окуу тайпалары (id, name, course_id, teacher_id, starts_on, ends_on, capacity, status: `recruiting`/`active`/`completed`/`cancelled`).
- `Application`: Курска кабыл алуу арыздары (id, student_id, course_id, manager_id, comment, status: `new`/`in_progress`/`accepted`/`rejected`/`cancelled`).
- `Enrollment`: Студенттин тайпага жазылуусу (id, student_id, group_id, status: `active`/`completed`/`cancelled`).

---

### 2. Бизнес логика жана Укуктар (Roles & Permissions)
1. **Category CRUD: ADMIN гана**
   - Категорияларды түзүү, өзгөртүү жана өчүрүү укугу бир гана `admin` ролундагы колдонуучуларга берилген.
2. **Course CRUD: Teacher гана**
   - Курстарды түзүү, өзгөртүү жана өчүрүү бир гана `teacher` (жана `admin`) тарабынан аткарылат.
3. **Application: Create (student)**:
   - Студент гана арыз бере алат.
   - **Эреже**:
     - `student.is_active == True`: каалаган курска (Free же Plus) арыз бере алат.
     - `student.is_active == False`: акысыз курстарга гана (`course.status == free`) арыз бере алат. Plus курска жазылууга аракет кылса, 403 Forbidden кайтарылат.
   - **Update, List, Detail, Delete**: Менеджер гана (`manager` жана `admin`). Студент өзү берген арыздарды гана көрө алат.
4. **Enrollment: Student (get_queryset)**:
   - Студент өзүнүн каттоолорун гана көрө алат (`filter(Enrollment.student_id == current_user.id)`).
   - Менеджерлер жана админдер бардык каттоолорду көрө алышат.
5. **StudyGroup: Create (student) recruiting, capacity**:
   - Тайпага студент катталуусу үчүн тайпанын статусу `recruiting` болушу керек.
   - Тайпанын бош орундарынын саны `capacity` чегинен ашпоого тийиш. Бош орун жок болсо же кабыл алуу жабык болсо, 400 Bad Request кайтарылат.
   - Мугалим жана админ тайпаларды түзүп, башкара алат.

---

### 3. AI Course Search (Доп ДЗ)
- **Endpoint**: `POST /search/`
- **Суроо форматы**:
  ```json
  {
    "question": "Найди мне курс по Python продолжительность до 4 недель"
  }
  ```
- **Технология**: LangChain + Ollama (`llama3.2` + `nomic-embed-text`) + `InMemoryVectorStore` + RAG базасы (`base_knowledge/courses.txt`).
- Суроону талдап, талап кылынган убакыт жана тил боюнча курстарды так таап берет.

---

### 4. SQLAdmin Админ-панели
- `http://127.0.0.1:8000/admin` дарегинде жеткиликтүү.
- Бардык моделдер (User, Category, Course, StudyGroup, Application, Enrollment) үчүн башкаруу интерфейси кошулган.

---

## 🛠 Долбоорду иштетүү (Кантип текшерсе болот)

1. **Серверди жүргүзүү**:
   ```powershell
   python main.py
   ```
   же
   ```powershell
   uvicorn main:app --reload --port 8000
   ```

2. **Базаны баштапкы маалыматтар менен толтуруу (Seed)**:
   ```powershell
   python seed.py
   ```

3. **Бардык тесттерди 100% автоматтык түрдө текшерүү**:
   ```powershell
   python test_suite.py
   ```

---

## 🔑 Тесттик аккаунттар (seed.py аркылуу түзүлгөн)

| Ролу | Email | Пароль | Статусу |
|---|---|---|---|
| **Admin** | admin@coursera.kg | admin123 | Pro / Active |
| **Teacher** | teacher@coursera.kg | teacher123 | Pro / Active |
| **Manager** | manager@coursera.kg | manager123 | Pro / Active |
| **Student (Active)** | student@coursera.kg | student123 | Pro / Active (бардык курстарга укуктуу) |
| **Student (Free)** | free_student@coursera.kg | student123 | Free / Inactive (акысыз курстарга гана) |

---

## 📌 Документация шилтемелери
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **SQLAdmin**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
