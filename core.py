import os
import re
import ast
import subprocess
from google import genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash-lite")
STORAGE_DIR = "storage"

os.makedirs(STORAGE_DIR, exist_ok=True)

def is_code_safe_and_valid(code: str):
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"Ошибка синтаксиса: {e}"
    
    forbidden = ['os.', 'subprocess.', 'shutil.', 'requests.', 'socket.', 'eval(', 'exec(', '__import__']
    for cmd in forbidden:
        if cmd in code:
            return False, f"Нарушение безопасности: команда '{cmd}' запрещена."
    return True, "OK"

def generate_and_run(user_query: str, task_id: int, on_progress=None):
    
    def log(message, percent):
        if on_progress:
            on_progress(message, percent)
        print(f"[{percent}%] {message}")

    max_retries = 3
    current_attempt = 0
    last_error = None
    bad_code = None

    log("Анализ запроса и подготовка промпта...", 10)

    while current_attempt < max_retries:
        current_attempt += 1
        
        if current_attempt == 1:
            log("Генерация кода через Gemini...", 30)
            code = get_generation_code(user_query, task_id)
        else:
            log(f"Попытка самоисправления {current_attempt-1}/{max_retries-1}...", 35)
            code = get_fix_from_llm(bad_code, last_error, task_id)

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
            try:
                df = pd.read_pickle(final_filename)
                df = df.fillna("")
                preview = df.head(5).astype(object).to_dict(orient='records')
            except Exception as e:
                print(f"Ошибка превью: {e}")

            log("Данные успешно сгенерированы.", 100)
            return {
                "status": "success", 
                "file": final_filename,
                "code": code,
                "preview": preview
            }
        else:
            log("Ошибка при исполнении. Попытка анализа...", 80)
            last_error = error_msg
            bad_code = code

    return {
        "status": "error", 
        "message": f"Не удалось создать данные после {max_retries} попыток. Последняя ошибка: {last_error}"
    }

def get_generation_code(prompt, task_id):
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
            model=MODEL_ID, 
            contents=f"{instr}\nЗапрос пользователя: {prompt}"
        )
        code = re.sub(r'```python|```', '', resp.text).strip()
        return code
    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return None

def get_fix_from_llm(bad_code, error_msg, task_id):
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
        resp = client.models.generate_content(model=MODEL_ID, contents=prompt)
        code = re.sub(r'```python|```', '', resp.text).strip()
        return code
    except Exception as e:
        print(f"Ошибка Gemini API при фиксе: {e}")
        return None

def run_in_sandbox(code, task_id):
    script_name = f"temp_script_{task_id}.py"
    output_name_host = os.path.join(STORAGE_DIR, f"result_{task_id}.pkl")
    
    with open(script_name, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        res = subprocess.run([
            "docker", "run", "--rm", 
            "-v", f"{os.getcwd()}:/app",
            "synthgen-env", 
            "python", f"/app/{script_name}"
        ], capture_output=True, text=True, encoding="utf-8", timeout=120)

        if res.returncode != 0:
            return False, res.stderr 
        
        if not os.path.exists(output_name_host) or os.path.getsize(output_name_host) < 10:
            return False, f"Файл не был создан или поврежден."
            
        return True, None
    except subprocess.TimeoutExpired:
        return False, "Превышено время ожидания исполнения (120 с)."
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)