"""Tests for /prompt_ctl/prompt_analyze — the free-text -> task-fields parser."""


def test_prompt_analyze_extracts_fields(client, auth_headers):
    headers = auth_headers(email="promptuser@example.com", password="pw123456")
    prompt = "やること 2026/08/15 09:00 東京都渋谷区 通知あり"

    res = client.post("/prompt_ctl/prompt_analyze", params={"prompt": prompt}, headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert data["plan_name"] == "やること"
    assert data["date"]["start_date"] == "2026-08-15"
    assert data["time"]["start_time"] == "09:00:00"
    assert data["alarm"] is True
    assert data["location"] == "東京都渋谷区"


def test_prompt_analyze_requires_authentication(client):
    res = client.post("/prompt_ctl/prompt_analyze", params={"prompt": "テスト"})
    assert res.status_code in (401, 403)


def test_prompt_analyze_falls_back_when_no_plan_name_found(client, auth_headers):
    headers = auth_headers(email="promptuser2@example.com", password="pw123456")

    res = client.post("/prompt_ctl/prompt_analyze", params={"prompt": "19:00 20:00 毎日"}, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["plan_name"] == "無題の予定"


def test_prompt_analyze_extracts_tags_and_url(client, auth_headers):
    headers = auth_headers(email="promptuser3@example.com", password="pw123456")
    prompt = "出張 2026/09/01 2026/09/03 10:00 18:00 毎週 #仕事 #大阪 https://example.com/doc"

    res = client.post("/prompt_ctl/prompt_analyze", params={"prompt": prompt}, headers=headers)
    assert res.status_code == 200, res.text

    data = res.json()
    assert set(data["tags"]) == {"#仕事", "#大阪"}
    assert data["url"] == "https://example.com/doc"
    assert data["repeats"] == "毎週"
    assert data["date"] == {"start_date": "2026-09-01", "finish_date": "2026-09-03"}
