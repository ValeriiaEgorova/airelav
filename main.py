import io
import os
import secrets
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import redis.asyncio as redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi_sso.sso.github import GithubSSO
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, col, desc, select

from auth import (
    create_access_token,
    get_current_user,
    get_current_user_or_api_key,
    get_password_hash,
    verify_password,
)
from core import generate_and_run
from database import create_db_and_tables, engine, get_session
from models import (
    APIKey,
    Conversation,
    EnhancePromptRequest,
    GenerateRequest,
    GenerationTask,
    User,
)

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    pass

github_sso = GithubSSO(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/auth/github/callback",
)


app = FastAPI(title="AIrelav API")

scheduler = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_user_tier_limit(
    current_user: User = Depends(get_current_user_or_api_key),
) -> tuple[int, int]:
    """
    Возвращает (количество_запросов, секунд).
    Например: (5, 60) = 5 запросов в минуту.
    """
    if current_user.tier == "pro":
        return 50, 60  # Pro: 50 запросов в минуту
    elif current_user.tier == "enterprise":
        return 1000, 60  # Enterprise: почти безлимит
    else:
        return 10, 60  # Free: 10 запросов в минуту


@app.on_event("startup")
async def on_startup() -> None:
    create_db_and_tables()

    redis_connection = redis.from_url(
        "redis://localhost:6379", encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(redis_connection)
    scheduler.add_job(
        cleanup_expired_files,
        trigger=IntervalTrigger(hours=12),
        id="gc_job",
        name="Cleanup expired generated files",
        replace_existing=True,
    )
    scheduler.start()


@app.post("/auth/register")
def register(
    email: str, password: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=email, hashed_password=get_password_hash(password))
    session.add(new_user)
    session.commit()
    return {"message": "User created successfully"}


@app.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/conversations")
async def get_conversations(
    offset: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    return session.exec(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .where(not Conversation.is_deleted)
        .order_by(desc(Conversation.created_at))
        .offset(offset)
        .limit(limit)
    ).all()


@app.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Any:
    chat = session.get(Conversation, conversation_id)
    if not chat or chat.user_id != current_user.id or chat.is_deleted:
        raise HTTPException(status_code=404, detail="Chat not found")

    tasks = session.exec(
        select(GenerationTask)
        .where(GenerationTask.conversation_id == conversation_id)
        .where(not GenerationTask.is_deleted)
        .order_by(desc(GenerationTask.created_at))
    ).all()
    return tasks


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    chat = session.get(Conversation, conversation_id)
    if not chat or chat.user_id != current_user.id or chat.is_deleted:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat.is_deleted = True
    session.add(chat)

    tasks = session.exec(
        select(GenerationTask).where(GenerationTask.conversation_id == conversation_id)
    ).all()

    for task in tasks:
        task.is_deleted = True
        session.add(task)

        if task.file_path and os.path.exists(task.file_path):
            try:
                os.remove(task.file_path)
            except OSError:
                pass

    session.commit()
    return {"message": "Conversation deleted successfully"}


@app.post("/generate", dependencies=[Depends(RateLimiter(times=20, seconds=60))])
async def start_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_or_api_key),
    session: Session = Depends(get_session),
) -> dict[str, Any]:

    if current_user.tier == "free":
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        count: int = session.exec(
            select(func.count())
            .select_from(GenerationTask)
            .where(GenerationTask.user_id == current_user.id)
            .where(GenerationTask.created_at > one_day_ago)
        ).one()

        if count >= 10:
            raise HTTPException(
                status_code=429,
                detail="Лимит тарифа Free исчерпан (10 генераций в сутки).",
            )

    active_task = session.exec(
        select(GenerationTask)
        .where(GenerationTask.user_id == current_user.id)
        .where(
            col(GenerationTask.status).in_(["pending", "processing"])
        )  # Добавили col()
    ).first()

    if active_task:
        raise HTTPException(
            status_code=429,  # 429 Too Many Requests
            detail="У вас уже выполняется генерация данных. Дождитесь её завершения перед отправкой нового запроса.",
        )

    previous_code = None

    prompt = request.prompt
    model = request.model
    conversation_id = request.conversation_id

    if not conversation_id:
        title = prompt[:40] + "..." if len(prompt) > 40 else prompt
        new_chat = Conversation(title=title, user_id=current_user.id)
        session.add(new_chat)
        session.commit()
        session.refresh(new_chat)
        conversation_id = new_chat.id
    else:
        chat = session.get(Conversation, conversation_id)
        if not chat or chat.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")

        last_task = session.exec(
            select(GenerationTask)
            .where(GenerationTask.conversation_id == conversation_id)
            .where(GenerationTask.status == "completed")
            .order_by(desc(GenerationTask.created_at))
        ).first()

        if last_task:
            previous_code = last_task.generated_code

    expiration_days = 1 if current_user.tier == "free" else 7
    expires_time = datetime.utcnow() + timedelta(days=expiration_days)

    task = GenerationTask(
        prompt=prompt,
        file_format="csv",
        user_id=current_user.id,
        conversation_id=conversation_id,
        expires_at=expires_time,
        ai_model=model,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    if task.id is None:
        raise HTTPException(status_code=500, detail="Database error: Task ID missing")

    background_tasks.add_task(run_generation_wrapper, task.id, previous_code, model)

    return {
        "task_id": task.id,
        "conversation_id": conversation_id,
        "message": "Генерация запущена",
    }


@app.get("/api-keys")
def get_api_keys(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    return user.api_keys


@app.post("/api-keys")
def create_api_key(
    name: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if len(user.api_keys) >= 10:
        raise HTTPException(
            status_code=400,
            detail="Вы достигли лимита в 10 активных API ключей. Удалите старые, чтобы создать новый.",
        )
    random_part = secrets.token_urlsafe(16)
    new_key_str = f"sk-relav-{random_part}"

    key_obj = APIKey(name=name, key=new_key_str, user_id=user.id)
    session.add(key_obj)
    session.commit()
    session.refresh(key_obj)
    return key_obj


@app.delete("/api-keys/{key_id}")
def delete_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    key = session.get(APIKey, key_id)
    if not key or key.user_id != user.id:
        raise HTTPException(status_code=404, detail="Key not found")

    session.delete(key)
    session.commit()
    return {"message": "Key deleted"}


# @app.get("/history")
# async def get_history(
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session),
# ) -> Any:
#     tasks = session.exec(
#         select(GenerationTask)
#         .where(GenerationTask.user_id == current_user.id)
#         .order_by(desc(GenerationTask.created_at))
#     ).all()
#     return tasks


@app.get("/download/{task_id}")
async def download_file(
    task_id: int,
    format: str = "csv",
    current_user: User = Depends(get_current_user_or_api_key),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    task = session.get(GenerationTask, task_id)

    if not task or not task.file_path or not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="Файл данных не найден")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому файлу")

    try:
        df = pd.read_csv(task.file_path)

        stream = io.BytesIO()

        if format == "csv":
            df.to_csv(stream, index=False, encoding="utf-8-sig")
            media_type = "text/csv"
            filename = f"dataset_{task_id}.csv"
        elif format == "json":
            df.to_json(stream, orient="records", force_ascii=False, indent=4)
            media_type = "application/json"
            filename = f"dataset_{task_id}.json"
        elif format == "xlsx":
            df.to_excel(stream, index=False, engine="openpyxl")
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"dataset_{task_id}.xlsx"
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported format: use csv, json, or xlsx"
            )

        stream.seek(0)
        return StreamingResponse(
            stream,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        print(f"Ошибка при конвертации для скачивания: {e}")
        # Правильный вариант:
        raise HTTPException(
            status_code=404, detail="Файл данных не найден или поврежден"
        ) from e


def run_generation_wrapper(
    task_id: int, previous_code: str | None = None, model_name: str = "gemini-2.5-flash"
) -> None:
    with Session(engine) as session:
        task = session.get(GenerationTask, task_id)
        if not task:
            return

        task_local: GenerationTask = task

        def update_progress(msg: str, percent: int) -> None:
            task_local.status_message = msg
            task_local.progress = percent
            session.add(task_local)
            session.commit()

        try:
            task.status = "processing"
            session.add(task)
            session.commit()

            result = generate_and_run(
                user_query=task.prompt,
                task_id=task_id,
                previous_code=previous_code,
                on_progress=update_progress,
                model_name=model_name,
            )

            if result["status"] == "success":
                task.status = "completed"
                task.file_path = result["file"]
                task.generated_code = result["code"]
                task.preview_data = result.get("preview")
                task.file_size = result.get("file_size")
                task.row_count = result.get("row_count")
                task.progress = 100
            else:
                task.status = "failed"
                task.error_log = result["message"]

            session.add(task)
            session.commit()

        except Exception as e:
            session.rollback()
            task = session.get(GenerationTask, task_id)
            if task:
                task.status = "failed"
                task.error_log = f"Critical Error: {str(e)}"
                session.add(task)
                session.commit()


@app.get("/tasks/{task_id}")
def get_task_status(
    task_id: int,
    current_user: User = Depends(get_current_user_or_api_key),
    session: Session = Depends(get_session),
) -> Any:
    """Проверка статуса конкретной задачи"""
    task = session.get(GenerationTask, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")

    return {
        "id": task.id,
        "status": task.status,
        "progress": task.progress,
        "status_message": task.status_message,
        "preview_data": task.preview_data,  # Важно для превью!
        "error_log": task.error_log,
        "file_size": task.file_size,
        "row_count": task.row_count,
    }


@app.post("/enhance-prompt", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def enhance_prompt(
    request: EnhancePromptRequest,
    current_user: User = Depends(get_current_user_or_api_key),
) -> dict[str, str]:

    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is empty")

    system_instruction = """
    Ты — Data Engineer. Твоя задача: улучшить короткий запрос пользователя для генератора синтетических данных.
    ПРАВИЛА:
    1. Сделай запрос более профессиональным: добавь нужные колонки, распределения (например, нормальное) или логические связи (например, "зарплата зависит от должности").
    2. КРАТКОСТЬ: Твой ответ должен быть ОЧЕНЬ лаконичным (максимум 2-3 предложения).
    3. ЛИМИТ СИМВОЛОВ: Строго уложись в 800 символов.
    4. Ответь ТОЛЬКО улучшенным текстом, без приветствий, без пояснений, без кавычек.
    5. Сохраняй язык оригинала (русский или английский).
    Пример:
    Оригинал: "сделай базу сотрудников"
    Улучшение: "Сгенерируй датасет из 500 сотрудников: ФИО, email (5% ошибок), должность, зарплата (зависит от должности) и дата найма (2020-2024)."
    """

    try:
        from core import DEFAULT_MODEL, client

        resp = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=f"{system_instruction}\n\nОРИГИНАЛЬНЫЙ ЗАПРОС:\n{request.prompt}",
        )

        enhanced_text = resp.text.strip() if resp.text else request.prompt

        if len(enhanced_text) > 990:
            enhanced_text = enhanced_text[:990] + "..."

        return {"enhanced_prompt": enhanced_text}

    except Exception as e:
        print(f"Enhance error: {e}")
        return {"enhanced_prompt": request.prompt}


def cleanup_expired_files():
    """Фоновая задача: удаляет физические файлы, чей срок жизни истек."""
    print(f"[{datetime.utcnow()}] Запуск Garbage Collector...")
    with Session(engine) as session:
        now = datetime.utcnow()
        expired_tasks = session.exec(
            select(GenerationTask)
            .where(GenerationTask.expires_at < now)
            .where(GenerationTask.file_path is not None)
        ).all()

        count = 0
        for task in expired_tasks:
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                    task.file_path = None
                    task.error_log = "Файл удален по истечении срока хранения (TTL)."
                    session.add(task)
                    count += 1
                except OSError as e:
                    print(f"GC Error: Не удалось удалить файл {task.file_path}: {e}")

        session.commit()
        if count > 0:
            print(f"Garbage Collector: Удалено {count} просроченных файлов.")


@app.get("/auth/me")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    total_tasks = session.exec(
        select(func.count())  # Убрали GenerationTask.id, так проще и MyPy доволен
        .select_from(GenerationTask)  # Явно указываем таблицу
        .where(GenerationTask.user_id == current_user.id)
        .where(GenerationTask.status == "completed")
    ).one()

    total_rows = (
        session.exec(
            select(func.sum(GenerationTask.row_count)).where(
                GenerationTask.user_id == current_user.id
            )
        ).one()
        or 0
    )

    return {
        "id": current_user.id,
        "email": current_user.email,
        "tier": current_user.tier,
        "stats": {
            "total_datasets": total_tasks,
            "total_rows": total_rows,
            "active_keys": len(current_user.api_keys),
        },
    }


@app.get("/auth/github/callback")
async def github_callback(request: Request, session: Session = Depends(get_session)):
    async with github_sso:  # <--- И ТУТ ASYNC
        user_data = await github_sso.verify_and_process(request)

    if not user_data:
        raise HTTPException(
            status_code=400, detail="Failed to get user data from GitHub"
        )

    user = session.exec(select(User).where(User.email == user_data.email)).first()

    if not user:
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            tier="free",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

    access_token = create_access_token(data={"sub": user.email})
    frontend_url = "http://localhost:5173/auth-success"
    return RedirectResponse(url=f"{frontend_url}?token={access_token}")


@app.get("/auth/github/login")
async def github_login():
    async with github_sso:  # <--- ТУТ ASYNC
        return await github_sso.get_login_redirect()


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@app.post("/auth/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest, session: Session = Depends(get_session)
):
    from auth import create_password_reset_token  # Импорт прямо перед использованием

    user = session.exec(select(User).where(User.email == request.email)).first()

    # Для безопасности мы не говорим, найден ли email, просто возвращаем ОК
    if not user:
        return {
            "message": "If this email is registered, you will receive a reset link."
        }

    reset_token = create_password_reset_token(email=user.email)

    # Эмуляция отправки письма (ссылка будет в консоли)
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

    return {
        "message": "If this email is registered, you will receive a reset link.",
        "demo_link": reset_link,
    }


@app.post("/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest, session: Session = Depends(get_session)
):
    from auth import get_password_hash, verify_password_reset_token  # Импорты

    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем пароль в БД
    user.hashed_password = get_password_hash(request.new_password)
    session.add(user)
    session.commit()

    return {"message": "Password updated successfully"}


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
