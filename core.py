import ast
import os
import re
import subprocess
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
# MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash-lite")
STORAGE_DIR = "storage"
DEFAULT_MODEL = "gemini-2.5-flash"

os.makedirs(STORAGE_DIR, exist_ok=True)


def is_code_safe_and_valid(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"Ошибка синтаксиса: {e}"

    forbidden = [
        "os.",
        "subprocess.",
        "shutil.",
        "requests.",
        "socket.",
        "eval(",
        "exec(",
        "__import__",
    ]
    for cmd in forbidden:
        if cmd in code:
            return False, f"Нарушение безопасности: команда '{cmd}' запрещена."
    return True, "OK"


def generate_and_run(
    user_query: str,
    task_id: int,
    previous_code: str | None = None,
    on_progress: Any = None,
    model_name: str = DEFAULT_MODEL,
) -> dict[str, Any]:

    def log(message: str, percent: int) -> None:
        if on_progress:
            on_progress(message, percent)
        print(f"[{percent}%] {message}")

    max_retries = 3
    current_attempt = 0
    last_error: str | None = None
    bad_code: str | None = None

    log("Анализ запроса и подготовка промпта...", 10)

    while current_attempt < max_retries:
        current_attempt += 1

        if current_attempt == 1:
            if previous_code:
                log("Модификация существующего кода...", 30)
                code = get_modification_code(
                    user_query, previous_code, task_id, model_name
                )
            else:
                log("Генерация кода с нуля...", 30)
                code = get_generation_code(user_query, task_id, model_name)
        else:
            log(
                f"Попытка самоисправления {model_name} {current_attempt-1}/{max_retries-1}...",
                35,
            )
            code = get_fix_from_llm(bad_code, last_error, task_id, model_name)

        if not code:
            return {"status": "error", "message": "Gemini вернула пустой ответ."}

        log("Проверка безопасности и синтаксиса...", 50)
        is_safe, msg = is_code_safe_and_valid(code)
        if not is_safe:
            last_error = msg
            bad_code = code
            log(f"Валидация не пройдена: {msg}", 55)
            continue

        log("Запуск кода в Docker-песочнице...", 70)
        success, error_msg = run_in_sandbox(code, task_id)

        if success:
            final_filename = f"{STORAGE_DIR}/result_{task_id}.pkl"

            log("Генерация предпросмотра...", 90)
            preview = []
            file_size = 0
            row_count = 0
            try:
                df = pd.read_pickle(final_filename)
                row_count = len(df)
                file_size = os.path.getsize(final_filename)
                df = df.fillna("")
                preview = df.head(5).astype(str).to_dict(orient="records")
            except Exception as e:
                print(f"Ошибка превью: {e}")

            log("Данные успешно сгенерированы.", 100)
            return {
                "status": "success",
                "file": final_filename,
                "code": code,
                "preview": preview,
                "file_size": file_size,
                "row_count": row_count,
            }
        else:
            log("Ошибка при исполнении. Попытка анализа...", 80)
            last_error = error_msg
            bad_code = code

    return {
        "status": "error",
        "message": f"Не удалось создать данные после {max_retries} попыток. Последняя ошибка: {last_error}",
    }


def get_generation_code(prompt: str, task_id: int, model_name: str) -> str | None:
    file_path_docker = f"{STORAGE_DIR}/result_{task_id}.pkl"

    cmd = f"df.to_pickle('{file_path_docker}')"

    instr = f"""Напиши Python код (Pandas + Faker) для генерации данных.
    ПРАВИЛА:
    1. Локализация Faker: fake = Faker('ru_RU').
    2. Создай DataFrame 'df'.
    3. Сохрани результат командой: {cmd}
    4. НЕ используй print().
    5. Выдай ТОЛЬКО чистый код."""

    try:
        resp = client.models.generate_content(
            model=model_name, contents=f"{instr}\nЗапрос пользователя: {prompt}"
        )
        text_response = resp.text if resp.text else ""
        code = re.sub(r"```python|```", "", text_response).strip()
        return code
    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return None


def get_fix_from_llm(
    bad_code: str | None, error_msg: str | None, task_id: int, model_name: str
) -> str | None:
    if not bad_code or not error_msg:
        return None

    file_path_docker = f"{STORAGE_DIR}/result_{task_id}.pkl"

    prompt = f"""
    Исправь ошибку в Python коде. НЕ ИСПОЛЬЗУЙ библиотеку os.
    ОШИБКА: {error_msg}
    ИСХОДНЫЙ КОД:
    {bad_code}
    ВАЖНО: Результат должен быть сохранен в: {file_path_docker}
    Выдай только полный исправленный код без пояснений.
    """
    try:
        resp = client.models.generate_content(model=model_name, contents=prompt)
        text_response = resp.text if resp.text else ""
        code = re.sub(r"```python|```", "", text_response).strip()
        return code
    except Exception as e:
        print(f"Ошибка Gemini API при фиксе: {e}")
        return None


def get_modification_code(
    user_changes: str, old_code: str, task_id: int, model_name: str
) -> str | None:

    file_path_docker = f"{STORAGE_DIR}/result_{task_id}.pkl"
    save_cmd = f"df.to_pickle('{file_path_docker}')"

    instr = f"""
    Ты — Python Data Expert. Твоя задача — изменить существующий код генерации данных.
    СТАРЫЙ КОД:
    {old_code}
    ТРЕБОВАНИЯ К ИЗМЕНЕНИЯМ:
    {user_changes}
    ПРАВИЛА:
    1. Используй pandas и faker (ru_RU).
    2. Сохрани итоговый DataFrame 'df' командой: {save_cmd}
    3. НЕ используй print() и библиотеку os.
    4. Верни ПОЛНЫЙ обновленный код, готовый к запуску (не diff, не куски).
    5. Выдай ТОЛЬКО код без Markdown разметки.
    """

    try:
        resp = client.models.generate_content(model=model_name, contents=instr)
        text_response = resp.text if resp.text else ""
        code = re.sub(r"```python|```", "", text_response).strip()
        return code
    except Exception as e:
        print(f"Ошибка Gemini API (Modification): {e}")
        return None


def run_in_sandbox(code: str, task_id: int) -> tuple[bool, str | None]:
    script_name = f"temp_script_{task_id}.py"
    output_name_host = os.path.join(STORAGE_DIR, f"result_{task_id}.pkl")

    with open(script_name, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        res = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{os.getcwd()}:/app",
                "synthgen-env",
                "python",
                f"/app/{script_name}",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
        )

        if res.returncode != 0:
            return False, res.stderr

        if (
            not os.path.exists(output_name_host)
            or os.path.getsize(output_name_host) < 10
        ):
            return False, "Файл не был создан или поврежден."

        return True, None
    except subprocess.TimeoutExpired:
        return False, "Превышено время ожидания исполнения (120 с)."
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
