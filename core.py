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
        "getattr",
        "setattr",
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
            # ТЕПЕРЬ ИСПОЛЬЗУЕМ CSV
            final_filename = f"{STORAGE_DIR}/result_{task_id}.csv"
            log("Генерация предпросмотра...", 90)

            preview = []
            file_size = 0
            row_count = 0

            try:
                # Читаем CSV (он универсален и не вызывает конфликтов типов)
                df = pd.read_csv(final_filename)
                row_count = len(df)
                file_size = os.path.getsize(final_filename)

                # Создаем чистый превью для JSON
                df_preview = df.head(5).fillna("")
                # Превращаем всё в строки, чтобы JSON точно не сломался
                preview = df_preview.astype(str).to_dict(orient="records")
            except Exception as e:
                print(f"Критическая ошибка при создании превью: {e}")
                preview = [{"error": f"Ошибка данных: {str(e)}"}]

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
        "message": f"Не удалось создать данные. Последняя ошибка: {last_error}",
    }


def get_generation_code(prompt: str, task_id: int, model_name: str) -> str | None:
    docker_path = f"storage/result_{task_id}.csv"

    system_prompt = f"""You are an Expert Data Engineer specializing in generating highly realistic synthetic datasets.
Your task is to write a Python script using `pandas`, `faker`, and `numpy`/`random` to generate data based on the user's request.

[RULES & REQUIREMENTS]
1. LIBRARIES: Import and use `pandas as pd` and `Faker`. You may use `numpy` or `random` for logic, distributions, and injecting anomalies.
2. LOCALE: Initialize Faker with Russian locale by default (`fake = Faker('ru_RU')`), unless the user explicitly requests another language.
3. LOGIC: Pay strict attention to requested correlations, dependencies (e.g., 'if age < 18, driver_license is None'), probabilities, and intentional data errors (nulls, duplicates) if asked.
4. DATAFRAME: The final data must be stored in a Pandas DataFrame named `df`.
5. EXPORT: You MUST save the dataset using exactly this command: df.to_csv('{docker_path}', index=False)

[CONSTRAINTS - CRITICAL]
- DO NOT use the `os` module under any circumstances.
- DO NOT use `print()` statements.
- DO NOT wrap the code in Markdown formatting (no ```python ... ```).
- Output ONLY the raw, executable Python code. No explanations.
"""

    try:
        resp = client.models.generate_content(
            model=model_name, contents=f"{system_prompt}\n\n[USER REQUEST]\n{prompt}"
        )
        text = resp.text if resp.text else ""
        return re.sub(
            r"```[a-zA-Z]*\n|```", "", text
        ).strip()  # Улучшенный regex для очистки
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        return None


def get_fix_from_llm(
    bad_code: str | None, error_msg: str | None, task_id: int, model_name: str
) -> str | None:
    if not bad_code or not error_msg:
        return None
    docker_path = f"storage/result_{task_id}.csv"

    system_prompt = f"""You are a Senior Python Debugger. The previous code generated to create a synthetic dataset failed with an error.
Your task is to analyze the traceback and fix the code.

[ERROR TRACEBACK]
{error_msg}[PREVIOUS BAD CODE]
{bad_code}

[RULES FOR THE FIX]
1. Fix the bug without changing the original intent of the data generation.
2. Do NOT use the `os` module.
3. The final DataFrame `df` MUST be saved using exactly: df.to_csv('{docker_path}', index=False)
4. Output ONLY the raw, executable Python code. No Markdown blocks, no explanations.
"""

    try:
        resp = client.models.generate_content(model=model_name, contents=system_prompt)
        text = resp.text if resp.text else ""
        return re.sub(r"```[a-zA-Z]*\n|```", "", text).strip()
    except Exception as e:
        print(f"LLM Self-Healing Error: {e}")
        return None


def get_modification_code(
    user_changes: str, old_code: str, task_id: int, model_name: str
) -> str | None:
    docker_path = f"storage/result_{task_id}.csv"

    system_prompt = f"""You are an Expert Data Engineer modifying an existing synthetic dataset generation script.
Update the provided Python code strictly according to the user's new requirements.

[OLD CODE]
{old_code}[USER REQUESTED CHANGES]
{user_changes}

[RULES & CONSTRAINTS]
1. Apply the changes logically without breaking the rest of the script.
2. The final DataFrame `df` MUST be saved using exactly: df.to_csv('{docker_path}', index=False)
3. DO NOT use the `os` module.
4. Output ONLY the raw, executable Python code. No Markdown blocks, no explanations.
"""

    try:
        resp = client.models.generate_content(model=model_name, contents=system_prompt)
        text = resp.text if resp.text else ""
        return re.sub(r"```[a-zA-Z]*\n|```", "", text).strip()
    except Exception as e:
        print(f"LLM Modification Error: {e}")
        return None


def run_in_sandbox(code: str, task_id: int) -> tuple[bool, str | None]:
    script_name = f"temp_script_{task_id}.py"
    output_name_host = os.path.join(STORAGE_DIR, f"result_{task_id}.csv")

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
            return False, "Файл CSV не был создан. Возможно, код упал до сохранения."

        return True, None
    except subprocess.TimeoutExpired:
        return False, "Таймаут 120с."
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(script_name):
            try:
                os.remove(script_name)
            except Exception:
                pass
