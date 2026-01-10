import requests
import os

# === НАСТРОЙКИ ===
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "sk-relav-RRxSscBKk1D2_7T6rorVFw"
TASK_ID = 6

headers = {"Authorization": f"Bearer {API_KEY}"}


def download_dataset(task_id, fmt):
    print(f"⬇️ Скачивание задачи {task_id} в формате {fmt.upper()}...")

    try:
        response = requests.get(
            f"{BASE_URL}/download/{task_id}",
            params={"format": fmt},
            headers=headers,
            stream=True,
        )

        if response.status_code == 200:
            filename = f"downloaded_data.{fmt}"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Успешно сохранено: {filename}")
        elif response.status_code == 403:
            print("⛔ Ошибка 403: Это не ваша задача или ключ неверный.")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Ошибка соединения: {e}")


if __name__ == "__main__":
    download_dataset(TASK_ID, "csv")
    download_dataset(TASK_ID, "json")
    download_dataset(TASK_ID, "xlsx")
