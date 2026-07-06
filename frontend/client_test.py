import requests

FASTAPI_URL = "http://127.0.0.1:8000/schedule"

def main():
    print("=== Schedule TEST CLI ===")

    start = input("出発地: ")
    end = input("目的地: ")
    date = input("日付 (例 2026-07-06): ")
    time = input("始業時間 (例 09:00): ")

    payload = {
        "start": start,
        "end": end,
        "date": date,
        "time": time
    }

    print("\n送信中...\n")

    try:
        res = requests.post(FASTAPI_URL, json=payload)
        res.raise_for_status()

        data = res.json()

        print("=== RESULT ===")
        print(data)

    except requests.exceptions.RequestException as e:
        print("通信エラー")
        print(e)

    except ValueError:
        print("JSON解析失敗")
        print(res.text)

if __name__ == "__main__":
    main()