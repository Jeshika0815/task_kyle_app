"""Tests for /task/* — CRUD, ownership scoping, and the name->id lookup used by the bot."""


def _sample_task(plan_name: str = "Test Task", **overrides) -> dict:
    task = {
        "plan_name": plan_name,
        "date": {"start_date": "2026-08-01", "finish_date": "2026-08-01"},
        "time": {"start_time": "09:00:00", "finish_time": "10:00:00"},
        "alarm": False,
        "repeats": None,
        "tags": [],
        "location": None,
        "url": None,
        "memo": None,
    }
    task.update(overrides)
    return task


def test_add_task_returns_created_task_with_id(client, auth_headers):
    headers = auth_headers(email="taskuser@example.com", password="pw123456")

    res = client.post("/task/add", json=_sample_task(), headers=headers)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["plan_name"] == "Test Task"
    assert "id" in body


def test_add_task_requires_authentication(client):
    res = client.post("/task/add", json=_sample_task())
    assert res.status_code in (401, 403)


def test_list_tasks_returns_only_own_tasks(client, auth_headers):
    headers_a = auth_headers(email="usera@example.com", password="pw123456")
    headers_b = auth_headers(email="userb@example.com", password="pw123456")

    client.post("/task/add", json=_sample_task("A's task"), headers=headers_a)

    res = client.get("/task/", headers=headers_a)
    assert res.status_code == 200
    assert len(res.json()) == 1

    res = client.get("/task/", headers=headers_b)
    assert res.status_code == 200
    assert res.json() == []


def test_view_task(client, auth_headers):
    headers = auth_headers(email="viewuser@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers).json()

    res = client.get("/task/view_task", params={"task_id": created["id"]}, headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_view_task_not_found_returns_404(client, auth_headers):
    headers = auth_headers(email="viewmissing@example.com", password="pw123456")

    res = client.get("/task/view_task", params={"task_id": 999999}, headers=headers)
    assert res.status_code == 404


def test_view_task_of_another_user_returns_404(client, auth_headers):
    headers_a = auth_headers(email="privatea@example.com", password="pw123456")
    headers_b = auth_headers(email="privateb@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers_a).json()

    res = client.get("/task/view_task", params={"task_id": created["id"]}, headers=headers_b)
    assert res.status_code == 404


def test_update_task(client, auth_headers):
    headers = auth_headers(email="updateuser@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers).json()

    updated = dict(created)
    updated["plan_name"] = "Updated Task"
    res = client.post("/task/update", json=updated, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["plan_name"] == "Updated Task"


def test_update_task_not_owned_by_user_fails(client, auth_headers):
    headers_a = auth_headers(email="ownera@example.com", password="pw123456")
    headers_b = auth_headers(email="ownerb@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers_a).json()

    attempt = dict(created)
    attempt["plan_name"] = "Hijacked"
    res = client.post("/task/update", json=attempt, headers=headers_b)
    assert res.status_code == 404


def test_delete_task(client, auth_headers):
    headers = auth_headers(email="deleteuser@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers).json()

    res = client.request("DELETE", "/task/delete", json=created, headers=headers)
    assert res.status_code == 200

    res = client.get("/task/", headers=headers)
    assert res.json() == []


def test_delete_task_not_owned_by_user_fails(client, auth_headers):
    headers_a = auth_headers(email="deletea@example.com", password="pw123456")
    headers_b = auth_headers(email="deleteb@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task(), headers=headers_a).json()

    res = client.request("DELETE", "/task/delete", json=created, headers=headers_b)
    assert res.status_code == 404


def test_nti_resolves_plan_name_to_id(client, auth_headers):
    """The Discord bot resolves a task's id from its plan_name via /task/nti."""
    headers = auth_headers(email="ntiuser@example.com", password="pw123456")
    created = client.post("/task/add", json=_sample_task("Findable Task"), headers=headers).json()

    res = client.get("/task/nti", params={"plan_name": "Findable Task"}, headers=headers)
    assert res.status_code == 200
    assert res.json() == created["id"]


def test_nti_unknown_plan_name_returns_404(client, auth_headers):
    headers = auth_headers(email="ntimissing@example.com", password="pw123456")

    res = client.get("/task/nti", params={"plan_name": "No Such Task"}, headers=headers)
    assert res.status_code == 404
