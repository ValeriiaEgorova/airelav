import sys
import time

import requests

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "sk-relav-RRxSscBKk1D2_7T6rorVFw"  # <--- ВАШ КЛЮЧ ЗДЕСЬ

headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def main():
    print("🚀 Запуск генерации через AIrelav API...")

    payload = {
        "prompt": "Сгенерируй список из 100 транзакций (ID, Сумма, Валюта, Дата). Валюта USD или EUR.",
        "model": "gemini-2.5-flash",
    }

    try:
        resp = requests.post(f"{BASE_URL}/generate", json=payload, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        print(resp.text)
        return

    data = resp.json()
    task_id = data["task_id"]
    print(f"✅ Задача принята! ID: {task_id}")

    while True:
        status_resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        task_info = status_resp.json()

        status = task_info["status"]
        progress = task_info["progress"]
        msg = task_info["status_message"]

        sys.stdout.write(f"\r⏳ Статус: {status} [{progress}%] - {msg}   ")
        sys.stdout.flush()

        if status == "completed":
            print("\n🎉 Генерация завершена!")
            break
        elif status == "failed":
            print(f"\n❌ Ошибка генерации: {task_info['error_log']}")
            return

        time.sleep(1.5)

    print("⬇️ Скачивание файла...")

    download_format = "csv"
    file_resp = requests.get(
        f"{BASE_URL}/download/{task_id}",
        params={"format": download_format},
        headers=headers,
    )

    if file_resp.status_code == 200:
        filename = f"dataset_{task_id}.{download_format}"
        with open(filename, "wb") as f:
            f.write(file_resp.content)
        print(f"💾 Файл сохранен как: {filename}")
    else:
        print("❌ Ошибка скачивания")


if __name__ == "__main__":
    main()
