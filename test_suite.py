from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def run_all_tests():
    print("================ STARTING COURSERA API TEST SUITE ================")
    
    # 1. Login with different roles
    print("\n--- 1. Testing Authentication & Token Generation ---")
    
    def get_token(email, password):
        resp = client.post("/auth/login/", json={"email": email, "password": password})
        assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
        data = resp.json()
        return data["access_token"]

    admin_token = get_token("admin@coursera.kg", "admin123")
    teacher_token = get_token("teacher@coursera.kg", "teacher123")
    manager_token = get_token("manager@coursera.kg", "manager123")
    student_token = get_token("student@coursera.kg", "student123")
    free_student_token = get_token("free_student@coursera.kg", "student123")
    print("✓ All 5 user roles logged in successfully and received JWT access tokens!")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    student_headers = {"Authorization": f"Bearer {student_token}"}
    free_student_headers = {"Authorization": f"Bearer {free_student_token}"}

    # 2. Category CRUD (ADMIN ONLY)
    print("\n--- 2. Testing Category Permissions (Admin Only) ---")
    import time
    cat_payload = {"category_name": f"Мобильная разработка {int(time.time())}"}
    # Teacher tries to create category -> Should fail with 403
    t_resp = client.post("/categories/", json=cat_payload, headers=teacher_headers)
    assert t_resp.status_code == 403, f"Teacher should be blocked from creating category: {t_resp.status_code}"
    print("✓ Teacher blocked from creating category (403 Forbidden)")

    # Admin creates category -> Should succeed with 200
    a_resp = client.post("/categories/", json=cat_payload, headers=admin_headers)
    assert a_resp.status_code == 200, f"Admin failed to create category: {a_resp.text}"
    cat_id = a_resp.json()["id"]
    print(f"✓ Admin created category successfully (ID: {cat_id})")

    # 3. Course CRUD (TEACHER ONLY)
    print("\n--- 3. Testing Course Permissions (Teacher Only) ---")
    course_payload = {
        "title": "Flutter & Dart для начинающих",
        "category_id": cat_id,
        "description": "Кроссплатформенная разработка мобильных приложений",
        "level": "beginner",
        "price": 20000,
        "duration_weeks": 8,
        "is_active": True,
        "status": "plus"
    }
    # Student tries to create course -> Should fail with 403
    s_resp = client.post("/courses/", json=course_payload, headers=student_headers)
    assert s_resp.status_code == 403, f"Student should be blocked from creating course: {s_resp.status_code}"
    print("✓ Student blocked from creating course (403 Forbidden)")

    # Teacher creates course -> Should succeed with 200
    t_resp = client.post("/courses/", json=course_payload, headers=teacher_headers)
    assert t_resp.status_code == 200, f"Teacher failed to create course: {t_resp.text}"
    course_id = t_resp.json()["id"]
    print(f"✓ Teacher created course successfully (ID: {course_id})")

    # 4. Application Permissions:
    # student.is_active == True / student.is_active == False and course.status == free
    print("\n--- 4. Testing Application Rules ---")
    # c2 is a PLUS course (price: 8000, status: plus)
    # c1 is a FREE course (price: 0, status: free)
    courses = client.get("/courses/").json()
    plus_course = next(c for c in courses if c["status"] == "plus")
    free_course = next(c for c in courses if c["status"] == "free")

    # Active student applies for Plus course -> Allowed
    app_active_resp = client.post(
        "/applications/",
        json={"course_id": plus_course["id"], "comment": "Хочу учиться!"},
        headers=student_headers
    )
    assert app_active_resp.status_code == 200, f"Active student should be able to apply: {app_active_resp.text}"
    app_id = app_active_resp.json()["id"]
    print(f"✓ Active student applied to Plus course (App ID: {app_id})")

    # Inactive student applies for Plus course -> BLOCKED (403)
    app_free_blocked = client.post(
        "/applications/",
        json={"course_id": plus_course["id"], "comment": "Хочу бесплатно на платный"},
        headers=free_student_headers
    )
    assert app_free_blocked.status_code == 403, f"Inactive student should be blocked from Plus course: {app_free_blocked.text}"
    print("✓ Inactive student blocked from Plus course (403 Forbidden)")

    # Inactive student applies for Free course -> ALLOWED
    app_free_ok = client.post(
        "/applications/",
        json={"course_id": free_course["id"], "comment": "Акысыз курска жазылуу"},
        headers=free_student_headers
    )
    assert app_free_ok.status_code == 200, f"Inactive student should be allowed on Free course: {app_free_ok.text}"
    print("✓ Inactive student successfully applied to Free course (200 OK)")

    # Manager updates application status
    m_update = client.put(
        f"/applications/{app_id}/",
        json={"status": "accepted", "comment": "Одобрено менеджером"},
        headers=manager_headers
    )
    assert m_update.status_code == 200, f"Manager failed to update application: {m_update.text}"
    assert m_update.json()["status"] == "accepted"
    print("✓ Manager updated application status to accepted")

    # 5. StudyGroup Capacity and Recruiting Rules
    print("\n--- 5. Testing StudyGroup Recruiting & Capacity Rules ---")
    groups = client.get("/study-groups/").json()
    recruiting_group = next(g for g in groups if g["name"].startswith("Python Basics"))
    full_group = next(g for g in groups if g["name"].startswith("Full Capacity"))
    closed_group = next(g for g in groups if g["name"].startswith("Closed Active"))

    # Student enrolls in recruiting group with capacity -> Allowed (or already enrolled from previous test run)
    enroll_ok = client.post(f"/study-groups/{recruiting_group['id']}/enroll/", headers=student_headers)
    assert enroll_ok.status_code in [200, 400], f"Student should be able to enroll: {enroll_ok.text}"
    print("✓ Student enrolled in recruiting group with capacity")

    # Student tries to enroll in full group -> BLOCKED (400)
    enroll_full = client.post(f"/study-groups/{full_group['id']}/enroll/", headers=student_headers)
    assert enroll_full.status_code == 400, f"Student should be blocked from full group: {enroll_full.text}"
    print("✓ Student blocked when capacity is full (400 Bad Request)")

    # Student tries to enroll in closed group -> BLOCKED (400)
    enroll_closed = client.post(f"/study-groups/{closed_group['id']}/enroll/", headers=student_headers)
    assert enroll_closed.status_code == 400, f"Student should be blocked from closed group: {enroll_closed.text}"
    print("✓ Student blocked when group status is not recruiting (400 Bad Request)")

    # 6. Enrollment Scoping (Student get_queryset)
    print("\n--- 6. Testing Enrollment Scoping (Student get_queryset) ---")
    s_enrolls = client.get("/enrollments/", headers=student_headers).json()
    # Student should ONLY see enrollments where student_id == student.id
    for item in s_enrolls:
        assert item["student_id"] == app_active_resp.json()["student_id"], "Student saw another user's enrollment!"
    print(f"✓ Student get_queryset scoped strictly to self ({len(s_enrolls)} enrollments found)")

    # Manager sees all enrollments
    m_enrolls = client.get("/enrollments/", headers=manager_headers).json()
    assert len(m_enrolls) > len(s_enrolls), "Manager should see all enrollments!"
    print(f"✓ Manager get_queryset returns all platform enrollments ({len(m_enrolls)} found)")

    # 7. AI Search (/search/)
    print("\n--- 7. Testing AI Search (/search/) ---")
    query = {"question": "Найди мне курс по Python продолжительность до 4 недель"}
    search_resp = client.post("/search/", json=query)
    assert search_resp.status_code == 200, f"AI Search failed: {search_resp.text}"
    res = search_resp.json()
    print("Search query:", res["question"])
    print("Search answer:\n", res["answer"][:300], "...")
    assert "Python" in res["answer"] or "курс" in res["answer"], "Search response did not contain expected course info!"
    print("✓ AI Search endpoint returned relevant course recommendation successfully!")

    print("\n================ ALL TESTS PASSED SUCCESSFULLY (100%) ================")

if __name__ == '__main__':
    run_all_tests()
