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

def generate_and_run(user_query: str, file_format: str, task_id: int, on_progress=None):
    
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
        
        # 1. Генерация (или исправление) кода
        if current_attempt == 1:
            log("Генерация кода через Gemini...", 30)
            code, ext = get_generation_code(user_query, file_format, task_id)
        else:
            log(f"Попытка самоисправления {current_attempt-1}/{max_retries-1}...", 35)
            code, ext = get_fix_from_llm(bad_code, last_error, file_format, task_id)

        if not code:
            return {"status": "error", "message": "Gemini вернула пустой ответ."}

        # 2. Валидация кода
        log("Проверка безопасности и синтаксиса...", 50)
        is_safe, msg = is_code_safe_and_valid(code)
        if not is_safe:
            last_error = msg
            bad_code = code
            log(f"Валидация не пройдена: {msg}", 55)
            continue

        # 3. Запуск в песочнице
        log("Запуск кода в Docker-песочнице...", 70)
        success, error_msg = run_in_sandbox(code, ext, task_id)

        if success:
            final_filename = f"{STORAGE_DIR}/result_{task_id}.{ext}"

            # --- НОВЫЙ БЛОК: ЧИТАЕМ ПРЕВЬЮ ---
            log("Генерация предпросмотра...", 90)
            preview = []
            try:
                if ext == 'csv':
                    df = pd.read_csv(final_filename)
                elif ext == 'xlsx':
                    df = pd.read_excel(final_filename)
                elif ext == 'json':
                    df = pd.read_json(final_filename)
                
                df = df.fillna("")
                preview = df.head(5).to_dict(orient='records')
            except Exception as e:
                print(f"Ошибка создания превью: {e}")

            log("Файл успешно создан и прошел проверку качества.", 100)
            return {
                "status": "success", 
                "file": final_filename, 
                "code": code,
                "format": ext,
                "preview": preview
            }
        else:
            log("Ошибка при исполнении. Попытка анализа...", 80)
            last_error = error_msg
            bad_code = code
            # Цикл продолжится для следующей попытки Self-Healing

    return {
        "status": "error", 
        "message": f"Не удалось создать данные после {max_retries} попыток. Последняя ошибка: {last_error}"
    }

def get_generation_code(prompt, file_format, task_id):
    ext = "xlsx" if file_format == "excel" else file_format
    # Путь сохранения внутри контейнера (относительно /app)
    file_path_docker = f"{STORAGE_DIR}/result_{task_id}.{ext}"

    format_cmds = {
        "csv": f"df.to_csv('{file_path_docker}', index=False, encoding='utf-8-sig')",
        "excel": f"df.to_excel('{file_path_docker}', index=False)",
        "json": f"df.to_json('{file_path_docker}', orient='records', force_ascii=False, indent=4)"
    }
    cmd = format_cmds.get(file_format, format_cmds["csv"])
    
    instr = f"""Напиши Python код (Pandas + Faker) для генерации данных.
    ПРАВИЛА:
    1. Локализация Faker: fake = Faker('ru_RU').
    2. Создай DataFrame 'df'.
    3. Сохрани результат командой: {cmd}
    4. НЕ используй библиотеку os и команду print().
    5. Выдай ТОЛЬКО чистый код без пояснений и разметки."""
    
    try:
        resp = client.models.generate_content(
            model=MODEL_ID, 
            contents=f"{instr}\nЗапрос пользователя: {prompt}"
        )
        code = re.sub(r'```python|```', '', resp.text).strip()
        return code, ext
    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return None, ext

def get_fix_from_llm(bad_code, error_msg, file_format, task_id):
    ext = "xlsx" if file_format == "excel" else file_format
    file_path_docker = f"{STORAGE_DIR}/result_{task_id}.{ext}"
    
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
        return code, ext
    except Exception as e:
        print(f"Ошибка Gemini API при фиксе: {e}")
        return None, ext

def run_in_sandbox(code, ext, task_id):
    script_name = f"temp_script_{task_id}.py"
    output_name_host = os.path.join(STORAGE_DIR, f"result_{task_id}.{ext}")
    
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