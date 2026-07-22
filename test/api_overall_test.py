# API Overall Test
import requests
import json
import pytest

ENDPOINT = "http://localhost:8000/"

@pytest.mark.api
def main():
    pass

@pytest.mark.api
def code_check():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200

@pytest.mark.api
def auth_check():
    response = requests.get(f"{ENDPOINT}/auth/")
    assert response.status_code == 200

@pytest.mark.api
def add_schedule():
    dataset = [
        "やること 2026/08/15 09:00 東京都渋谷区宇田川町XX-YY-ZZ アラーム付き 今日は私の誕生日です",
        "出張 2026/09/01 2026/09/03 10:00 18:00 毎週 #仕事 #大阪 大阪府大阪市北区 議事録を忘れずに",
        "ジム 19:00 20:00 毎日 #健康 軽めのメニューで",
        "買い物 2026/08/20",
    ]
    for prompt in dataset:
        result = requests.get(f"{ENDPOINT}/prompt_ctl/prompt_analyze", params={"prompt": prompt, "user_id": 1, "client": ""})
        assert result.status_code == 200

@pytest.mark.api
def integration_test():
