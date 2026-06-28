import requests

FASTAPI_URL = "http://127.0.0.1:8000/send-to-gas"

def main():
    print("=== GAS TEST CLI ===")

    start = input("出発地: ")
    end = input("目的地: ")
    time = input("始業時間 (例 09:00): ")

    payload = {
        "start": start,
        "end": end,
        "time": time
    }
    

    print("\n送信中...\n")

    res = requests.post(FASTAPI_URL, json=payload)

    try:
        data = res.json()
    except Exception:
        print("レスポンス解析失敗")
        print(res.text)
        return

    print("=== RESULT ===")
    print(data)


if __name__ == "__main__":
    main()
